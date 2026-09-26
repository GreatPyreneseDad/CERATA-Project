#!/usr/bin/env python3
"""CERATA GitHub Action entry point.

Reads the triggering event, checks who is asking, then runs:
  /cerata hunt <owner/repo>      perception report as a comment
  /cerata consume <owner/repo>   metabolism → branch → pull request
  /cerata help

Local dry run (no pushes, comments printed):
  CERATA_DRY_RUN=1 CERATA_COMMAND="hunt psf/requests" python cerata_action/main.py
"""

import base64
import json
import os
import subprocess
import sys
import tempfile
import traceback
from datetime import datetime, timezone
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from cerata_action import commands, consume, copilot, hunt_runner, llm as llm_mod, report  # noqa: E402
from cerata_action.github_api import GitHub, GitHubError  # noqa: E402
from cerata_action.llm import LLMError, Scripted  # noqa: E402

MARKER = "<!-- cerata -->"


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default) or default


def log(msg: str) -> None:
    print(f"🐚 {msg}", flush=True)


def set_output(key: str, value) -> None:
    path = env("GITHUB_OUTPUT")
    if path:
        with open(path, "a") as f:
            f.write(f"{key}={value}\n")


def summary(md: str) -> None:
    path = env("GITHUB_STEP_SUMMARY")
    if path:
        with open(path, "a") as f:
            f.write(md + "\n")


class Context:
    def __init__(self):
        self.dry_run = env("CERATA_DRY_RUN") == "1"
        self.repo = env("GITHUB_REPOSITORY", "local/dry-run")
        self.workspace = Path(env("GITHUB_WORKSPACE", os.getcwd())).resolve()
        self.home = Path(env("CERATA_HOME", str(HERE.parent))).resolve()
        self.gh = GitHub(env("CERATA_GITHUB_TOKEN") or env("GITHUB_TOKEN"), self.repo, self.dry_run)
        self.event_name = env("GITHUB_EVENT_NAME", "workflow_dispatch")
        self.event = {}
        if env("GITHUB_EVENT_PATH") and Path(env("GITHUB_EVENT_PATH")).is_file():
            self.event = json.loads(Path(env("GITHUB_EVENT_PATH")).read_text())
        self.issue = (self.event.get("issue") or {}).get("number")
        self.comment_id = (self.event.get("comment") or {}).get("id")

    def say(self, body: str) -> None:
        body = f"{MARKER}\n{body}"
        summary(body)
        if self.dry_run or not self.issue:
            print(body)
            return
        self.gh.comment(self.issue, body)

    def react(self, content: str) -> None:
        if self.comment_id and not self.dry_run:
            self.gh.react(self.comment_id, content)


def read_command(ctx: Context):
    explicit = env("CERATA_COMMAND").strip()
    if explicit:
        text = explicit[len("/cerata"):].strip() if explicit.startswith("/cerata") else explicit
        return commands.parse(text), None
    if ctx.event_name != "issue_comment":
        return None, "No command: set the `command` input or trigger from an issue comment."
    comment = ctx.event.get("comment") or {}
    body = comment.get("body", "")
    if MARKER in body or (ctx.event.get("sender") or {}).get("type") == "Bot":
        return None, None  # our own output; stay silent
    text = commands.extract(body)
    if text is None:
        return None, None  # not addressed to CERATA
    allowed = {a.strip().upper() for a in env("CERATA_ALLOWED_ASSOCIATIONS",
                                              "OWNER,MEMBER,COLLABORATOR").split(",")}
    if comment.get("author_association", "NONE").upper() not in allowed:
        return None, (f"@{comment.get('user', {}).get('login', 'someone')}: only "
                      f"{', '.join(sorted(allowed)).lower()} can command CERATA here.")
    return commands.parse(text), None


# ------------------------------------------------------------------- hunt --

def do_hunt(ctx: Context, cmd, workdir: Path):
    prey_dir = workdir / "prey"
    ok, err = hunt_runner.clone(cmd.prey.url, prey_dir)
    if not ok:
        raise RuntimeError(f"Could not clone `{cmd.prey.slug}`: {err[-300:]}")
    hunt_mod = hunt_runner.load_hunt_module(ctx.home)
    info = ctx.gh.repo_info(cmd.prey.slug)
    result = hunt_runner.hunt(hunt_mod, prey_dir, cmd.prey.url, info,
                              env("CERATA_ALLOW_COPYLEFT") == "true")
    set_output("viability", result["viability"]["viability"])
    set_output("coherence", result["coherence"]["coherence"])
    return result, prey_dir


# ---------------------------------------------------------------- consume --

def git(ctx: Context, *args, check=True, **kw):
    r = subprocess.run(["git", "-C", str(ctx.workspace), *args], capture_output=True, text=True, **kw)
    if check and r.returncode != 0:
        raise RuntimeError(f"git {args[0]} failed: {r.stderr.strip()[-400:]}")
    return r.stdout.strip()


def strip_persisted_credentials(ctx: Context) -> None:
    """actions/checkout stores the token in .git/config; model-written tests must not see it."""
    for key in ("http.https://github.com/.extraheader",):
        git(ctx, "config", "--local", "--unset-all", key, check=False)


def api_key() -> str:
    return env("CERATA_API_KEY") or env("CERATA_ANTHROPIC_API_KEY")


def resolve_provider() -> str:
    p = env("CERATA_PROVIDER", "auto").lower()
    if p == "auto" and not api_key() and not env("CERATA_BASE_URL") and env("CERATA_COPILOT_TOKEN"):
        return "copilot"
    return p


def make_llm():
    scripted = env("CERATA_SCRIPTED_LLM")
    if scripted:
        return Scripted(json.loads(Path(scripted).read_text()), model="scripted")
    return llm_mod.make(resolve_provider(), api_key(), env("CERATA_MODEL"), env("CERATA_BASE_URL"),
                        int(env("CERATA_MAX_OUTPUT_TOKENS", "32000")))


def do_consume(ctx: Context, cmd, workdir: Path):
    hunt, prey_dir = do_hunt(ctx, cmd, workdir)
    if not hunt["license"]["consumable"]:
        raise RuntimeError(f"Consumption blocked. {hunt['license']['note']}.")
    if hunt["viability"]["viability"] == "UNFIT_PREY" and not cmd.paths:
        raise RuntimeError("Prey is UNFIT. Name specific files to extract anyway: "
                           f"`/cerata consume {cmd.prey.slug} path/file.py`.")

    base = env("CERATA_BASE_BRANCH") or (git(ctx, "rev-parse", "--abbrev-ref", "HEAD", check=False) or "main")
    if not ctx.dry_run and not env("CERATA_BASE_BRANCH"):
        try:
            base = ctx.gh.default_branch()
        except GitHubError:
            pass

    if resolve_provider() == "copilot" and not env("CERATA_SCRIPTED_LLM"):
        return do_copilot_handoff(ctx, cmd, hunt, prey_dir, base)

    llm = make_llm()
    strip_persisted_credentials(ctx)

    result = consume.metabolize(llm, ctx.workspace, prey_dir, cmd.prey.slug, hunt, cmd.paths,
                                focus=cmd.focus, max_repair=int(env("CERATA_MAX_REPAIR_ROUNDS", "2")),
                                log=log)
    plan = result["plan"]
    if result["declined"]:
        ctx.say(f"### 🐚 CERATA declined `{cmd.prey.slug}`\n\n{plan.get('summary', 'No gap found.')}\n\n"
                + "\n".join(f"- {w}" for w in plan.get("warnings", [])) + f"\n\n{report.SIGNATURE}")
        return None

    extra = consume.attribution(ctx.workspace, prey_dir, cmd.prey.slug, hunt,
                                plan.get("integration_point", ""), result["consumed"])
    written = sorted(set(result["written"]) | set(extra))
    plan["_written"], plan["_model"] = written, f"{getattr(llm, 'provider', '?')}/{llm.model}"

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M")
    branch = f"cerata/consume-{cmd.prey.key.replace('__', '-')}-{stamp}"
    title = plan.get("pr_title") or f"CERATA: consume {cmd.prey.slug}"
    extra = ""
    if result["wired"]:
        how = plan.get("wiring", "")
        extra += ("\n\n### Wiring\n✅ EXPERIMENTAL is reachable. Existing files changed: "
                 + ", ".join(f"`{m}`" for m in result["modified_existing"]) + (f"\n\n{how}" if how else ""))
    else:
        extra += ("\n\n### Wiring\n⚠️ **Not wired.** No existing host code calls the new capability, so no trial "
                 "is running: this PR only adds a library. " + plan.get("unwired_reason", ""))
    if result["unverified"]:
        extra += ("\n\n### Unverified numbers\nThese trial-record figures are not measured by any test in this PR; "
                 "read them as targets:\n" + "\n".join(f"- {u}" for u in result["unverified"]))
    if result["rejected"]:
        extra += ("\n\n> ⛔ Rejected paths (unsafe location, or a license file the model wrote; CERATA copies "
                 "the upstream license itself): " + ", ".join(f"`{r}`" for r in sorted(set(result["rejected"]))))
    if plan.get("warnings"):
        extra += "\n\n### Warnings\n" + "\n".join(f"- {w}" for w in plan["warnings"])
    plan["_extra"] = extra
    body = report.pr_body(cmd.prey.slug, hunt, plan, result["tests"], result["rounds"])

    if ctx.dry_run:
        log(f"[dry-run] would push {branch} with {len(written)} files and open PR: {title}")
        (workdir / "PR_BODY.md").write_text(body)
        set_output("pr-url", "dry-run")
        return {"branch": branch, "written": written, "body": body, "tests": result["tests"]}

    git(ctx, "checkout", "-b", branch)
    git(ctx, "add", "--", *written)
    msg = (f"{title}\n\nConsumed-From: https://github.com/{cmd.prey.slug}@{hunt['commit']}\n"
           f"Nematocysts: {', '.join(n.get('name', '?') for n in plan.get('nematocysts', []))}\n"
           f"Trial-Status: IN_PROGRESS")
    git(ctx, "-c", "user.name=cerata[bot]",
        "-c", "user.email=41898282+github-actions[bot]@users.noreply.github.com",
        "commit", "-m", msg)
    token = env("CERATA_GITHUB_TOKEN") or env("GITHUB_TOKEN")
    header = "AUTHORIZATION: basic " + base64.b64encode(f"x-access-token:{token}".encode()).decode()
    git(ctx, "-c", f"http.https://github.com/.extraheader={header}", "push", "origin", branch)

    try:
        pr = ctx.gh.open_pr(branch, base, title, body)
        url = pr.get("html_url")
    except GitHubError as e:
        url = None
        ctx.say(f"### 🐚 Branch pushed, PR not opened\n\n`{branch}` is ready but GitHub refused the PR ({e.status}).\n"
                f"Enable **Settings → Actions → General → Allow GitHub Actions to create and approve pull requests**, "
                f"or open it yourself: https://github.com/{ctx.repo}/compare/{base}...{branch}\n\n{report.SIGNATURE}")
    if url:
        set_output("pr-url", url)
        t = result["tests"]
        status = "tests ✅" if t.get("passed") else ("tests ⚠️ failing" if t.get("ran") else "no tests run")
        status += " · wired ✅" if result["wired"] else " · ⚠️ not wired (library only)"
        ctx.say(f"### 🐚 Consumed `{cmd.prey.slug}` → {url}\n\n{plan.get('summary', '')}\n\n"
                f"{len(written)} files · {status} · {result['rounds']} round(s)\n\n{report.SIGNATURE}")
    return {"branch": branch, "url": url}


def do_copilot_handoff(ctx: Context, cmd, hunt, prey_dir: Path, base: str):
    token = env("CERATA_COPILOT_TOKEN")
    if not token:
        raise RuntimeError("`provider: copilot` needs `copilot-token`: a PAT with issues + pull requests "
                           "write. The workflow GITHUB_TOKEN cannot assign Copilot.")
    files = consume.select_prey_files(prey_dir, hunt, cmd.paths)
    gh_user = GitHub(token, ctx.repo, ctx.dry_run)
    issue = copilot.handoff(gh_user, ctx.workspace, ctx.repo, base, cmd.prey.slug, hunt, files, cmd.focus)
    if ctx.dry_run:
        print(json.dumps(gh_user.calls[-1][2], indent=2))
    agent = "the `cerata` custom agent" if copilot.agent_profile_present(ctx.workspace) else "Copilot"
    ctx.say(f"### 🐚 Handed to Copilot: {issue.get('html_url')}\n\n{agent} is consuming "
            f"`{cmd.prey.slug}` ({', '.join(f'`{f}`' for f in files)}). Its PR will link back to that issue."
            f"\n\n{report.SIGNATURE}")
    set_output("pr-url", issue.get("html_url", ""))
    return {"issue": issue.get("html_url")}


# ------------------------------------------------------------------- main --

def main() -> int:
    ctx = Context()
    cmd, err = read_command(ctx)
    if cmd is None:
        if err:
            ctx.say(f"⚠️ {err}")
            return 0 if ctx.event_name == "issue_comment" else 1
        log("nothing addressed to CERATA; exiting")
        return 0

    set_output("command", cmd.verb)
    if cmd.error:
        ctx.say(f"⚠️ {cmd.error}\n\n{report.HELP}")
        return 0
    if cmd.verb == "help":
        ctx.say(report.HELP)
        return 0

    ctx.react("eyes")
    with tempfile.TemporaryDirectory(prefix="cerata-") as tmp:
        workdir = Path(tmp)
        try:
            if cmd.verb == "hunt":
                result, _ = do_hunt(ctx, cmd, workdir)
                ctx.say(report.hunt_markdown(cmd.prey.slug, result))
                if ctx.issue and not ctx.dry_run:
                    ctx.gh.add_labels(ctx.issue, ["cerata:hunt"])
            else:
                out = do_consume(ctx, cmd, workdir)
                if ctx.dry_run and out and out.get("body"):
                    print(out["body"])
            ctx.react("rocket")
            return 0
        except (RuntimeError, LLMError, consume.ConsumeError, GitHubError) as e:
            ctx.react("confused")
            ctx.say(f"### 🐚 CERATA `{cmd.verb}` failed\n\n{e}\n\n{report.SIGNATURE}")
            return 1
        except Exception:
            ctx.react("confused")
            tb = traceback.format_exc()
            print(tb, file=sys.stderr)
            ctx.say(f"### 🐚 CERATA crashed\n\n```\n{tb[-1500:]}\n```\n\n{report.SIGNATURE}")
            return 1


if __name__ == "__main__":
    sys.exit(main())
