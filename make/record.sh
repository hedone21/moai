#!/usr/bin/env bash
# Record the daemon scenes of the moai-5n6m PR: one daemon window and four client windows.
#
#     MOAI=<moai binary with `moai daemon`> SEED=<moai checkout>/scripts/site-demo/seed.sh record.sh <out dir>
#
# The demo lives in DEMO_ROOT (default /tmp/mira), so no path of the recording machine shows on screen.
# XDG_RUNTIME_DIR points inside it, so the daemon here never meets a daemon the person runs.
set -euo pipefail
here=$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)
out=$(mkdir -p "${1:?usage: record.sh <out dir>}" && cd "$1" && pwd)
moai=$(realpath -- "${MOAI:?set MOAI}")
seed=$(realpath -- "${SEED:?set SEED}")
root=${DEMO_ROOT:-/tmp/mira}
if [ -e "$root" ] && [ ! -e "$root/.moai-demo" ]; then
  echo "record.sh: $root exists and is not a demo home; set DEMO_ROOT" >&2; exit 1
fi
rm -rf "$root"
mkdir -p "$root/.local/bin" "$root/run"
chmod 700 "$root/run"
touch "$root/.moai-demo"
cp "$moai" "$root/.local/bin/moai"
export DEMO_ROOT=$root DEMO_NOW=${DEMO_NOW:-2026-11-04T09:00:00Z}
export MOAI_NOW=$DEMO_NOW
MOAI=$root/.local/bin/moai bash "$seed" "$root/lantern" >/dev/null
cat > "$root/.bashrc-demo" <<'RC'
PS1='\[\e[38;5;245m\]lantern\[\e[0m\] \[\e[38;5;209m\]$\[\e[0m\] '
ask() { echo "$1" | socat -t 2 - UNIX-CONNECT:$XDG_RUNTIME_DIR/moai/daemon.socket; }
RC

rec() { # <scene> <cols> <rows>
  asciinema rec --cols "$2" --rows "$3" --overwrite -q -c "python3 $here/drive.py $1" "$root/$1.cast" </dev/null >/dev/null
  jq -c 'if type == "object" and has("version") then del(.command, .env, .timestamp) else . end' \
    "$root/$1.cast" > "$out/$1.cast"
}

rec daemon 120 5 &
daemon=$!
for _ in $(seq 50); do [ -S "$root/run/moai/daemon.socket" ] && break; sleep 0.2; done
[ -S "$root/run/moai/daemon.socket" ] || { echo "record.sh: the daemon did not come up" >&2; exit 1; }
rec start 120 9
rec ask 120 21
rec parity 120 14
rec changes 120 26
touch "$root/.scenes-done"
wait "$daemon"
# the daemon window is shown while it runs: keep its events up to the "listening" line
python3 - "$out/daemon.cast" <<'PY'
import json, sys
lines = open(sys.argv[1]).read().splitlines()
keep = [lines[0]]
for l in lines[1:]:
    keep.append(l)
    if 'listening' in json.loads(l)[2]:
        break
open(sys.argv[1], 'w').write('\n'.join(keep) + '\n')
PY
rm -rf "$root"
echo "recorded into $out"
