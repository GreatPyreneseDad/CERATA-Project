# CERATA: Action → App roadmap

**Phase 1 (this release): GitHub Action.** Runs on the user's own Actions minutes with their own
model key. No servers, and nothing for ROSE Corp to host or pay for. Published to the Marketplace from `action.yml`.

**Model access.** CERATA works with any model: native Anthropic, or any OpenAI-compatible endpoint
(OpenAI, OpenRouter, Gemini, DeepSeek, Mistral, Groq, Together, xAI, Ollama, self-hosted). With no model key,
`provider: copilot` hands consumption to Copilot's cloud agent on the user's Copilot plan.
GitHub Models, which would have given free inference through `GITHUB_TOKEN`, was retired on 2026-07-30,
so there is no zero-cost inference path inside Actions any more. Copilot is the no-key route.

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

- [x] Merge this branch; tag `v1.0.0` and a moving `v1` tag.
- [ ] Marketplace requires `action.yml` at the root **and no workflow files in `.github/workflows/`**.
      Keep CI for this repo in a separate repo or run the tests locally:
      `python -m unittest discover -s cerata_action/tests -t .`
- [ ] Draft release → "Publish this Action to the GitHub Marketplace" → category *Code quality*.
- [ ] The name "CERATA Hunt" must be unique on the Marketplace; adjust `name:` if taken.
