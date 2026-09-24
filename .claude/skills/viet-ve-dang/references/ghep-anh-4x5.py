#!/usr/bin/env python3
"""Compose a Zoom screenshot into a 4:5 (1080x1350) Facebook image.
Usage: ghep-anh-4x5.py <screenshot> <out.png> --tieu-de "..." --dong-duoi "..." [--cat-chat] [--tac-gia NAME]
Adds a sub-headline with the composition timestamp and a small author credit at the bottom-left
(Owner 09:3x 24/09/2026). Default KEEPS the whole screenshot including the Zoom chat column with student comments
(Owner 11:4x 24/09/2026: "ưu tiên giữ hình chụp màn hình gốc có cả comment của học viên"); --cat-chat crops the right 28 %.
"""
import argparse
import datetime
import zoneinfo
from PIL import Image, ImageDraw, ImageFont

NAVY = (11, 26, 51)
GOLD = (230, 177, 69)
CREAM = (245, 240, 230)
GREY = (170, 176, 190)


def font(size, bold=True):
    paths = [
        "/System/Library/Fonts/Supplemental/Arial Bold.ttf" if bold else "/System/Library/Fonts/Supplemental/Arial.ttf",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            pass
    return ImageFont.load_default()


def wrap(draw, text, f, maxw):
    lines, cur = [], ""
    for w in text.split():
        t = (cur + " " + w).strip()
        if draw.textlength(t, font=f) <= maxw:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


ap = argparse.ArgumentParser()
ap.add_argument("src")
ap.add_argument("out")
ap.add_argument("--tieu-de", default="BÍ MẬT AI · BUỔI 1")
ap.add_argument("--dong-duoi", default="")
ap.add_argument("--cat-chat", action="store_true", help="crop the right-hand chat panel (old default before 11:4x 24/09)")
ap.add_argument("--giu-chat", action="store_true", help="kept for old commands; keeping the chat is now the default")
ap.add_argument("--tac-gia", default="trợ lý AI · skill viet-ve-dang")
a = ap.parse_args()

now_vn = datetime.datetime.now(zoneinfo.ZoneInfo("Asia/Ho_Chi_Minh"))
now_uk = datetime.datetime.now(zoneinfo.ZoneInfo("Europe/London"))
stamp = f"Ghép lúc {now_vn:%H:%M %d/%m/%Y} giờ VN ({now_uk:%H:%M} London)"

im = Image.open(a.src).convert("RGB")
W, H = im.size
if a.cat_chat and W > H:
    # Zoom layout: the chat panel occupies roughly the right 28% of the frame; crop it out.
    im = im.crop((0, 0, int(W * 0.72), H))

canvas = Image.new("RGB", (1080, 1350), NAVY)
d = ImageDraw.Draw(canvas)

# title band + timestamp sub-headline
f_t = font(54)
y = 60
for ln in wrap(d, a.tieu_de, f_t, 1000):
    d.text(((1080 - d.textlength(ln, font=f_t)) // 2, y), ln, font=f_t, fill=GOLD)
    y += 66
f_sub = font(30, False)
d.text(((1080 - d.textlength(stamp, font=f_sub)) // 2, y), stamp, font=f_sub, fill=GREY)
y += 44
d.line((90, y + 4, 990, y + 4), fill=GOLD, width=3)
y += 34

# screenshot fitted to width 1000 inside a thin gold frame
sw = 1000
sh = int(im.height * sw / im.width)
if sh > 720:
    sh = 720
    sw = int(im.width * sh / im.height)
shot = im.resize((sw, sh))
x = (1080 - sw) // 2
d.rectangle((x - 6, y - 6, x + sw + 6, y + sh + 6), outline=GOLD, width=3)
canvas.paste(shot, (x, y))
y += sh + 36

# bottom hook (up to three lines)
if a.dong_duoi:
    f_b = font(42)
    for ln in wrap(d, a.dong_duoi, f_b, 980)[:3]:
        d.text(((1080 - d.textlength(ln, font=f_b)) // 2, y), ln, font=f_b, fill=CREAM)
        y += 56

# footer: author credit bottom-left, signature bottom-right
f_s = font(24, False)
d.text((60, 1350 - 52), f"ghép hình: {a.tac_gia}", font=f_s, fill=GREY)
f_sig = font(30, False)
sig = "@Eroca Thanh"
d.text((1080 - d.textlength(sig, font=f_sig) - 60, 1350 - 58), sig, font=f_sig, fill=GOLD)
canvas.save(a.out, "PNG")
print(a.out, canvas.size, stamp)
