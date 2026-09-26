# Contributing to CERATA

CERATA improves the way it improves your repo: through hunts, trials and PRs.

- **Run it on CERATA itself.** `/cerata hunt <repo>` on an issue here, then `/cerata consume` if
  the prey fills a gap. The PR carries its own hunt record and trial files.
- **Report a trial outcome.** When a CLASSIC/EXPERIMENTAL trial resolves in your repo, open an issue
  with the `forest/` records. Winners and graveyard entries both sharpen `tools/hunt.py`.
- **Improve perception.** `tools/hunt.py` is the lens. Known gaps: `q` is a fixed placeholder
  (candidate: git activity via pydriller), τ and λ are unmeasured, and only Python is read.
- **Tests:** `python -m unittest discover -s cerata_action/tests -t .` (stdlib only, no network).

By contributing you agree your contributions are licensed under Apache-2.0.
Consumed third-party code must keep its upstream license file and attribution.
