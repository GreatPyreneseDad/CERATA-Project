# CERATA: Action → App roadmap

**Phase 1 (this release): GitHub Action.** Runs on the user's own Actions minutes with their own
model key. No servers, and nothing for ROSE Corp to host or pay for. Published to the Marketplace from `action.yml`.

**Phase 2: GitHub App shell.** A thin webhook receiver (Cloudflare Worker) that:

1. receives `issue_comment` events from installed repos,
2. verifies the webhook signature and the commenter's association,
3. calls `workflow_dispatch` on the installed repo's `cerata.yml` with the parsed command.

Compute and secrets stay in the user's repo. The App adds one-click install, a bot identity
(`cerata[bot]`), and org-wide install. App permissions needed: `issues: write`, `actions: write`,
`metadata: read`. It never needs `contents` because the Action does the writing.

**Phase 3: the commons.** Opt-in upload of `.cerata/hunts/*.json` and trial outcomes to a shared
index, so every installation's hunts teach every other installation's perception
(the graveyard becomes collective).

## Publishing checklist (Phase 1)

- [ ] Merge this branch; tag `v1.0.0` and a moving `v1` tag.
- [ ] Marketplace requires `action.yml` at the root **and no workflow files in `.github/workflows/`**.
      Keep CI for this repo in a separate repo or run the tests locally:
      `python -m unittest discover -s cerata_action/tests -t .`
- [ ] Draft release → "Publish this Action to the GitHub Marketplace" → category *Code quality*.
- [ ] The name "CERATA Hunt" must be unique on the Marketplace; adjust `name:` if taken.
