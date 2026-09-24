#!/usr/bin/env python3
"""AUDIT the published post of a viet-ve-dang run against the Owner's public-writing rules.
Usage: audit-bai-viet.py <run-dir> [--out DIR] [--luat FILE] [--khong-hermes] [--ghe NAME]
Reads  20-bai/content.md · 50-dang/posted.json · 50-dang/youtube-log*.txt
Writes <out>/AUDIT-<stamp>.md / .html / .pdf / .json   (PDF via headless Chrome, fallback LibreOffice)
Owner 12:2x 24/09/2026: after the links are delivered, "thanh tra"/"audit" (or 10 min of silence) triggers this.
Deterministic checks are the verdict; the Hermes voice review (rule 6) is advisory and clearly labelled.
"""
import argparse, datetime, hashlib, json, os, re, subprocess, sys, glob, html

ap = argparse.ArgumentParser()
ap.add_argument("run"); ap.add_argument("--out"); ap.add_argument("--luat", default=os.path.expanduser("~/Operations/luat-viet/LUAT-VIET-BAI-CONG-KHAI.md"))
ap.add_argument("--khong-hermes", action="store_true"); ap.add_argument("--ghe", default="trợ lý AI")
a = ap.parse_args()
R = os.path.abspath(a.run); OUT = a.out or os.path.join(R, "60-audit"); os.makedirs(OUT, exist_ok=True)
STAMP = datetime.datetime.now().strftime("%m%d%H%M")
NOW_VN = (datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(hours=7)).strftime("%H:%M %d/%m/%Y")
NOW_LDN = subprocess.run(["bash", "-c", "TZ=Europe/London date '+%H:%M %d/%m/%Y'"], capture_output=True, text=True).stdout.strip()

raw = open(os.path.join(R, "20-bai", "content.md"), encoding="utf-8").read()
body = re.sub(r"^---.*?---\s*", "", raw, flags=re.S).strip()           # drop front-matter
md5 = hashlib.md5(body.encode()).hexdigest()[:12]
lines = [l for l in body.splitlines()]
words = body.split(); sents = [s for s in re.split(r"[.!?…]+\s", body) if s.strip()]

def find(pat, flags=re.I):
    return [(i + 1, l.strip()) for i, l in enumerate(lines) if re.search(pat, l, flags)]

checks = []
def add(code, name, status, evidence, note=""):
    checks.append({"code": code, "name": name, "status": status, "evidence": evidence, "note": note})

# L1 public naming — internal course codes must not appear
hits = find(r"\b(Cohort\s*Alpha|K\d{1,2}|cohort)\b")
add("1", "Tên gọi công khai (không «Cohort Alpha», không mã K+số)", "ĐẠT" if not hits else "KHÔNG ĐẠT", hits or ["không thấy mã nội bộ"])
# L2 self reference
thanh = len(re.findall(r"\bThanh\b", body)); em = find(r"(^|[\s,.!?:;(«\"'])[Ee]m\s")
add("2", "Tự xưng «Thanh», không xưng «Em»", "ĐẠT" if thanh and not em else ("CẦN NGƯỜI NHÌN" if em else "KHÔNG ĐẠT"), [f"«Thanh» {thanh} lần"] + em, "«em» có thể là lời gọi máy, người đọc quyết")
# L3 signature
sig = "— Eroca Thanh" in body or "- Eroca Thanh" in body
add("3", "Ký tên «— Eroca Thanh»", "ĐẠT" if sig else "THÔNG TIN", ["có chữ ký" if sig else "không có chữ ký (luật ghi cho email; bài fanpage không bắt buộc)"])
# L4 addressing: written text -> «bạn», not «anh chị»
ban = len(re.findall(r"\bbạn\b", body, re.I)); anhchi = find(r"\banh\s*/?\s*chị\b|\bcác bạn\b")
add("4", "Gọi người đọc: văn bản viết dùng «bạn» 100 %", "ĐẠT" if ban and not anhchi else "KHÔNG ĐẠT", [f"«bạn» {ban} lần"] + (anhchi or []))
# L5 no tables
tbl = find(r"^\s*\|")
add("5", "Không dùng bảng", "ĐẠT" if not tbl else "KHÔNG ĐẠT", tbl or ["0 dòng bảng"])
# forbidden prohibition symbol
sym = body.count(chr(0x26D4))
add("K", "Không dùng ký hiệu cấm thay chữ «không»", "ĐẠT" if not sym else "KHÔNG ĐẠT", [f"{sym} ký hiệu"])
# anti-LLM watermark vocab (advisory, not hard)
vocab = ["kiến trúc", "framework", "deep dive", "audit-self", "context", "workflow", "trí tuệ nhân tạo", "tối ưu hoá", "tối ưu hóa", "hành trình", "khai phá"]
vh = [(w, len(re.findall(re.escape(w), body, re.I))) for w in vocab]; vh = [f"«{w}» {n}" for w, n in vh if n]
add("V", "Từ nên tránh khi có từ Việt thông dụng hơn (không cấm cứng)", "ĐẠT" if not vh else "CẦN NGƯỜI NHÌN", vh or ["không gặp"])
# CTA + links
cta = find(r"bình luận|comment|email")
add("C", "Có lời mời hành động (CTA)", "ĐẠT" if cta else "THÔNG TIN", cta or ["không thấy CTA"])

links = {}
try:
    pj = json.load(open(os.path.join(R, "50-dang", "posted.json"), encoding="utf-8"))
    pid = (pj.get("response") or {}).get("post_id") or pj.get("post_id")
    if pid: links["fanpage"] = f"https://www.facebook.com/{pid.split('_')[0]}/posts/{pid.split('_')[-1]}"
    links["fanpage_target"] = pj.get("target", ""); links["posted_at"] = pj.get("posted_at", "")
except Exception as e:
    links["fanpage"] = f"(không đọc được posted.json: {type(e).__name__})"
yl = sorted(glob.glob(os.path.join(R, "50-dang", "youtube-log*.txt")), key=os.path.getmtime)
for f in reversed(yl):
    m = re.search(r"url=(https?://\S+)", open(f, encoding="utf-8", errors="ignore").read())
    if m: links["youtube"] = m.group(1); break

hard_fail = [c for c in checks if c["status"] == "KHÔNG ĐẠT"]; look = [c for c in checks if c["status"] == "CẦN NGƯỜI NHÌN"]
verdict = "ĐẠT" if not hard_fail else "CẦN SỬA"

# Rule 6 — voice, advisory via Hermes (time-boxed), never blocks the report
voice = {"status": "chưa chấm máy", "text": ""}
if not a.khong_hermes:
    prompt = ("Bạn là người soi giọng viết cho Eroca Thanh. Chấm BÀI dưới đây theo giọng gốc: điềm đạm, tâm sự một-một, tiếng Việt dễ hiểu, "
              "tự xưng «Thanh», gọi người đọc «bạn», không hô hào, không từ sáo. Trả lời ĐÚNG khuôn 4 dòng, không thêm gì khác:\n"
              "DIEM: <số 1-10>\nKHEN: <một câu>\nSUA: <một câu nêu chỗ nên sửa, hoặc «không»>\nVIET-LAI: <một câu trong bài viết lại cho đúng giọng hơn, hoặc «không»>\n\nBÀI:\n" + body)
    try:
        p = subprocess.run([os.path.expanduser("~/.local/bin/hermes"), "-p", "marketer", "chat", "-q", prompt], capture_output=True, text=True, timeout=90)
        out = p.stdout
        # Hermes echoes the prompt, so the FIRST "DIEM:" block is our own template; take the last block without "<"
        blocks = [b for b in re.findall(r"DIEM:.*?VIET-LAI:[^\n]*", out, re.S) if "<số" not in b and "<một" not in b]
        voice = {"status": "Hermes marketer (gpt-6-astra) chấm, tham khảo", "text": (blocks[-1] if blocks else "(Hermes không trả đúng khuôn 4 dòng — người đọc tự chấm)").strip()}
    except subprocess.TimeoutExpired:
        voice = {"status": "Hermes không trả lời trong 90 giây — bỏ qua phần giọng, người đọc tự chấm", "text": ""}
    except Exception as e:
        voice = {"status": f"không gọi được Hermes ({type(e).__name__}) — người đọc tự chấm", "text": ""}

stats = {"ky_tu": len(body), "tu": len(words), "cau": len(sents), "dong": len([l for l in lines if l.strip()]), "dong_dai_nhat": max((len(l) for l in lines), default=0)}
rep = {"stamp": STAMP, "run": R, "content_md5": md5, "verdict": verdict, "checks": checks, "voice": voice, "links": links, "stats": stats, "luat": a.luat, "ghe": a.ghe, "gio_vn": NOW_VN, "gio_london": NOW_LDN}
json.dump(rep, open(os.path.join(OUT, f"AUDIT-{STAMP}.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)

# Markdown
md = [f"# BÁO CÁO THANH TRA BÀI ĐĂNG — {verdict}", f"Lượt: `{os.path.basename(R)}` · bài md5 `{md5}` · soi lúc {NOW_VN} giờ VN ({NOW_LDN} London) · ghế: {a.ghe}", f"Luật soi: `{a.luat}`", ""]
md.append("## Kết luận"); md.append(f"**{verdict}** — {len(hard_fail)} luật không đạt · {len(look)} chỗ cần người nhìn · {len(checks)-len(hard_fail)-len(look)} đạt/thông tin"); md.append("")
md.append("## Từng luật")
for c in checks:
    md.append(f"- **[{c['status']}] Luật {c['code']} — {c['name']}**"); [md.append(f"  - {e if isinstance(e,str) else f'dòng {e[0]}: {e[1]}'}") for e in c["evidence"]]
    if c["note"]: md.append(f"  - ghi chú: {c['note']}")
md += ["", "## Luật 6 — Giọng gốc (tham khảo)", f"_{voice['status']}_", "", voice["text"] or "(trống)", "", "## Đường dẫn đã đăng"] + [f"- {k}: {v}" for k, v in links.items()]
md += ["", "## Số đo", ", ".join(f"{k} {v}" for k, v in stats.items()), "", "## Bài đã đăng (nguyên văn)", "", "```", body, "```"]
open(os.path.join(OUT, f"AUDIT-{STAMP}.md"), "w", encoding="utf-8").write("\n".join(md))

# HTML (brand: navy · gold · cream) -> PDF
col = {"ĐẠT": "#1f8a4c", "KHÔNG ĐẠT": "#c0392b", "CẦN NGƯỜI NHÌN": "#b7791f", "THÔNG TIN": "#5a6b7d"}
def card(c):
    ev = "".join(f"<li>{html.escape(e if isinstance(e,str) else f'dòng {e[0]}: {e[1]}')}</li>" for e in c["evidence"])
    note = f"<div class='note'>{html.escape(c['note'])}</div>" if c["note"] else ""
    return f"<div class='card'><div class='badge' style='background:{col[c['status']]}'>{c['status']}</div><div class='ttl'>Luật {c['code']} · {html.escape(c['name'])}</div><ul>{ev}</ul>{note}</div>"
H = f"""<!doctype html><html lang="vi"><head><meta charset="utf-8"><title>Thanh tra bài đăng</title><style>
@page{{size:A4;margin:16mm}} body{{font-family:-apple-system,'Helvetica Neue',Arial,sans-serif;color:#0b1a33;background:#fff;margin:0}}
.hdr{{background:#0b1a33;color:#fff;padding:22px 26px;border-bottom:5px solid #e6b145}} .hdr h1{{margin:0;font-size:24px;letter-spacing:.5px}} .hdr .sub{{color:#e6b145;margin-top:6px;font-size:13px}}
.verdict{{display:inline-block;margin:18px 26px 0;padding:10px 18px;border-radius:8px;color:#fff;font-weight:800;font-size:20px;background:{'#1f8a4c' if verdict=='ĐẠT' else '#c0392b'}}}
.sum{{margin:8px 26px 0;font-size:14px;color:#3b4a5c}} h2{{margin:22px 26px 8px;font-size:16px;color:#0b1a33;border-left:5px solid #e6b145;padding-left:10px}}
.card{{margin:8px 26px;padding:10px 14px;border:1px solid #e3e8ef;border-radius:8px;background:#fbf8f1;page-break-inside:avoid}} .badge{{display:inline-block;color:#fff;font-size:11px;font-weight:700;padding:3px 8px;border-radius:5px;margin-bottom:4px}}
.ttl{{font-weight:700;font-size:14px}} .card ul{{margin:6px 0 0 18px;font-size:12.5px;color:#3b4a5c}} .note{{font-size:12px;color:#7a5c1e;margin-top:4px}}
.voice{{margin:8px 26px;padding:12px 14px;border-radius:8px;background:#f1f4f8;font-size:13px;white-space:pre-wrap}} .links{{margin:8px 26px;font-size:13px}} .links a{{color:#0b57d0;word-break:break-all}}
.post{{margin:8px 26px 20px;padding:14px;border:1px dashed #b9c3d0;border-radius:8px;font-size:13px;white-space:pre-wrap;background:#fff}} .foot{{margin:10px 26px 24px;font-size:11px;color:#7a8794}}
</style></head><body>
<div class="hdr"><h1>BÁO CÁO THANH TRA BÀI ĐĂNG</h1><div class="sub">Skill viet-ve-dang · lượt {html.escape(os.path.basename(R))} · soi lúc {NOW_VN} giờ VN ({NOW_LDN} London)</div></div>
<div class="verdict">{verdict}</div><div class="sum">{len(hard_fail)} luật không đạt · {len(look)} chỗ cần người nhìn · {len(checks)-len(hard_fail)-len(look)} đạt hoặc thông tin · bài md5 {md5} · luật: {html.escape(os.path.basename(a.luat))}</div>
<h2>Từng luật viết bài công khai</h2>{''.join(card(c) for c in checks)}
<h2>Luật 6 · Giọng gốc (tham khảo, không quyết)</h2><div class="voice"><b>{html.escape(voice['status'])}</b>\n{html.escape(voice['text'] or '(trống)')}</div>
<h2>Đường dẫn đã đăng</h2><div class="links">{'<br>'.join(f'{html.escape(k)}: <a href="{html.escape(str(v))}">{html.escape(str(v))}</a>' if str(v).startswith('http') else f'{html.escape(k)}: {html.escape(str(v))}' for k,v in links.items())}</div>
<h2>Số đo</h2><div class="links">{', '.join(f'{k} {v}' for k,v in stats.items())}</div>
<h2>Bài đã đăng (nguyên văn)</h2><div class="post">{html.escape(body)}</div>
<div class="foot">Người soi: {html.escape(a.ghe)} · thước: audit-bai-viet.py (skill viet-ve-dang) · phần luật 1–5 và ký hiệu là phép đo máy; luật 6 là nhận xét máy khác hãng, người đọc quyết.</div>
</body></html>"""
hp = os.path.join(OUT, f"AUDIT-{STAMP}.html"); open(hp, "w", encoding="utf-8").write(H)
pdf = os.path.join(OUT, f"AUDIT-{STAMP}.pdf"); chrome = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"; ok = False
if os.path.exists(chrome):
    try:
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer", f"--print-to-pdf={pdf}", "file://" + hp], capture_output=True, text=True, timeout=60); ok = os.path.exists(pdf) and os.path.getsize(pdf) > 1000
    except Exception: ok = False
if not ok:
    subprocess.run(["soffice", "--headless", "--convert-to", "pdf", "--outdir", OUT, hp], capture_output=True, text=True, timeout=120); ok = os.path.exists(pdf)
print(f"AUDIT {verdict} · {len(hard_fail)} không đạt · {len(look)} cần nhìn · pdf {'OK' if ok else 'HỎNG'} → {pdf}")
sys.exit(0 if ok else 5)
