"""Render CERATA output as GitHub-flavoured markdown."""

from typing import Dict, List

SIGNATURE = "<sub>🐚 CERATA · coherence is constructed, not discovered</sub>"

HELP = f"""### 🐚 CERATA

| Command | What happens |
|---|---|
| `/cerata hunt owner/repo` | Clone the prey, read it through Rose Glass (Ψ ρ q f), check its license, list nematocyst candidates. |
| `/cerata consume owner/repo` | Metabolize the top candidates into this repo and open a pull request with the integration, tests and trial records. |
| `/cerata consume owner/repo path/a.py path/b.py` | Consume specific files. |
| `/cerata consume owner/repo -- focus note` | Anything after ` -- ` steers the metabolism (e.g. `-- only the retry logic`). |
| `/cerata help` | This table. |

Hunt is free. Consume uses whatever the workflow is configured with: any model API key, or GitHub Copilot
(no model key). Only owners, members and collaborators can command CERATA.
Nothing merges itself: every consume lands as a PR for a human to review.

{SIGNATURE}"""


def _fmt(v) -> str:
    return "—" if v is None else f"{v:.2f}"


def _bar(v: float, width: int = 10) -> str:
    n = max(0, min(width, round(v * width)))
    return "█" * n + "░" * (width - n)


def _dim_row(name: str, v, note: str) -> str:
    if v is None:
        return f"| {name} | `—` | `{'░' * 10}` | {note} |"
    return f"| {name} | `{v:.2f}` | `{_bar(v)}` | {note} |"


def _history_note(h) -> str:
    if not h or not h.get("commits_seen"):
        return "no git history read"
    return f"{h['commits_last_90d']} commits in 90d, last {h['days_since_last_commit']}d ago"


def _span_note(h) -> str:
    if not h or not h.get("commits_seen"):
        return "no git history read"
    return f"{h['span_days_seen']}d of history seen" + (" (shallow clone)" if h.get("shallow") else "") + f", {h['authors_seen']} authors"


def hunt_markdown(slug: str, r: Dict) -> str:
    c, v, lic, s = r["coherence"], r["viability"], r["license"], r.get("signals", {})
    lines: List[str] = [
        f"### 🎯 HUNT: [`{slug}`](https://github.com/{slug}) @ `{r['commit'][:7]}`",
        "",
        "| Dim | Reading | | Measured from |",
        "|---|---|---|---|",
        f"| Ψ consistency | `{c['psi']:.2f}` | `{_bar(c['psi'])}` | readme, tests, license, docs, structure |",
        f"| ρ wisdom | `{c['rho']:.2f}` | `{_bar(c['rho'])}` | tests, CI, docstrings, comments, types |",
        _dim_row("q activation", c.get("q"), _history_note(r.get("history"))),
        f"| f belonging | `{c['f']:.2f}` | `{_bar(c['f'])}` | manifests, config, src/ layout |",
        _dim_row("τ survival", c.get("tau"), _span_note(r.get("history"))),
        f"| **Coherence** | **`{c['coherence']:.2f}`** / 4 | | Ψ ρ q f; τ and λ reported, not folded in |",
        "",
        f"**Viability: `{v['viability']}`**: {v['recommendation']}",
        "",
        f"**License:** {'✅' if lic['consumable'] else '⛔'} {lic['note']}",
    ]
    st = r["structure"]
    if st.get("js_files", 0) > st.get("python_files", 0):
        v.setdefault("warnings", []).append(
            "Mostly JS/TS: hunt.py's ρ reads Python docstrings/type hints only, so ρ is understated")
    if v.get("warnings"):
        lines += ["", "**Warnings**"] + [f"- {w}" for w in v["warnings"]]
    if s:
        obs = []
        if s.get("stars") is not None:
            obs.append(f"★ {s['stars']:,}")
        if s.get("days_since_push") is not None:
            obs.append(f"last push {s['days_since_push']}d ago")
        if s.get("archived"):
            obs.append("archived")
        if obs:
            lines += ["", f"<sub>Observed (not scored): {' · '.join(obs)}</sub>"]
    cands = r.get("nematocyst_candidates", [])[:5]
    if cands:
        lines += ["", "**Nematocyst candidates**", "", "| # | Path | fn | cls | lines |", "|---|---|---|---|---|"]
        for i, n in enumerate(cands, 1):
            lines.append(f"| {i} | `{n['path']}` | {n['functions']} | {n['classes']} | {n['lines']} |")
    else:
        lines += ["", "_No nematocysts detected (CERATA reads Python, TypeScript and JavaScript)._"]
    lines.append("")
    if v["proceed"] and lic["consumable"]:
        top = " ".join(n["path"] for n in cands[:2])
        lines += ["**Next:**", "```", f"/cerata consume {slug} {top}".rstrip(), "```"]
    else:
        lines.append("✗ **Consumption not recommended.**")
    lines += ["", SIGNATURE]
    return "\n".join(lines)


def pr_body(slug: str, hunt: Dict, plan: Dict, tests: Dict, rounds: int) -> str:
    c = hunt["coherence"]
    nem = plan.get("nematocysts", [])
    rows = "\n".join(
        f"| `{n.get('name','?')}` | `{n.get('source','?')}` | {n.get('dimension','')} | {n.get('purpose','')} |"
        for n in nem) or "| — | — | — | — |"
    test_line = ("✅ passed" if tests.get("passed") else
                 "⚠️ **failed**. Review before merging" if tests.get("ran") else
                 "➖ not run (no runnable tests detected)")
    files = "\n".join(f"- `{p}`" for p in plan.get("_written", []))
    details = ""
    if tests.get("ran"):
        details = ("<details><summary>test output</summary>\n\n```\n"
                   + tests.get("output", "")[-4000:] + "\n```\n</details>")
    return f"""## 🐚 CERATA consume: `{slug}`

{plan.get('summary', '').strip()}

### Hunt Record
- **Prey:** https://github.com/{slug} @ `{hunt['commit'][:12]}`
- **License:** {hunt['license']['note']}
- **Coherence:** `{c['coherence']:.2f}` (Ψ {c['psi']:.2f} · ρ {c['rho']:.2f} · q {_fmt(c.get('q'))} · f {c['f']:.2f} · τ {_fmt(c.get('tau'))}), `{hunt['viability']['viability']}`

### Nematocysts
| Nematocyst | Source | Dimension | Purpose |
|---|---|---|---|
{rows}

### Trial
**Integration point:** `{plan.get('integration_point', '?')}`

{plan.get('trial_notes', '').strip()}

### Validation
Tests: {test_line} after {rounds} metabolism round(s).
{details}

{plan.get('_extra', '').strip()}

### Files
{files}

---
Generated by CERATA with `{plan.get('_model', '?')}`. The prey's code was untrusted input to the model: **read every line before merging.**

{SIGNATURE}
"""
