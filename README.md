# Pictures for the moai-5n6m pull request

This branch holds only the pictures of the pull request "moai daemon — local read API over JSON-RPC 2.0 (moai-5n6m)" to `buzzni/moai:daemonize`, and the scripts that made them. It shares no history with moai and is never merged. The pull request links each picture by the commit of this branch, so do not rewrite it.

| File | What it shows |
|---|---|
| `media/01-overview.drawio.png` | What the PR adds. The PNG embeds its draw.io source, so draw.io opens it for editing |
| `media/02-start.png` | `moai daemon start` in one terminal, `project add`, `daemon status`, and a second `start` that only says a daemon is already running (exit 0) in another |
| `media/03-ask.png` | Raw JSON-RPC 2.0 lines over the socket with `socat`: `hello`, `show`, `ready`, an unknown param |
| `media/04-parity.png` | The daemon's `value` against `moai --json` for `show`, `show --all --sort due`, `stats` and `status` |
| `media/05-changes.png` | Polling `changes` while the CLI moves, adds and removes rows |

## How they were made

The screenshots are a real run of the branch's release binary (`moai 0.48.0` at `292557f8`) in a demo repository, Lantern, that `scripts/site-demo/seed.sh` builds. Nothing on them was typed by hand or edited afterwards.

    MOAI=<moai with daemon> SEED=<moai>/scripts/site-demo/seed.sh make/record.sh casts
    make/render.sh casts raw
    python3 make/frame.py -o media/02-start.png 'terminal 1 — moai daemon start' raw/daemon.png 'terminal 2' raw/start.png
    python3 make/frame.py -o media/03-ask.png 'JSON-RPC 2.0 over the Unix socket' raw/ask.png
    python3 make/frame.py -o media/04-parity.png "the daemon answers with the CLI's --json value" raw/parity.png
    python3 make/frame.py -o media/05-changes.png 'polling changes while the CLI writes' raw/changes.png
    drawio -x -f png -e -s 2 -b 16 -o media/01-overview.drawio.png make/overview.drawio

- `record.sh` builds the demo in `/tmp/mira` (so no path of the recording machine shows) and points `XDG_RUNTIME_DIR` inside it, so the recorded daemon never meets a daemon that the person runs. It fixes the clock with `MOAI_NOW`. The ids change on every run, because `seed.sh` mints new ones.
- `drive.py` types each scene into a bash in a pty, as `scripts/site-demo/shell.py` does; `asciinema` 2 records it.
- `render.sh` draws each recording with `agg` in the homepage's terminal colours and keeps the last screen. The daemon window is cut at its "listening" line.
- `frame.py` crops empty rows and draws the window frame.
- Needs: `asciinema`, `agg`, ImageMagick, Python with Pillow, `socat`, `jq`, draw.io desktop.
