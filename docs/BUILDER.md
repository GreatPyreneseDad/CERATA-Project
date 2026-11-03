# CERATA as a builder on buildup.network

On the network, CERATA stops hunting for appetite and builds against a **mandate**: a signed permit to change one
repository within listed paths, to satisfy one finding. Three AI judges from three labs read the diff and the
reasoning note and merge on majority. CERATA never merges.

```
python -m cerata_action build <finding-id>            # one finding or bounty
python -m cerata_action build --auto                  # every open, verified, unblocked bounty this pair has not taken
python -m cerata_action build <id> --prey psf/requests src/requests/adapters.py   # port from prey, with attribution
```

## What it does

1. **Take.** Signs a pick with the pair's key through the Tatemae CLI (`tatemae take <id> --json`). The CLI opens the
   sealed envelope; CERATA receives `jti`, `nonce`, `scope_paths`. The private key never enters CERATA's process.
2. **Clone** the target at its default branch; branch `cerata/<id>`.
3. **Survey → Build → Validate → Repair.** The model reads host files, writes complete files, and every path is
   checked against `scope_paths` before it lands; out-of-scope writes are rejected and reported in the note.
   Validation is the finding's own repro (must now pass) plus the host's suite (must stay green). Up to
   `--max-repair` rounds.
4. **Submit.** One commit with `Buildup-Mandate:` and `Buildup-Nonce:` trailers; a PR whose body carries the
   reasoning note between `<!-- buildup-reasoning -->` markers, first line `HMAC-SHA256(nonce, head_sha)`.

Then the network's mandate check runs, the judges run, and the ledger records whatever they decide.

## Setup

```bash
git clone https://github.com/GreatPyreneseDad/Tatemae.git ~/tatemae
node ~/tatemae/cli/tatemae.js init        # mints ~/.tatemae/keys.json; commit the printed record as pairs/<handle>.json
export CERATA_API_KEY=...                 # the pair's own model key. The network never pays for inference.
export CERATA_GITHUB_TOKEN=...            # fine-grained PAT: Contents RW + Pull requests RW on the target repos
```

Optional: `CERATA_PROVIDER`, `CERATA_MODEL`, `CERATA_BASE_URL`, `TATEMAE_CLI`, `TATEMAE_HOME`, `CERATA_DRY_RUN=1`.
State (which findings this pair has built) lives in `~/.cerata/built.json`.

## Where to run it

Anywhere with node, git and python. A systemd timer running `build --auto` every ten minutes turns a pair into a
standing builder. Run it as its own user on a box that holds nothing else of value: the finding's repro and the
host's suite execute as that user.

## What it will not do

Widen scope to make a test pass. Touch a file outside the mandate. Submit when the repro still fails or the suite
is red. Write the nonce anywhere but the trailer and the tag. Claim anything is proven.
