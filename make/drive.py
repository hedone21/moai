#!/usr/bin/env python3
"""Drive a bash in a pty for one scene; asciinema records what it prints.

    asciinema rec --cols 110 --rows 24 -q -c 'drive.py <scene> <repo>' out.cast

Modelled on scripts/site-demo/shell.py. A step is (seconds to wait first, line to send). A callable
line is built when it is sent, so a step can name an id that an earlier step made.
"""
import fcntl, json, os, pty, select, signal, struct, subprocess, sys, termios, time

ROOT = os.environ['DEMO_ROOT']
REPO = os.path.join(ROOT, 'lantern')
DONE = os.path.join(ROOT, '.scenes-done')

ASK = 'ask() { echo "$1" | socat -t 2 - UNIX-CONNECT:$XDG_RUNTIME_DIR/moai/daemon.socket; }'
POLL = ('poll() { r=$(ask \'{"jsonrpc":"2.0","id":9,"method":"changes",'
        '"params":{"project":"/tmp/mira/lantern","cursor":"\'"$C"\'"}}\'); '
        'C=$(jq -r .result.value.cursor <<<"$r"); jq -c \'.result.value | del(.cursor)\' <<<"$r"; }')


def ids():
    with open(os.path.join(REPO, '.demo-ids')) as f:
        return dict(l.strip().split('=', 1) for l in f if '=' in l)


def moai_json(env, *args):
    out = subprocess.run([env['MOAI'], *args, '--json'], cwd=REPO, env=env, capture_output=True, text=True)
    return json.loads(out.stdout)


def scenes(env):
    def line(text, then=1.2):
        return (then, text + '\r')

    def by_title(title):
        # seed.sh mints new ids on every run, so a step finds its row by title when it is sent
        rows = [r for r in moai_json(env, 'show', '--all') if r['title'] == title]
        return rows[0]['id']

    return {
        # terminal 1: the daemon in the foreground until the client scenes are done
        'daemon': [
            (0.6, None),
            line('moai daemon start', then=0.4),
            ('until', DONE),
        ],
        # terminal 2: register the project, look at the daemon, a second start is refused
        'start': [
            (0.6, None),
            line('moai project add .', then=0.4),
            line('moai daemon status'),
            line('moai daemon start'),
        ],
        # raw JSON-RPC 2.0 over the socket
        'ask': [
            (0.6, None),
            line(ASK, then=0.4),
            line('ask \'{"jsonrpc":"2.0","id":1,"method":"hello","params":{"proto":1}}\''),
            line('ask \'{"jsonrpc":"2.0","id":2,"method":"show","params":{"project":"/tmp/mira/lantern","status":"todo"}}\' '
                 '| jq -c \'.result.value[] | {id, assignee, title}\''),
            line('ask \'{"jsonrpc":"2.0","id":3,"method":"ready","params":{"project":"/tmp/mira/lantern"}}\' '
                 '| jq -c \'.result | {ready: [.value.ready[].id], messages, partial}\''),
            line('ask \'{"jsonrpc":"2.0","id":4,"method":"show","params":{"project":"/tmp/mira/lantern","stauts":"todo"}}\' '
                 '| jq -c .error'),
        ],
        # the same JSON value as the CLI's --json (jq -S sorts keys: the daemon's come sorted)
        'parity': [
            (0.6, None),
            line('diff <(ask \'{"jsonrpc":"2.0","id":5,"method":"show","params":{"project":"/tmp/mira/lantern","status":"todo"}}\' '
                 '| jq -S .result.value) <(moai --json show -s todo | jq -S .) && echo same'),
            line('diff <(ask \'{"jsonrpc":"2.0","id":6,"method":"show","params":{"project":"/tmp/mira/lantern","all":true,"sort":"due"}}\' '
                 '| jq -S .result.value) <(moai --json show --all --sort due | jq -S .) && echo same'),
            line('diff <(ask \'{"jsonrpc":"2.0","id":7,"method":"stats","params":{"project":"/tmp/mira/lantern"}}\' '
                 '| jq -S .result.value) <(moai --json stats | jq -S .) && echo same'),
            line('diff <(ask \'{"jsonrpc":"2.0","id":8,"method":"status","params":{"project":"/tmp/mira/lantern"}}\' '
                 '| jq -S .result.value) <(moai --json status | jq -S .) && echo same'),
        ],
        # polling changes while the CLI writes. Finishing "Slash command menu" (in review) moves its epic
        # "Editor polish" from review back to in_progress, since one member is still todo: a derived column,
        # so the epic is in `changed` too
        'changes': [
            (0.6, None),
            line(POLL, then=0.4),
            line('poll'),
            line('poll'),
            (1.2, lambda: f"moai mv {by_title('Slash command menu')} done\r"),
            line('poll'),
            line("moai add 'Export a notebook as PDF'"),
            line('poll'),
            (1.2, lambda: f"moai rm {by_title('Export a notebook as PDF')}\r"),
            line('poll'),
            line('moai daemon stop', then=1.5),
        ],
    }


def main():
    scene = sys.argv[1]
    cols, rows = os.get_terminal_size(sys.stdout.fileno()) if sys.stdout.isatty() else (120, 24)
    bindir = os.path.join(ROOT, '.local', 'bin')
    env = dict(TZ='UTC', TERM='xterm-256color', COLORTERM='truecolor', LANG='C.UTF-8', MOAI_LANG='en',
               MOAI_NO_UPDATE_CHECK='1', MOAI=os.path.join(bindir, 'moai'),
               MOAI_CONFIG=os.path.join(REPO, '.demo-home', 'config.toml'), MOAI_NOW=os.environ['MOAI_NOW'],
               XDG_RUNTIME_DIR=os.path.join(ROOT, 'run'), HOME=ROOT,
               PATH=bindir + ':/usr/local/bin:/usr/bin:/bin')
    rc = os.path.join(ROOT, '.bashrc-demo')
    pid, fd = pty.fork()
    if pid == 0:
        fcntl.ioctl(0, termios.TIOCSWINSZ, struct.pack('HHHH', rows, cols, 0, 0))
        os.chdir(REPO)
        os.execve('/bin/bash', ['bash', '--rcfile', rc, '-i'], env)
    out = sys.stdout.buffer
    seen = {'row': 1}

    def pump(seconds):
        end = time.time() + seconds
        while True:
            left = end - time.time()
            if left <= 0:
                return
            r, _, _ = select.select([fd], [], [], left)
            if r:
                try:
                    data = os.read(fd, 65536)
                except OSError:
                    return
                if b'\x1b[6n' in data:
                    head = data.split(b'\x1b[6n', 1)[0]
                    row = min(rows, seen['row'] + head.count(b'\n'))
                    os.write(fd, f'\x1b[{row};1R'.encode())
                seen['row'] = min(rows, seen['row'] + data.count(b'\n'))
                out.write(data)
                out.flush()

    for wait, what in scenes(env)[scene]:
        if wait == 'until':
            while not os.path.exists(what):
                pump(0.2)
            pump(1.5)
            continue
        pump(wait)
        if what is None:
            continue
        if callable(what):
            what = what()
        os.write(fd, what.encode())
    pump(1.0)
    try:
        os.kill(pid, signal.SIGTERM)
    except ProcessLookupError:
        pass


if __name__ == '__main__':
    main()
