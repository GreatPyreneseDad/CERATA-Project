"""The overseer: drive one goal until its acceptance test passes on main, or until it stops making progress.

    python -m cerata_action oversee --repo <clone url> --goal goals/forge/goal.json

A goal is a JSON file in the target repo: {name, title, acceptance, checks, scope, stall_rounds}. Its acceptance
command prints `PASS <n> ...` / `FAIL <n> ...: why` lines and exits 0 when every check passes. The overseer never
builds anything. Each tick it:

  1. runs the acceptance command on a fresh clone of main;
  2. green → state `done`, posts the result, stops for good;
  3. a proposal it filed is still being laid out, or a bounty for this repo is open and still alive → waits;
  4. otherwise (red, nothing alive) → files the next proposal from what still fails, signed by its own pair,
     unless `stall_rounds` proposals in a row added no passing check, or the round cap is reached → `stalled`.

It speaks once per state change, as a comment on the goal's tracking PR, and logs every tick. The panel still
decomposes every proposal and the judges still decide every merge; the overseer only notices what is missing.
"""

import base64
import json
import os
import re
import shutil
import subprocess
import tempfile
import time
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple

PICKS = os.environ.get("TATEMAE_PICKS", "https://nnnlitdzggyyboyqismx.supabase.co/functions/v1/picks")
CLI = os.environ.get("TATEMAE_CLI", str(Path.home() / "tatemae" / "cli" / "tatemae.js"))
STATE = Path(os.environ.get("OVERSEER_STATE", str(Path.home() / ".overseer" / "state.json")))
CERATA_STATE = Path(os.environ.get("CERATA_HOME_STATE", str(Path.home() / ".cerata"))) / "built.json"
MAX_ROUNDS = int(os.environ.get("OVERSEER_MAX_ROUNDS", "12"))
DEAD = ("declined", "repro_fails", "suite_red")


def log(msg: str) -> None:
    print(f"overseer: {msg}", flush=True)


def get_json(url: str):
    with urllib.request.urlopen(url, timeout=60) as r:
        return json.loads(r.read())


def gh(token: str, method: str, path: str, body: Optional[Dict] = None):
    req = urllib.request.Request(f"https://api.github.com{path}", method=method,
                                 data=json.dumps(body).encode() if body is not None else None,
                                 headers={"authorization": f"Bearer {token}", "accept": "application/vnd.github+json",
                                          "user-agent": "buildup-overseer", "content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=60) as r:
        return json.loads(r.read() or b"{}")


def auth_args(token: str) -> List[str]:
    h = base64.b64encode(f"x-access-token:{token}".encode()).decode()
    return ["-c", f"http.https://github.com/.extraheader=AUTHORIZATION: basic {h}"]


def slug(url: str) -> str:
    m = re.match(r"https?://github\.com/([^/]+/[^/.]+)", url)
    if not m:
        raise SystemExit(f"overseer drives GitHub repos for now: {url}")
    return m.group(1)


def key(url: str) -> str:
    return re.sub(r"(\.git)?/*$", "", url.strip().lower())


# ------------------------------------------------------------------ state --

def load_state(goal_name: str) -> Dict:
    try:
        s = json.loads(STATE.read_text())
    except (OSError, json.JSONDecodeError):
        s = {}
    s.setdefault(goal_name, {"state": "new", "round": 0, "best": -1, "stall": 0, "proposals": [], "said": "", "progress_at": time.time()})
    return s


def save_state(s: Dict) -> None:
    STATE.parent.mkdir(parents=True, exist_ok=True)
    STATE.write_text(json.dumps(s, indent=1))


# -------------------------------------------------------------- measuring --

def run_acceptance(host: Path, cmd: str, timeout: int = 900) -> Tuple[bool, Dict[int, str], str]:
    try:
        r = subprocess.run(["bash", "-lc", cmd], cwd=host, capture_output=True, text=True, timeout=timeout)
        out, ok = r.stdout + r.stderr, r.returncode == 0
    except subprocess.TimeoutExpired:
        return False, {}, f"(acceptance timed out after {timeout}s)"
    checks = {}
    for line in out.splitlines():
        m = re.match(r"^(PASS|FAIL) (\d+) (.*)$", line)
        if m:
            checks[int(m.group(2))] = f"{m.group(1)} {m.group(3)}"
    return ok, checks, out


def alive_work(repo_url: str, goal: Dict, st: Dict) -> Tuple[List[str], List[str]]:
    """(alive, dead) open bounties on this repo. Dead = CERATA tried under the current harness and gave up."""
    rows = get_json(f"{PICKS}?json")
    try:
        built = json.loads(CERATA_STATE.read_text()).get("built", {})
    except (OSError, json.JSONDecodeError):
        built = {}
    alive, dead = [], []
    for r in rows:
        if r.get("judged") or key(r["f"]["location"]["repo"]) != key(repo_url):
            continue
        if r.get("verified") == "green":
            continue
        title = (r.get("bounty") or {}).get("title") or r["f"]["defect"][:60]
        prior = built.get(r["id"], {})
        if prior.get("status") in DEAD or (prior.get("retried") and time.time() - prior.get("at", 0) > 7200):
            dead.append(f"{title}: {prior['status']}" + (f" ({prior.get('error', '')[:120]})" if prior.get("error") else ""))
        else:
            alive.append(title)
    return alive, dead


def proposals_settling(st: Dict) -> bool:
    """A proposal this overseer filed that the panel has not laid out yet."""
    if not st["proposals"]:
        return False
    mine = {p["id"]: p for p in get_json(f"{PICKS}?proposals") if p["id"] in st["proposals"]}
    return any(p.get("status") in ("filed", "accepted") and not p.get("bounties") for p in mine.values())


# ---------------------------------------------------------------- filing --

def propose(token: str, repo_url: str, goal: Dict, host: Path, st: Dict, checks: Dict[int, str], out: str, dead: List[str],
            keys_home: str, dry: bool) -> Optional[str]:
    n = st["round"] + 1
    failing = [f"- check {k}: {v[5:]}" for k, v in sorted(checks.items()) if v.startswith("FAIL")]
    passing = [f"- check {k}: {v[5:]}" for k, v in sorted(checks.items()) if v.startswith("PASS")]
    tree = subprocess.run(["bash", "-c", " ".join(["git", "ls-files", "--"] + goal.get("scope", []))], cwd=host,
                          capture_output=True, text=True).stdout.strip() or "(nothing yet)"
    title = f"{goal['title']}: round {n}"
    doc = f"""# {title}

Filed by the overseer. The goal's acceptance test (`{goal['acceptance']}`) still fails on main
at `{st.get('head', '')[:12]}`. This proposal is what is missing; the panel lays it out as bounties.
Builders work under {', '.join(f'`{s}`' for s in goal.get('scope', []))}; the contract itself does not change.

## Still failing ({len(failing)} of {goal.get('checks', len(checks))})
{chr(10).join(failing) or '- (the run produced no check lines; see the output below)'}

## Already passing
{chr(10).join(passing) or '- none'}

## Earlier attempts that gave up
{chr(10).join(f'- {d}' for d in dead) or '- none'}

## Files in scope today
```
{tree[:3000]}
```

## Acceptance output (tail)
```
{out[-5000:]}
```

Each bounty's acceptance command should be `{goal['acceptance']} --only <n>` for the checks it covers, joined with
`&&`. Prefer pieces small enough that one failing check is one bounty. Do not repeat a piece that already merged.
"""
    branch = f"proposal/{goal['name']}-r{n}"
    path = f"proposals/{goal['name']}-r{n}.md"
    if dry:
        log(f"[dry] would file {title}\n{doc[:1500]}")
        return None
    subprocess.run(["git", "-C", str(host), "checkout", "-q", "-B", branch], check=True)
    (host / path).parent.mkdir(parents=True, exist_ok=True)
    (host / path).write_text(doc)
    subprocess.run(["git", "-C", str(host), "add", path], check=True)
    msg = f"proposal: {title}\n\nFiled by the overseer from the failing acceptance checks.\n\nBuildup-Proposal: yes\n"
    subprocess.run(["git", "-C", str(host), "-c", "user.name=buildup overseer", "-c", "user.email=overseer@buildup.network",
                    "commit", "-q", "-F", "-"], input=msg, text=True, check=True)
    subprocess.run(["git"] + auth_args(token) + ["-C", str(host), "push", "-q", "-f", "origin", f"HEAD:refs/heads/{branch}"], check=True,
                   capture_output=True)
    base = subprocess.run(["git", "-C", str(host), "rev-parse", "origin/HEAD"], capture_output=True, text=True).stdout.strip()
    s = slug(repo_url)
    try:
        pr = gh(token, "POST", f"/repos/{s}/pulls", {"title": f"proposal: {title}", "head": branch, "base": "main",
                                                     "body": "Reference only; never merges. Filed by the overseer from the goal's failing acceptance checks."})
    except urllib.error.HTTPError as e:
        if e.code != 422:
            raise
        pr = (gh(token, "GET", f"/repos/{s}/pulls?state=open&head={s.split('/')[0]}:{branch}") or [{}])[0]
    desc = f"Round {n} toward: {goal['title']}. {len(failing)} acceptance checks still fail; details in {path}."
    js = ("import { signJws, post } from " + json.dumps(CLI) + "; import { readFileSync } from 'node:fs'; import { randomBytes } from 'node:crypto';"
          "const k = JSON.parse(readFileSync(process.env.TATEMAE_HOME + '/keys.json', 'utf8')); const now = Math.floor(Date.now()/1000);"
          "const a = JSON.parse(process.argv[1]);"
          "const t = signJws({ privateJwk: k.privateJwk, header: { typ: 'buildup-proposal+jwt' }, claims: { ...a, sub: k.pair_id, iat: now, exp: now + 600, jti: randomBytes(8).toString('hex') } });"
          "console.log(JSON.stringify(await post({ type: 'proposal_filed', proposal_token: t })));")
    args = json.dumps({"repo_url": repo_url, "title": title, "description": desc, "pr_url": pr.get("html_url"), "base_commit": base})
    r = subprocess.run(["node", "--input-type=module", "-e", js, args], capture_output=True, text=True,
                       env={**os.environ, "TATEMAE_HOME": keys_home})
    if r.returncode != 0:
        raise RuntimeError(f"proposal_filed failed: {(r.stderr or r.stdout)[-300:]}")
    pid = json.loads(r.stdout.strip().splitlines()[-1]).get("proposal_event_id")
    log(f"filed round {n}: {pr.get('html_url')} → proposal {pid}")
    return pid


def say(token: str, repo_url: str, pr_number: Optional[int], st: Dict, text: str) -> None:
    """One comment per state change on the goal's tracking PR. Silence otherwise."""
    if not pr_number or st.get("said") == text:
        return
    try:
        gh(token, "POST", f"/repos/{slug(repo_url)}/issues/{pr_number}/comments", {"body": f"**overseer**\n\n{text}"})
        st["said"] = text
    except Exception as e:
        log(f"comment failed: {e}")


# ------------------------------------------------------------------ tick --

def tick(repo_url: str, goal_path: str, token: str, keys_home: str, track_pr: Optional[int], dry: bool = False) -> str:
    work = Path(tempfile.mkdtemp(prefix="overseer-"))
    try:
        host = work / "host"
        r = subprocess.run(["git"] + auth_args(token) + ["clone", "-q", "--depth", "50", repo_url, str(host)], capture_output=True, text=True)
        if r.returncode != 0:
            raise RuntimeError(f"clone: {r.stderr[-300:]}")
        goal = json.loads((host / goal_path).read_text())
        allst = load_state(goal["name"]); st = allst[goal["name"]]
        if st["state"] in ("done", "stalled"):
            log(f"{goal['name']}: {st['state']} since round {st['round']}; nothing to do")
            return st["state"]
        st["head"] = subprocess.run(["git", "-C", str(host), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
        ok, checks, out = run_acceptance(host, goal["acceptance"])
        passes = sum(1 for v in checks.values() if v.startswith("PASS"))
        total = goal.get("checks", len(checks))
        log(f"{goal['name']} @ {st['head'][:7]}: {passes}/{total} passing" + (" — DONE" if ok else ""))
        if passes > st.get("passes", -1):
            st["progress_at"] = time.time()
        st["passes"] = passes
        quiet_h = (time.time() - st.get("progress_at", time.time())) / 3600
        if not ok and quiet_h > float(os.environ.get("OVERSEER_QUIET_HOURS", "12")):
            st["state"] = "stalled"
            say(token, repo_url, track_pr, st, f"**Stopped: no new passing check in {quiet_h:.0f} hours** (round {st['round']}, {passes}/{goal.get('checks', len(checks))} on main). Something upstream of the overseer is stuck; see the CERATA and judge logs.")
            save_state(allst); return "stalled"
        if ok:
            st["state"] = "done"
            say(token, repo_url, track_pr, st, f"**Done.** `{goal['acceptance']}` passes on main at `{st['head'][:12]}`: {passes}/{total} checks, after {st['round']} overseer round(s).")
            save_state(allst); return "done"
        if proposals_settling(st):
            st["state"] = "waiting"; log("a proposal is still being laid out"); save_state(allst); return "waiting"
        alive, dead = alive_work(repo_url, goal, st)
        if alive:
            st["state"] = "building"; log(f"{len(alive)} open bounties alive: {alive[:4]}")
            save_state(allst); return "building"
        # Red, and nothing on the board will move it. Did the last round help?
        if st["round"] > 0:
            if passes > st["best"]:
                st["best"], st["stall"] = passes, 0
            else:
                st["stall"] += 1
        else:
            st["best"] = passes
        if st["stall"] >= int(goal.get("stall_rounds", 3)) or st["round"] >= MAX_ROUNDS:
            st["state"] = "stalled"
            why = f"{st['stall']} round(s) without a new passing check" if st["stall"] >= int(goal.get("stall_rounds", 3)) else f"round cap {MAX_ROUNDS}"
            say(token, repo_url, track_pr, st, f"**Stopped: {why}.** {passes}/{total} checks pass on main at `{st['head'][:12]}`. Still failing:\n" +
                "\n".join(f"- {k}: {v[5:]}" for k, v in sorted(checks.items()) if v.startswith("FAIL")) +
                ("\n\nGave up:\n" + "\n".join(f"- {d}" for d in dead) if dead else ""))
            save_state(allst); return "stalled"
        pid = propose(token, repo_url, goal, host, st, checks, out, dead, keys_home, dry)
        if pid:
            st["round"] += 1; st["proposals"].append(pid); st["state"] = "filed"; st["progress_at"] = time.time()
            say(token, repo_url, track_pr, st, f"Round {st['round']} filed: {passes}/{total} checks pass on main; proposal `{pid}` covers what still fails.")
        save_state(allst)
        return "filed"
    finally:
        shutil.rmtree(work, ignore_errors=True)


def discover_goals(repo_url: str, token: str) -> List[Tuple[str, Optional[int]]]:
    """Every goals/*/goal.json on main, with its track_pr if the file names one."""
    work = Path(tempfile.mkdtemp(prefix="overseer-ls-"))
    try:
        if subprocess.run(["git"] + auth_args(token) + ["clone", "-q", "--depth", "1", repo_url, str(work / "h")], capture_output=True).returncode:
            return []
        out = []
        for gj in sorted((work / "h" / "goals").glob("*/goal.json")):
            try:
                g = json.loads(gj.read_text()); pr = g.get("track_pr")
            except (OSError, json.JSONDecodeError):
                pr = None
            out.append((f"goals/{gj.parent.name}/goal.json", int(pr) if pr else None))
        return out
    finally:
        shutil.rmtree(work, ignore_errors=True)


def main(argv: List[str]) -> int:
    def opt(name, default=None):
        return argv[argv.index(name) + 1] if name in argv else default
    repo = opt("--repo"); goal = opt("--goal"); pr = opt("--track-pr")
    token = os.environ.get("OVERSEER_GITHUB_TOKEN") or os.environ.get("CERATA_GITHUB_TOKEN", "")
    keys_home = os.environ.get("OVERSEER_HOME", str(Path.home() / ".overseer"))
    if not repo or not goal or not token:
        print("usage: python -m cerata_action oversee --repo <url> --goal <path in repo> [--track-pr <n>]  (needs OVERSEER_GITHUB_TOKEN)")
        return 2
    if "--all-goals" in argv:
        rc = 0
        for gpath, gpr in discover_goals(repo, token):
            try:
                tick(repo, gpath, token, keys_home, int(pr) if pr else gpr, dry="--dry-run" in argv)
            except Exception as e:
                log(f"tick failed for {gpath}: {e}"); rc = 1
        return rc
    try:
        tick(repo, goal, token, keys_home, int(pr) if pr else None, dry="--dry-run" in argv)
        return 0
    except Exception as e:
        log(f"tick failed: {e}")
        return 1
