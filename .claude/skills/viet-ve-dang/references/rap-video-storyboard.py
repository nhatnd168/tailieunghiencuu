#!/usr/bin/env python3
"""Assemble the 9:16 background video from the storyboard, then write Remotion caption props.
Usage: rap-video-storyboard.py <run-dir> <bg-out.mp4> <props-out.json> <video-name-for-remotion> [anh-dir-name]
Segment 0 = the 4:5 fanpage image for intro_sec (860 px wide, pinned top, navy around) so captions sit under it.
Segments n = VERTICAL 9:16 storyboard images (y-NN.png, 1080x1920) shown full-frame (cover crop).
TIMING (v2.8, Owner 11:1x 24/09/2026 "captions must match the audio"): if 40-video/dong-loi/loi-dong.json exists
(made by dong-loi-whisper.py from whisper word timestamps), every cue starts at the real start of its first word and
every image segment switches at the real start of its first word. Without that file: proportional-by-text fallback
(known to drift up to 4 s) — and the caller must say so in the log.
Captions: <=9 words per cue (balanced), two lines via CaptionOverVideoHigh. Requires ffmpeg on PATH.
"""
import json
import math
import os
import subprocess
import sys

run, bg_out, props_out, vid_name = sys.argv[1:5]
anh_dir = sys.argv[5] if len(sys.argv) > 5 else "anh-9x16"
V = os.path.join(run, "40-video")
A = os.path.join(V, anh_dir)
sb = json.load(open(os.path.join(A, "storyboard.json"), encoding="utf-8"))
img45 = os.path.join(run, "30-anh", "anh-4x5.png")
NAVY = "#0b1a33"
FPS = 30
INTRO = float(sb["intro_sec"])
tmp = os.path.join(V, "doan")
os.makedirs(tmp, exist_ok=True)

# ---------- timing source ----------
dong_path = os.environ.get("VVD_DONG") or os.path.join(V, "dong-loi", "loi-dong.json")
timed_words = None
if os.path.isfile(dong_path):
    dong = json.load(open(dong_path, encoding="utf-8"))
    seg_counts = [len(s["text"].split()) for s in sb["segments"]]
    if sum(seg_counts) == len(dong["words"]):
        timed_words = dong["words"]
        audio_end = float(dong.get("audio_end") or timed_words[-1]["end"])
        pos = 0
        for s, n in zip(sb["segments"], seg_counts):
            s["_words"] = timed_words[pos:pos + n]
            pos += n
        # image boundaries at the real start of each segment's first word
        for k, s in enumerate(sb["segments"]):
            first = s["_words"][0]["start"]
            s["start"] = INTRO if k == 0 else first
        for k, s in enumerate(sb["segments"]):
            nxt = sb["segments"][k + 1]["start"] if k + 1 < len(sb["segments"]) else max(audio_end + 0.3, s["_words"][-1]["end"] + 0.3)
            s["dur"] = round(nxt - s["start"], 3)
        sb["total_sec"] = round(sb["segments"][-1]["start"] + sb["segments"][-1]["dur"], 3)
        sb["timing"] = "dong-loi-whisper"
        json.dump({k: v for k, v in sb.items()} | {"segments": [{k: v for k, v in s.items() if k != "_words"} for s in sb["segments"]]},
                  open(os.path.join(A, "storyboard-dong.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    else:
        print(f"CANH BAO: số từ storyboard {sum(seg_counts)} khác số từ dóng lời {len(dong['words'])} — dùng chia đều theo chữ")
if timed_words is None:
    sb["timing"] = "chia-deu-theo-chu (LECH toi 4s — chi dung khi khong co dong-loi)"


def seg(src, dur, out, mode):
    if mode == "4x5":
        # intro image shrunk to 860 px wide and pinned near the top so the raised caption block
        # (bottom edge at 1920-560) sits BELOW the image instead of over its footer
        vf = f"scale=860:-2,pad=1080:1920:110:40:color={NAVY},format=yuv420p"
    else:  # 9x16 full-frame cover
        vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920,format=yuv420p"
    subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-loop", "1", "-i", src, "-t", f"{dur:.3f}", "-r", str(FPS),
                    "-vf", vf, "-pix_fmt", "yuv420p", out], check=True)


parts = []
seg(img45, INTRO, os.path.join(tmp, "d00.mp4"), "4x5")
parts.append(os.path.join(tmp, "d00.mp4"))
missing = []
for s in sb["segments"]:
    src = os.path.join(A, s["file"])
    mode = "9x16"
    if not os.path.isfile(src):
        missing.append(s["file"])
        src, mode = img45, "4x5"
    out = os.path.join(tmp, f"d{s['n']:02d}.mp4")
    seg(src, s["dur"], out, mode)
    parts.append(out)
lst = os.path.join(tmp, "list.txt")
with open(lst, "w", encoding="utf-8") as f:
    for p in parts:
        f.write(f"file '{p}'\n")
subprocess.run(["ffmpeg", "-loglevel", "error", "-y", "-f", "concat", "-safe", "0", "-i", lst, "-c", "copy", bg_out], check=True)

# ---------- cues ----------
cues = []


def chunks_of(words):
    # <=9 words per cue, BALANCED so the last cue is never a lone word
    n_chunks = max(1, math.ceil(len(words) / 9))
    size = math.ceil(len(words) / n_chunks) if words else 0
    return [words[i:i + size] for i in range(0, len(words), size)] if words else [[]]


if timed_words is not None:
    for k, s in enumerate(sb["segments"]):
        seg_end = s["start"] + s["dur"] if k > 0 else sb["segments"][1]["start"] if len(sb["segments"]) > 1 else s["start"] + s["dur"]
        ch = chunks_of(s["_words"])
        for ci, c in enumerate(ch):
            t0 = 0.0 if (k == 0 and ci == 0) else c[0]["start"]
            t1 = ch[ci + 1][0]["start"] if ci + 1 < len(ch) else seg_end
            f0, f1 = int(t0 * FPS), int(t1 * FPS)
            cues.append({"from": f0, "to": max(f1, f0 + 1),
                         "words": [{"text": w["word"], "hot": i == 0, "reveal": max(0, min(int((w["start"] - t0) * FPS), max(f1 - f0 - 1, 0)))}
                                   for i, w in enumerate(c)]})
else:
    def add_cues(text, start, dur):
        ch = chunks_of(text.split())
        per = dur / len(ch)
        t = start
        for c in ch:
            f0, f1 = int(t * FPS), int((t + per) * FPS)
            cues.append({"from": f0, "to": max(f1, f0 + 1),
                         "words": [{"text": w, "hot": i == 0, "reveal": min(i * 3, max(f1 - f0 - 1, 0))} for i, w in enumerate(c)]})
            t += per
    first = sb["segments"][0]
    add_cues(first["text"], 0.0, first["start"] + first["dur"])
    for s in sb["segments"][1:]:
        add_cues(s["text"], s["start"], s["dur"])

frames = int(math.ceil(sb["total_sec"] * FPS))
top_line = sb.get("top_line") or os.environ.get("VVD_TOP_LINE", "")
bottom_pad = int(sb.get("bottom_pad") or os.environ.get("VVD_BOTTOM_PAD", "560"))
json.dump({"video": vid_name, "cues": cues, "durationInFrames": frames, "topLine": top_line, "bottomPad": bottom_pad, "fontSize": 54},
          open(props_out, "w", encoding="utf-8"), ensure_ascii=False)
print(f"nền {bg_out} · đoạn {len(parts)} · thiếu ảnh thay bằng 4:5: {missing or 'không'} · cue {len(cues)} · khung {frames} · timing {sb['timing']} · dòng trên: {top_line or '(trống)'} · bottomPad {bottom_pad}")
