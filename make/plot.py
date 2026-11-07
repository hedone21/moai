"""moai-upq5 PR 그림. ARGUS 스타일. `python3 plot.py ko` 와 `python3 plot.py en` 으로 두 언어를 그린다."""
import sys
from pathlib import Path

sys.path.insert(0, "/home/go/.claude/skills/argus-figure-style/scripts")

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from argus_style import ARGUS, DASH, FIGSIZE, FONT, apply_argus_style, save_figure

apply_argus_style()
plt.rcParams["font.family"] = ["Times New Roman", "Noto Serif CJK JP"]

LANG = sys.argv[1] if len(sys.argv) > 1 else "ko"
HERE = Path(__file__).parent / LANG
HERE.mkdir(exist_ok=True)
W = FIGSIZE.DOUBLE_COL[0] * 72  # 1 데이터 단위 = 1pt
INK = ARGUS.INK
MUTED = ARGUS.MUTED
RED = ARGUS.LINE_RED
PICK = ARGUS.BAR_LIME
PANEL = ARGUS.PLACEHOLDER
THIN, MID, THICK = 0.7, 1.0, 1.7
_checks = []


def T(ko, en):
    return ko if LANG == "ko" else en


def canvas(h):
    fig = plt.figure(figsize=(W / 72 - 0.02, h / 72))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xlim(0, W)
    ax.set_ylim(h, 0)
    ax.axis("off")
    return fig, ax


def text(ax, x, y, s, size=FONT.TICK, weight="normal", color=INK, ha="center", va="center", z=5):
    return ax.text(x, y, s, fontsize=size, fontweight=weight, color=color, ha=ha, va=va, zorder=z)


def box(ax, x, y, w, h, lines=(), fill="white", lw=THIN, ls="-", ec=INK, r=3, z=2, color=INK):
    ax.add_patch(
        FancyBboxPatch(
            (x, y), w, h, boxstyle=f"round,pad=0,rounding_size={r}", fc=fill, ec=ec, lw=lw, ls=ls, zorder=z, mutation_aspect=1
        )
    )
    norm = []
    for i, ln in enumerate(lines):
        if isinstance(ln, str):
            ln = (ln, FONT.TICK if i == 0 else FONT.NOTE, "normal", color)
        else:
            ln = tuple(ln) + (FONT.TICK, "normal", color)[len(ln) - 1 :]
        norm.append(ln)
    total = sum(n[1] * 1.28 for n in norm)
    cy = y + h / 2 - total / 2
    for s, size, weight, c in norm:
        t = text(ax, x + w / 2, cy + size * 0.64, s, size, weight, c, z=z + 3)
        _checks.append((t, x, w))
        cy += size * 1.28


def new(ax, x, y, w, h, lines):
    """이번 PR 의 핵심 동작. 연초록에 굵은 테두리."""
    head, *rest = lines
    box(ax, x, y, w, h, [(head, FONT.TICK, "bold"), *rest], fill=PICK, lw=THICK)


def off(ax, x, y, w, h, lines):
    """지원하지 않는 것. 점선에 흐린 글자."""
    box(ax, x, y, w, h, lines, ls=DASH.RULE, ec=MUTED, color=MUTED)


def route(ax, pts, lw=THIN, ls="-", color=INK, head=True, z=3):
    for (x0, y0), (x1, y1) in zip(pts[:-2], pts[1:-1]):
        ax.plot([x0, x1], [y0, y1], color=color, lw=lw, ls=ls, solid_capstyle="round", zorder=z)
    (x0, y0), (x1, y1) = pts[-2], pts[-1]
    if head:
        hl, hw = 3.6 + lw, 1.7 + lw * 0.5
        ax.add_patch(
            FancyArrowPatch(
                (x0, y0), (x1, y1), arrowstyle=f"-|>,head_length={hl},head_width={hw}", mutation_scale=1,
                color=color, lw=lw, ls=ls, shrinkA=0, shrinkB=0, zorder=z,
            )
        )
    else:
        ax.plot([x0, x1], [y0, y1], color=color, lw=lw, ls=ls, zorder=z)


def panel(ax, y, h, title):
    box(ax, 2, y, W - 4, h, fill=PANEL + "55", lw=MID)
    text(ax, W / 2, y + 11, title, FONT.BODY, "bold")


def report(fig, name):
    fig.canvas.draw()
    r = fig.canvas.get_renderer()
    for t, x, w in _checks:
        if t.figure is not fig:
            continue
        inv = t.axes.transData.inverted()
        bb = t.get_window_extent(r)
        (x0, _), (x1, _) = inv.transform((bb.x0, bb.y0)), inv.transform((bb.x1, bb.y1))
        if x0 < x + 2 or x1 > x + w - 2:
            print(f"  넘침 {name}: {t.get_text()!r} 폭 {x1 - x0:.0f} > 상자 {w}")


def finish(fig, name):
    report(fig, name)
    save_figure(fig, name, source_dir=HERE, formats=("png",), width="text")
    plt.close(fig)


# ── 1. 무엇이 바뀌었나 ──────────────────────────────────────────────────
def overview():
    fig, ax = canvas(300)
    head = [
        (T("① 첫 설치 때 기본 등록", "① A first install registers"),
         T("터미널 설치만. --no-service로 제외", "From a terminal; --no-service skips it")),
        (T("② 업데이트는 등록 상태 유지", "② Upgrades keep registration"),
         T("실행 중인 moai 서비스만 재시작", "Only moai's running service restarts")),
        (T("③ 서비스 파일로 등록 여부 판단", "③ The service file is the state"),
         T("moai가 만든 파일만 수정, 삭제", "moai changes only files it wrote")),
    ]
    for x, (a, b) in zip([4, 172, 340], head):
        box(ax, x, 2, 160, 40, [(a, FONT.BODY, "bold"), (b, FONT.TICK)], lw=MID)

    panel(ax, 50, 178, T("(a) 서비스 등록 경로: Linux, macOS (신규)", "(a) How the service is registered: Linux and macOS (new)"))
    c1, c2, c3, h = 94, 138, 184, 36
    ex, ew, axx, aw, sx, sw, ox, ow = 12, 92, 128, 120, 274, 90, 388, 110
    box(ax, ex, c1 - h / 2, ew, h, ["install.sh", T("첫 설치 마지막에", "end of a first install")])
    box(ax, ex, c2 - h / 2, ew, h, [T("사용자", "You"), T("직접 실행", "by hand")])
    box(ax, ex, c3 - h / 2, ew, h, ["moai update", T("새 버전 설치 후", "after installing")])
    new(ax, axx, c1 - h / 2, aw, h, ["moai daemon install", T("등록하고 바로 시작", "register, start now")])
    new(ax, axx, c2 - h / 2, aw, h, ["moai daemon uninstall", T("중지하고 파일 삭제", "stop, remove the file")])
    new(ax, axx, c3 - h / 2, aw, h, [T("서비스 재시작", "Restart the service"),
                                     T("조건을 모두 만족할 때만", "only when every check holds")])
    route(ax, [(ex + ew, c1), (axx, c1)])
    route(ax, [(ex + ew, c2), (axx, c2)])
    route(ax, [(116, c2), (116, c1 + 10), (axx, c1 + 10)])
    route(ax, [(ex + ew, c3), (axx, c3)])
    top, bot = c1 - h / 2, c3 + h / 2
    box(ax, sx, top, sw, bot - top, [("service.rs", FONT.TICK, "bold"),
                                     T("서비스 파일 작성", "writes the file"),
                                     T("systemctl, launchctl 실행", "calls the manager")])
    for c in (c1, c2, c3):
        route(ax, [(axx + aw, c), (sx, c)])
    box(ax, ox, c1 - h / 2, ow, h, [("Linux: systemd", FONT.TICK, "bold"), "~/.config/systemd/user/", "moai-daemon.service"])
    box(ax, ox, c2 - h / 2, ow, h, [("macOS: launchd", FONT.TICK, "bold"), "~/Library/LaunchAgents/",
                                    "com.buzzni.moai-daemon.plist"])
    box(ax, ox, c3 - h / 2, ow, h, [("Windows", FONT.TICK, "bold"), T("이 PR에 미포함", "not in this PR")],
        ls=DASH.RULE, ec=RED, lw=MID, color=RED)
    route(ax, [(sx + sw, c1), (ox, c1)])
    route(ax, [(sx + sw, c2), (ox, c2)])
    route(ax, [(sx + sw, c3), (ox, c3)], ls=DASH.RULE, color=RED)
    text(ax, W / 2, 216, T("로그인하면 서비스 관리자가 moai daemon start를 실행합니다. 서비스는 셸과 같은 소켓 경로를 씁니다.",
                           "At login the service manager runs moai daemon start, which uses the same socket directory as your shell."),
         FONT.TICK)

    panel(ax, 236, 62, T("(b) 바뀌지 않는 것", "(b) What stays the same"))
    keep = [
        (T("CLI 명령", "CLI commands"), T("데몬을 호출하지 않음", "never call the daemon")),
        (T("터미널이 아닌 설치", "Install without a terminal"), T("등록 안 함, 출력 동일", "no service, same output")),
        (T("서비스 없는 moai update", "moai update, no service"), T("추가 동작 없음, 출력 동일", "no manager call, same output")),
        ("install.ps1, Windows", T("등록 안 함 (이 PR에 미포함)", "registers nothing")),
    ]
    for x, (a, b) in zip([12, 134, 256, 378], keep):
        red = a.startswith("install.ps1")
        box(ax, x, 258, 116, 32, [a, b], ec=RED if red else INK, color=RED if red else INK)
    finish(fig, "01-overview")


# ── 2. 첫 설치 ──────────────────────────────────────────────────────────
def first_install():
    fig, ax = canvas(252)
    panel(ax, 2, 108, T("(a) install.sh: 첫 설치 마지막에 등록 여부 결정", "(a) install.sh decides at the end of a first install"))
    box(ax, 12, 46, 80, 36, ["install.sh", T("moai 설치 완료", "moai is in place")])
    route(ax, [(92, 64), (112, 64)])
    qx, qw = 112, 186
    box(ax, qx, 24, qw, 80, [
        (T("다섯 조건을 모두 만족하는가?", "Do all five hold?"), FONT.TICK, "bold"),
        T("① 첫 설치 (설치 경로에 moai가 없었음)", "① First install (no moai in that directory)"),
        T("② --no-service, MOAI_NO_SERVICE=1 없음", "② No --no-service, no MOAI_NO_SERVICE=1"),
        T("③ 표준 출력이 터미널", "③ Standard output is a terminal"),
        T("④ root가 아님", "④ Not root"),
        T("⑤ 설치한 버전에 daemon install 있음", "⑤ The release has daemon install"),
    ])
    fx = qx + qw
    route(ax, [(fx, 64), (306, 64), (306, 40), (338, 40)])
    route(ax, [(306, 64), (306, 84), (338, 84)], lw=THICK)
    text(ax, 322, 34, T("아니요", "No"), FONT.NOTE)
    text(ax, 322, 78, T("예", "Yes"), FONT.NOTE, "bold")
    box(ax, 338, 24, 160, 32, [T("등록하지 않고 설치 완료", "Install ends, no service"),
                              T("출력도 그대로 (root만 한 줄 안내)", "same output (one line for root)")])
    new(ax, 338, 66, 160, 36, [T("moai daemon install 실행", "Run moai daemon install"),
                               T("실패해도 설치는 성공 (한 줄 안내)", "a failure is one line; install succeeds")])

    panel(ax, 118, 132, T("(b) moai daemon install의 동작", "(b) What moai daemon install does"))
    xs, w, y, h = [10, 110, 210, 310, 410], 84, 144, 40
    steps = [
        [T("sudo가 아님", "Not under sudo"), T("root의 서비스가 되므로", "it would be root's")],
        [T("서비스 파일 확인", "Check the file"), T("없거나 moai가 만든 파일", "none, or moai's own")],
        [T("파일 작성 (없을 때)", "Write it (if none)"), T("임시 파일에 쓴 뒤 교체", "temp file, then rename")],
        None,
        [T("최대 5초 대기", "Wait up to 5 s"), T("응답 확인 후 결과 출력", "report if it answers")],
    ]
    for i, s in enumerate(steps):
        if s:
            box(ax, xs[i], y, w, h, s)
    new(ax, xs[3], y, w, h, [T("서비스 관리자에 등록", "Hand to the manager"), "systemd: enable --now", "launchd: bootstrap"])
    for i in range(4):
        route(ax, [(xs[i] + w, y + h / 2), (xs[i + 1], y + h / 2)])
    fy = 206
    for i in (0, 1):
        route(ax, [(xs[i] + w / 2, y + h), (xs[i] + w / 2, fy)], ls=DASH.RULE)
    box(ax, 10, fy, 184, 34, [T("거부, 아무것도 바꾸지 않음", "Refuse and change nothing"),
                              T("sudo, 직접 작성한 파일, 다른 moai의 파일", "sudo, a hand-written file, another moai's")])
    cx = xs[3] + w / 2
    route(ax, [(cx, y + h), (cx, fy)], ls=DASH.RULE)
    box(ax, cx - 92, fy, 184, 34, [T("서비스 관리자가 거부하면", "If the manager refuses"),
                                   T("이번에 만든 파일만 삭제, service_failed", "remove a file written now; service_failed")])
    finish(fig, "02-first-install")


# ── 3. 업데이트 ─────────────────────────────────────────────────────────
def update():
    fig, ax = canvas(254)
    panel(ax, 2, 250, T("moai update: 등록된 서비스를 새 버전으로 재시작 (신규)",
                        "moai update: restart a registered service on the new version (new)"))
    xs, w = [10, 106, 202, 298], 84
    y1, h1 = 30, 40
    m1 = y1 + h1 / 2
    box(ax, xs[0], y1, w, h1, ["moai update", T("새 버전 내려받기", "fetch the release")])
    box(ax, xs[1], y1, w, h1, ["install.sh --force", T("등록 상태는 그대로", "registration unchanged")])
    box(ax, xs[2], y1, w, h1, [T("새 버전으로 상태 확인", "Ask the new binary"), "moai daemon status"])
    box(ax, xs[3], y1, w, h1, [T("다른 버전 데몬이", "Another version's"), T("실행 중인가?", "daemon running?")])
    for i in range(3):
        route(ax, [(xs[i] + w, m1), (xs[i + 1], m1)])
    ox, ow = 410, 84
    route(ax, [(xs[3] + w, m1), (ox, m1)])
    text(ax, 398, m1 - 7, T("아니요", "No"), FONT.NOTE)
    box(ax, ox, y1, ow, h1, [T("아무것도 안 함", "Do nothing"), T("출력은 기존과 같음", "same output as before")])

    y2, h2 = 98, 50
    m2 = y2 + h2 / 2
    cx = xs[3] + w / 2
    route(ax, [(cx, y1 + h1), (cx, y2)])
    text(ax, cx + 5, 84, T("예", "Yes"), FONT.NOTE, ha="left")
    box(ax, xs[3], y2, w, h2, [T("세 조건을 모두 만족?", "All three true?"),
                               T("moai가 만든 서비스 파일", "service file by moai"),
                               T("이 실행 파일을 가리킴", "names this binary"),
                               T("서비스가 실행 중", "service is running")])
    route(ax, [(xs[3] + w, m2), (ox, m2)])
    text(ax, 398, m2 - 7, T("아니요", "No"), FONT.NOTE)
    box(ax, ox, y2, ow, h2, [T("기존 안내 출력", "Print the notice"), T("직접 재시작하라는 안내", "restart it yourself"),
                             "daemon_restart: true"])

    y3 = 176
    route(ax, [(cx, y2 + h2), (cx, 162), (58, 162), (58, y3)], lw=THICK)
    text(ax, cx + 5, 156, T("예", "Yes"), FONT.NOTE, "bold", ha="left")
    new(ax, 10, y3, 96, 40, [T("서비스 재시작", "Restart the service"), "systemctl --user restart", "launchctl kickstart -k"])
    route(ax, [(106, y3 + 20), (124, y3 + 20)], lw=THICK)
    new(ax, 124, y3, 84, 40, [T("최대 5초 대기", "Wait up to 5 s"), T("새 버전이 응답하는가?", "does the new one answer?")])
    route(ax, [(208, y3 + 20), (220, y3 + 20), (220, y3 + 2), (234, y3 + 2)], lw=THICK)
    route(ax, [(220, y3 + 20), (220, y3 + 52), (234, y3 + 52)])
    new(ax, 234, y3 - 12, 140, 30, [T("응답함: 재시작 완료 안내", "Answered: says restarted"), "daemon_restarted: true"])
    box(ax, 234, y3 + 38, 140, 30, [T("응답 없음: 아직 응답 없음 안내", "No answer: says not yet"), "daemon_restart: true"])
    box(ax, 386, y3 - 12, 108, 80, [
        (T("이 경로에서 하지 않는 것", "Never on this path"), FONT.TICK, "bold"),
        T("등록 상태 변경", "a change of registration"),
        T("중지된 서비스 시작", "starting a stopped service"),
        T("직접 작성한 파일 재시작", "restarting a hand-written one"),
        T("종료 코드 변경", "a change of exit code"),
    ], ls=DASH.RULE)
    finish(fig, "03-update")


overview()
first_install()
update()
