"""`python -m cerata_action build ...` — run CERATA outside GitHub Actions (a VM, a laptop, a cron)."""

import os
import sys


def main() -> int:
    args = sys.argv[1:]
    if args and args[0] == "oversee":
        from cerata_action import oversee
        return oversee.main(args[1:])
    if not args or args[0] in ("-h", "--help") or args[0] != "build":
        print(__doc__.strip())
        print("\n  build <finding-id> [--prey owner/repo [path ...]] [--note '...'] [--dry-run]\n  build --auto\n"
              "\nenv: CERATA_API_KEY (any provider; CERATA_PROVIDER/CERATA_MODEL/CERATA_BASE_URL optional),\n"
              "     CERATA_GITHUB_TOKEN (push + pull requests on the target repos), TATEMAE_CLI (path to cli/tatemae.js),\n"
              "     TATEMAE_HOME (where keys.json lives), CERATA_DRY_RUN=1 to build without pushing.")
        return 0 if args and args[0] in ("-h", "--help") else 2
    from cerata_action import build, llm
    client = llm.make(os.environ.get("CERATA_PROVIDER", "auto"), os.environ.get("CERATA_API_KEY", ""),
                      os.environ.get("CERATA_MODEL", ""), os.environ.get("CERATA_BASE_URL", ""),
                      int(os.environ.get("CERATA_MAX_OUTPUT_TOKENS", "32000")))
    argv = args[1:]
    dry = "--dry-run" in argv or os.environ.get("CERATA_DRY_RUN") == "1"
    argv = [a for a in argv if a != "--dry-run"]
    token = os.environ.get("CERATA_GITHUB_TOKEN", "")
    if not token and not dry:
        print("CERATA_GITHUB_TOKEN is required to push and open the PR (or pass --dry-run)")
        return 2
    return build.main(argv, client, token, dry)


if __name__ == "__main__":
    sys.exit(main())
