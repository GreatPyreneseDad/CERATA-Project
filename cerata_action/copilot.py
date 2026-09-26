"""Hand consumption to GitHub Copilot's cloud agent. No model key needed.

CERATA hunts (deterministic, free), writes a consume brief as a new issue, and assigns it to
Copilot. Copilot does the metabolism in its own sandbox and opens the PR. This is how the
first outside-the-walls consume (tldextract, PR #1) happened.

Needs: a paid Copilot plan with the cloud agent enabled for the repo, and a *user* token
(classic/fine-grained PAT with issues + pull requests write). The workflow GITHUB_TOKEN cannot
assign Copilot: GitHub only accepts user-to-server tokens for agent assignment.
"""

from pathlib import Path
from typing import Dict, List

from cerata_action.consume import SYSTEM
from cerata_action.github_api import GitHub

ASSIGNEE = "copilot-swe-agent[bot]"
AGENT_NAME = "cerata"


def agent_profile_present(host: Path) -> bool:
    agents = host / ".github" / "agents"
    return any((agents / f"{AGENT_NAME}{ext}").is_file() for ext in (".agent.md", ".md"))


def brief(slug: str, hunt: Dict, files: List[str], focus: str) -> str:
    c, lic = hunt["coherence"], hunt["license"]
    cands = "\n".join(f"- `{n['path']}` ({n['functions']} fn, {n['classes']} cls, {n['lines']} lines)"
                      for n in hunt["nematocyst_candidates"][:8])
    targets = "\n".join(f"- `{p}`" for p in files)
    return f"""## 🐚 CERATA consume brief: `{slug}`

**Prey:** https://github.com/{slug} pinned at commit `{hunt['commit']}`
**License:** {lic['note']} (upstream file: `{lic.get('file') or 'none'}`)
**Coherence:** `{c['coherence']:.3f}` (Ψ {c['psi']:.2f} · ρ {c['rho']:.2f} · q {c['q']:.2f} · f {c['f']:.2f}), `{hunt['viability']['viability']}`

### Consume
{targets}

### Other candidates
{cands}
{f'''
### Operator focus
{focus}
''' if focus else ''}
### Deliverables (one PR)
1. The integration: digested, adapted, zero new dependencies where possible, attribution header on every consumed file.
2. Copy the upstream license file verbatim (do not write your own) to `<integration dir>/LICENSE-{slug.split('/')[1]}`.
3. Tests in the host's language that run without network: Python `unittest` (`python -m unittest <file>`), or for TS/JS `node:test` files (`node --test <file>`) that need no `npm install`. Run them and make them pass.
4. Wire it: modify the existing code that should use the capability so EXPERIMENTAL is selectable behind a flag defaulting to CLASSIC. A library nothing calls is not a trial.
5. Trial records `forest/classic_<domain>_gen<N>.md` and `forest/experimental_<domain>_gen<N+1>.md`. Any number not measured by a test in the PR is labelled "target".
6. PR body with a Hunt Record (prey, commit, license, coherence), a nematocyst table, what was discarded, and warnings.

If the prey does not fill a real gap in this repo, say so in the PR and change nothing. A false integration is worse than none.

<details><summary>CERATA protocol</summary>

{SYSTEM}
</details>
"""


def handoff(gh_user: GitHub, host: Path, repo: str, base: str, slug: str, hunt: Dict,
            files: List[str], focus: str) -> Dict:
    body = brief(slug, hunt, files, focus)
    custom_agent = AGENT_NAME if agent_profile_present(host) else ""
    return gh_user.request("POST", f"/repos/{repo}/issues", {
        "title": f"CERATA: consume {slug}",
        "body": body,
        "labels": ["cerata:consume"],
        "assignees": [ASSIGNEE],
        "agent_assignment": {
            "target_repo": repo,
            "base_branch": base,
            "custom_instructions": "Follow the CERATA consume brief in this issue exactly.",
            "custom_agent": custom_agent,
            "model": "",
        },
    })
