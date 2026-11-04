# Pictures for the moai-3hgm pull request

This branch holds only the pictures of the pull request "moai daemon — write methods (moai-3hgm)" to `buzzni/moai:daemonize`, and the scripts that made them. It shares no history with moai and is never merged. The pull request links each picture by the commit of this branch, so do not rewrite it.

| File | What it shows |
|---|---|
| `media/01-overview.drawio.png` | What the PR adds on top of PR #78. The PNG embeds its draw.io source, so draw.io opens it for editing |
| `media/02-write.png` | `moai daemon start` in one terminal; in another, `add`, `note` (with another `actor`), `mv`, and a `mv` whose `from` lost the race (`exit` 1), then the CLI reads the row the daemon wrote |
| `media/03-theirs.png` | A `mv` of someone else's row is not refused: the CLI's notice comes in `messages`; `take: true` takes it over |
| `media/04-parity.png` | The daemon's `value` against `moai --json` for `show`, `stats` and `status`, compared without sorting keys |
| `media/05-changes.png` | Polling `changes` while the daemon and the CLI both write |

## How they were made

The screenshots are a real run of the branch's release binary (`moai 0.48.0` at the head of `worktree-moai-3hgm`) in a demo repository, Lantern, that `scripts/site-demo/seed.sh` builds. Nothing on them was typed by hand or edited afterwards.

    MOAI=<moai with daemon> SEED=<moai>/scripts/site-demo/seed.sh make/record.sh casts
    make/render.sh casts raw
    python3 make/frame.py -o media/02-write.png 'terminal 1 — moai daemon start' raw/daemon.png 'terminal 2 — writes over the socket' raw/write.png
    python3 make/frame.py -o media/03-theirs.png "someone else's row: not refused, the notice comes in messages" raw/theirs.png
    python3 make/frame.py -o media/04-parity.png "value is the CLI's --json, byte for byte" raw/parity.png
    python3 make/frame.py -o media/05-changes.png 'polling changes while the daemon and the CLI write' raw/changes.png
    drawio -x -f png -e -s 2 -b 16 -o media/01-overview.drawio.png make/overview.drawio

- `record.sh` builds the demo in `/tmp/mira` (so no path of the recording machine shows) and points `XDG_RUNTIME_DIR` inside it, so the recorded daemon never meets a daemon that the person runs. It fixes the clock with `MOAI_NOW`. The ids change on every run, because `seed.sh` mints new ones; `drive.py` finds rows by title, and "someone else's row" is the first todo issue not held by Mira when the scene runs.
- `drive.py` types each scene into a bash in a pty, as `scripts/site-demo/shell.py` does; `asciinema` 2 records it.
- `render.sh` draws each recording with `agg` in the homepage's terminal colours and keeps the last screen. The daemon window is cut at its "listening" line.
- `frame.py` crops empty rows and draws the window frame.
- Needs: `asciinema`, `agg`, ImageMagick, Python with Pillow, `socat`, `jq`, draw.io desktop.

The pictures of PR #78 (the read API) are on `pr-media-moai-5n6m`.
