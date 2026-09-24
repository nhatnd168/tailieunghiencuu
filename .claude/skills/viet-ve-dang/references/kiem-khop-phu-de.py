#!/usr/bin/env python3
"""GATE: do captions match the narration timing?  Usage: kiem-khop-phu-de.py <props.json> <loi-dong.json> [max_offset_s=0.5]
For each cue, the expected on-screen moment is the START of its first word in the aligned narration.
Reports the offset (cue start - word start) per cue; FAIL (exit 4) if any |offset| > max_offset.
Cue words are matched to script words in order (normalised), so the same script must feed both files.
"""
import json, re, sys
FPS = 30
props = json.load(open(sys.argv[1], encoding="utf-8"))
dong = json.load(open(sys.argv[2], encoding="utf-8"))["words"]
tol = float(sys.argv[3]) if len(sys.argv) > 3 else 0.5
norm = lambda w: re.sub(r"[^\w]+", "", w.lower())
script = [norm(w["word"]) for w in dong]
pos = 0; worst = 0.0; bad = 0; rows = []
for c in props["cues"]:
    cw = [norm(w["text"]) for w in c["words"]]
    # find the first cue word at/after pos
    k = None
    for p in range(pos, len(script)):
        if script[p] == cw[0] and script[p:p + len(cw)] == cw:
            k = p; break
    if k is None:
        rows.append((c["from"] / FPS, None, None, " ".join(w["text"] for w in c["words"])[:40])); bad += 1; continue
    exp = dong[k]["start"]; got = c["from"] / FPS; off = got - exp
    worst = max(worst, abs(off))
    if abs(off) > tol: bad += 1
    rows.append((got, exp, off, " ".join(w["text"] for w in c["words"])[:40]))
    pos = k + len(cw)
for got, exp, off, txt in rows:
    if exp is None:
        print(f"  {got:6.2f}s  KHÔNG tìm thấy trong lời  | {txt}")
    else:
        flag = "  " if abs(off) <= tol else "🔴"
        print(f"{flag}{got:6.2f}s  tiếng {exp:6.2f}s  lệch {off:+5.2f}s | {txt}")
print(f"cue {len(rows)} · lệch lớn nhất {worst:.2f}s · quá {tol}s: {bad}")
if bad:
    print("KHÔNG KHỚP — không đăng, không gửi"); sys.exit(4)
print("KHỚP")
