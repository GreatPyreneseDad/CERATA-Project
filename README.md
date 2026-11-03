# CERATA — The Evolving Predator

**A Claude Project that grows through predation**

> *"The habitat changes everything. The body is the conversation."*

---

## Run CERATA on your repo

CERATA ships as a GitHub Action. Install it once and command it from any issue:

```
/cerata hunt psf/requests                          # Rose Glass perception report + license check
/cerata consume psf/requests src/requests/adapters.py   # metabolize → pull request
/cerata consume owner/repo -- only the retry logic # steer the metabolism
```

**Setup (2 minutes):**

1. Copy [`templates/workflows/cerata.yml`](templates/workflows/cerata.yml) to `.github/workflows/cerata.yml`.
2. Pick what powers `consume` (`hunt` needs nothing):
   - **Any model:** add a `CERATA_API_KEY` secret. Anthropic, OpenAI, OpenRouter, Gemini, DeepSeek, Mistral, Groq, Together, xAI and Ollama keys are auto-detected, and any OpenAI-compatible endpoint works via `base-url`.
   - **No model key, via Copilot:** set `provider: copilot` and add a PAT as `CERATA_COPILOT_PAT` (a paid Copilot plan is required). CERATA hunts, writes a consume brief as an issue and assigns it to Copilot's cloud agent, which opens the PR. Copy [`templates/agents/cerata.agent.md`](templates/agents/cerata.agent.md) to `.github/agents/` so Copilot works as CERATA. That profile also lets people run `hunt` and `consume` straight from Copilot, with no Action at all.
3. Settings → Actions → General → enable **Allow GitHub Actions to create and approve pull requests**.

**What consume does:** clones the prey, runs the hunt, refuses copyleft or unlicensed code, asks the
model to survey your repo, then digests the chosen files into a self-contained capability with tests
and CLASSIC/EXPERIMENTAL trial records. It runs those tests (sandboxed as an unprivileged user) and
lets the model repair failures. Then it opens a PR carrying the hunt record, the upstream license and
attribution. Nothing merges itself.

**Safety model:** only owners, members and collaborators can command it. Prey code is treated as
untrusted data. The model can't write to `.git/`, `.github/` or `.cerata/`. The persisted checkout
token is stripped before any generated code runs. Read every consume PR before merging it.

---

## Two halves

What's above is the **Action**: code, tests, a safety model, and it runs today. The other half of CERATA is a way of
running a Claude Project where repositories are prey and capabilities compete in dual-branch trials. That half is
design and ritual, not software yet; it lives in [`docs/BODY.md`](docs/BODY.md) and [`CERATA.md`](CERATA.md).

## What the hunt measures

The hunt reads a repository through four Rose Glass dimensions and reports a fifth beside them. Each is a structural
proxy computed from the clone, named in the report so you can weigh it:

| Dim | Proxy |
|---|---|
| Ψ consistency | readme, tests, license, docs, both functions and classes present |
| ρ wisdom | tests, CI, test count, docstrings, comment density, type hints |
| q activation | commits in the last 90 days and days since the last one (from git history) |
| f belonging | manifests, config files, src/ or lib/ layout |
| τ survival | span of the history seen (reported, not folded into coherence) |

λ, the cost of adapting prey to your repo, depends on your repo and is the model's job during `consume`.
If the clone has no history, q is marked unknown and coherence is computed with q neutral. The report says so.

## On the network

CERATA is also a **builder** on [buildup.network](https://buildup.network): `cerata build <finding-id>` takes a
bounty under a signed mandate, metabolizes a fix within the mandate's scope, and opens a pull request carrying the
trailers and reasoning note the network's judges require. See [`docs/BUILDER.md`](docs/BUILDER.md).

## License

Apache-2.0. Consumed code keeps its upstream license and attribution; see each integration's `HUNT_MANIFEST.md`.
