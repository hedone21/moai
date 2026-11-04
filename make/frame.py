#!/usr/bin/env python3
"""Put terminal stills in a window frame like the homepage's, and stack several into one picture.

    frame.py -o out.png 'Title one' one.png ['Title two' two.png ...]

Empty rows at the bottom of a still are cropped. The colours are those of site/assets/site.css (.window).
"""
import subprocess, sys
from PIL import Image, ImageDraw, ImageFont

BG = (18, 18, 18)          # the terminal (#121212)
WINDOW = (10, 11, 10)      # .window
BAR = (24, 26, 24)         # .window .bar
LINE = (44, 48, 44)        # border
DOT = (44, 48, 44)
TITLE = (150, 147, 140)
SCALE = 1
PAD = 14                   # inside the window, left, right and bottom of the terminal
PAD_TOP = 2                # agg leaves its own margin above the first row
BAR_H = 38
GAP = 22                   # between stacked windows
MARGIN = 0


def font(size):
    path = subprocess.run(['fc-match', '-f', '%{file}', 'Noto Sans:medium'], capture_output=True, text=True).stdout
    return ImageFont.truetype(path, size)


def crop(img):
    px = img.convert('RGB').load()
    w, h = img.size
    last = 0
    for y in range(h):
        if any(px[x, y] != BG for x in range(0, w, 2)):
            last = y
    return img.crop((0, 0, w, min(h, last + 12)))


def window(title, path):
    term = crop(Image.open(path).convert('RGB'))
    w, h = term.size[0] + 2 * PAD, term.size[1] + BAR_H + PAD_TOP + PAD
    img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.rounded_rectangle((0, 0, w - 1, h - 1), radius=12, fill=BG, outline=LINE)
    d.rounded_rectangle((0, 0, w - 1, BAR_H), radius=12, fill=BAR, outline=LINE)
    d.rectangle((1, BAR_H - 12, w - 2, BAR_H - 1), fill=BAR)
    d.line((0, BAR_H, w - 1, BAR_H), fill=LINE)
    for i in range(3):
        cx, cy = 22 + i * 19, BAR_H // 2
        d.ellipse((cx - 6, cy - 6, cx + 6, cy + 6), fill=DOT)
    f = font(15)
    tw = d.textlength(title, font=f)
    d.text(((w - tw) / 2, BAR_H / 2), title, font=f, fill=TITLE, anchor='lm')
    img.paste(term, (PAD, BAR_H + PAD_TOP))
    return img


def main():
    args = sys.argv[1:]
    if len(args) < 4 or args[0] != '-o' or len(args[2:]) % 2:
        raise SystemExit(__doc__)
    out, pairs = args[1], args[2:]
    wins = [window(pairs[i], pairs[i + 1]) for i in range(0, len(pairs), 2)]
    w = max(x.size[0] for x in wins) + 2 * MARGIN
    h = sum(x.size[1] for x in wins) + GAP * (len(wins) - 1) + 2 * MARGIN
    canvas = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    y = MARGIN
    for x in wins:
        canvas.paste(x, (MARGIN, y), x)
        y += x.size[1] + GAP
    canvas.save(out, optimize=True)


if __name__ == '__main__':
    main()
