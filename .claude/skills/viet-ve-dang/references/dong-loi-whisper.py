#!/usr/bin/env python3
"""Align the narration SCRIPT (loi-doc.txt) to whisper word timestamps (loi.json) -> loi-dong.json.
Usage: dong-loi-whisper.py <loi-doc.txt> <whisper-loi.json> <out loi-dong.json>
Every script word gets start/end seconds: matched words take whisper times, unmatched words are
interpolated between their matched neighbours. Prints matched ratio; exit 3 if < 0.6 (alignment unusable).
Run whisper first:  whisper loi.mp3 --language vi --model small --word_timestamps True --output_format json --output_dir dong-loi --fp16 False
"""
import difflib, json, re, sys

script_path, whisper_path, out_path = sys.argv[1:4]
norm = lambda w: re.sub(r"[^\w]+", "", w.lower())
script = open(script_path, encoding="utf-8").read().split()
d = json.load(open(whisper_path, encoding="utf-8"))
ww = [w for s in d["segments"] for w in s.get("words", [])]
a = [norm(w) for w in script]
b = [norm(w["word"]) for w in ww]
sm = difflib.SequenceMatcher(None, a, b, autojunk=False)
start = [None] * len(script); end = [None] * len(script); matched = [False] * len(script)
for i, j, n in sm.get_matching_blocks():
    for k in range(n):
        start[i + k] = float(ww[j + k]["start"]); end[i + k] = float(ww[j + k]["end"]); matched[i + k] = True
# interpolate gaps
total_end = float(ww[-1]["end"]) if ww else 0.0
idx = [i for i in range(len(script)) if matched[i]]
if not idx:
    print("KHONG khop duoc tu nao"); sys.exit(3)
prev_i = None
for i in range(len(script)):
    if matched[i]:
        prev_i = i; continue
    # find next matched
    nxt = next((k for k in range(i + 1, len(script)) if matched[k]), None)
    t0 = end[prev_i] if prev_i is not None else 0.0
    t1 = start[nxt] if nxt is not None else total_end
    gap_words = (nxt if nxt is not None else len(script)) - (prev_i + 1 if prev_i is not None else 0)
    pos = i - (prev_i + 1 if prev_i is not None else 0)
    step = (t1 - t0) / max(gap_words, 1)
    start[i] = t0 + step * pos; end[i] = t0 + step * (pos + 1)
    prev_i = prev_i  # keep
words = [{"i": i, "word": script[i], "start": round(start[i], 3), "end": round(end[i], 3), "matched": matched[i]} for i in range(len(script))]
# monotonic fix
for i in range(1, len(words)):
    if words[i]["start"] < words[i - 1]["start"]:
        words[i]["start"] = words[i - 1]["start"]
    if words[i]["end"] < words[i]["start"]:
        words[i]["end"] = words[i]["start"] + 0.05
ratio = sum(matched) / len(script)
json.dump({"words": words, "matched_ratio": round(ratio, 3), "audio_end": total_end}, open(out_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(f"script {len(script)} từ · whisper {len(ww)} từ · khớp {sum(matched)}/{len(script)} = {ratio:.0%} · tiếng kết {total_end:.2f}s")
if ratio < 0.6:
    print("DONG LOI KHONG DUNG DUOC (khớp < 60%) — dùng chia đều theo chữ và BÁO"); sys.exit(3)
