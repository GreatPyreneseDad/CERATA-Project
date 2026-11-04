#!/usr/bin/env bash
# vendored from buildup sandbox/run.sh @ 1852c20 — keep in sync; buildup/goals/sandbox is its referee.
# sandbox/run.sh — containment runner for builders' repros and the judge's evaluation builds.
#
#   sandbox/run.sh <workdir> -- <cmd> [args...]
#
# The child runs with <workdir> as cwd and as the only writable location, in new user, mount, pid and network
# namespaces (no network). Secret-shaped environment variables are removed, paths in SANDBOX_HIDE (colon-separated)
# read as absent/empty, SANDBOX_TIMEOUT seconds (default 900) of wall clock and SANDBOX_MEM megabytes (default 2048)
# of address space are enforced. Stdout, stderr and the exit code are the child's. Files written under <workdir> stay.
# Needs util-linux unshare and setpriv, GNU timeout, and unprivileged user namespaces.
set -u

usage() { echo "usage: run.sh <workdir> -- <cmd> [args...]" >&2; exit 2; }
[ "$#" -ge 3 ] && [ "$2" = "--" ] || usage
WD=$1; shift 2

for t in unshare setpriv timeout env; do
  command -v "$t" >/dev/null 2>&1 || { echo "run.sh: $t not found" >&2; exit 126; }
done

TMO=${SANDBOX_TIMEOUT:-900}; MEM=${SANDBOX_MEM:-2048}
for v in "$TMO" "$MEM"; do
  case "$v" in ''|*[!0-9]*|??????????*) echo "run.sh: SANDBOX_TIMEOUT and SANDBOX_MEM must be whole numbers (at most 9 digits)" >&2; exit 2;; esac
done
# force base 10 (08 is not octal) and refuse 0: timeout(1) reads 0 as "no limit"
TMO=$((10#$TMO)); MEM=$((10#$MEM))
[ "$TMO" -ge 1 ] && [ "$MEM" -ge 1 ] || { echo "run.sh: SANDBOX_TIMEOUT and SANDBOX_MEM must be at least 1" >&2; exit 2; }

mkdir -p "$WD" && WD=$(cd "$WD" && pwd -P) || { echo "run.sh: cannot create workdir" >&2; exit 126; }

# strip every secret-shaped variable before the child can see the environment
SCRUB=()
for n in $(compgen -e); do
  up=${n^^}
  if [[ "$up" =~ (SECRET|TOKEN|PASSW|CREDENTIAL|API_?KEY|PRIVATE_?KEY|_KEY$|^KEY$) ]]; then SCRUB+=(-u "$n"); fi
done

INNER=$(cat <<'EOF'
set -u
wd=$1; hide=$2; tmo=$3; mem=$4; shift 4
mount --make-rprivate / || exit 126
mount --bind "$wd" "$wd" || exit 126
# read-only root: every mount except the work dir; a failure on / is fatal, the rest is best effort
while IFS= read -r mp; do
  mp=$(printf '%b' "$mp")
  case "$mp" in "$wd"|"$wd"/*) continue;; esac
  mount -o remount,bind,ro "$mp" 2>/dev/null || [ "$mp" != / ] || exit 126
done < <(awk '{print $5}' /proc/self/mountinfo)
# hidden paths: files read empty, directories read as an empty read-only tmpfs; failing to hide is fatal
IFS=: read -ra hp <<<"$hide"
for p in "${hp[@]}"; do
  [ -n "$p" ] || continue
  if [ -d "$p" ]; then mount -t tmpfs -o ro tmpfs "$p" || exit 126
  elif [ -e "$p" ]; then mount --bind /dev/null "$p" || exit 126
  fi
done
cd "$wd" || exit 126
# the rest of the filesystem is read-only, so scratch space has to live under the work dir
case "${TMPDIR:-}" in "$wd"/*) ;; *) mkdir -p "$wd/.tmp" && export TMPDIR="$wd/.tmp";; esac
ulimit -v $((mem * 1024)) || exit 126
# root in this user namespace could remount the filesystem read-write: drop every capability before the child runs
timeout -k 2 "$tmo" setpriv --no-new-privs --bounding-set=-all --inh-caps=-all "$@"
exit $?
EOF
)

exec env "${SCRUB[@]}" unshare --map-root-user --mount --net --pid --fork --mount-proc \
  bash -c "$INNER" sandbox "$WD" "${SANDBOX_HIDE:-}" "$TMO" "$MEM" "$@"
