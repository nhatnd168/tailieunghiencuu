#!/bin/bash
# viet-ve-dang orchestration scaffold.
# Creates the run folder, writes the log, prints one line per stage for the class,
# copies sample artifacts in dry mode, and HARD-STOPS before publishing unless --dong-y.
# It never calls a child skill by itself: the agent session invokes child skills in order.
set -u
export LC_ALL=en_US.UTF-8
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
MAU="$SKILL_DIR/references/mau-demo"
ROOT="${VIET_VE_DANG_ROOT:-$HOME/DU-AN/aiboss-business-os-org/viet-ve-dang}"
QUET="$HOME/.claude/skills/demo-truoc-lop/references/quet-rieng-tu.py"

case "${1:-}" in
  ''|--*) echo "cách dùng: chay-viet-ve-dang.sh \"<chủ đề>\" [--kho] [--toi viet|anh|tieng|video|dang] [--dong-y]" >&2; exit 2 ;;
esac
CHU_DE="$1"; shift
KHO=0; DONG_Y=0; TOI="dang"
for a in "$@"; do
  case "$a" in
    --kho) KHO=1 ;;
    --dong-y) DONG_Y=1 ;;
    --toi=*) TOI="${a#--toi=}" ;;
    --toi) ;;  # value handled below
    viet|anh|tieng|video|dang) TOI="$a" ;;
    *) echo "cờ lạ: $a" >&2; exit 2 ;;
  esac
done
[ -n "$CHU_DE" ] || { echo "cách dùng: chay-viet-ve-dang.sh \"<chủ đề>\" [--kho] [--toi viet|anh|tieng|video|dang] [--dong-y]" >&2; exit 2; }

slug=$(python3 -c 'import sys,unicodedata,re;s=sys.argv[1].replace("đ","d").replace("Đ","D");s=unicodedata.normalize("NFD",s);s="".join(c for c in s if unicodedata.category(c)!="Mn");s=re.sub(r"[^A-Za-z0-9]+","-",s).strip("-").lower();print(s[:40])' "$CHU_DE")
[ -n "$slug" ] || slug="chu-de"
TS=$(date +%Y%m%d-%H%M%S)
RUN="$ROOT/$slug-$TS"
mkdir -p "$RUN/10-kich-ban" "$RUN/20-bai" "$RUN/30-anh" "$RUN/40-video" "$RUN/50-dang"
gio() { TZ=Europe/London date '+%H:%M'; }
md5s() { [ -f "$1" ] && md5 -q "$1" | cut -c1-12 || echo "-"; }
log() { printf '%s | %s | %s | %s | %s\n' "$(gio)" "$1" "$2" "$3" "$4" >> "$RUN/NHAT-KY.md"; }
in_lop() { echo "[chặng $1/5] $2 · $3 · hiện vật: $4"; }

printf '# ĐỀ BÀI\nChủ đề: %s\nChế độ: %s\nDừng sau: %s\nBắt đầu: %s London\n' "$CHU_DE" "$([ $KHO = 1 ] && echo 'KHÔ (hiện vật mẫu)' || echo 'SỐNG')" "$TOI" "$(gio)" > "$RUN/00-de-bai.md"
printf '# NHẬT KÝ LƯỢT — %s\ngiờ | chặng | skill gọi | hiện vật | md5\n' "$slug" > "$RUN/NHAT-KY.md"
echo "Lượt: $slug-$TS · chế độ $([ $KHO = 1 ] && echo KHÔ || echo SỐNG) · dừng sau chặng «${TOI}»"

# stage 1 VIET
if [ $KHO = 1 ]; then cp "$MAU/content.md" "$RUN/20-bai/content.md"; cp "$MAU/narration.txt" "$RUN/10-kich-ban/narration.txt"; else printf '# GỌI SKILL: viet-giong-eroca\nViết từ 00-de-bai.md ⇒ ghi 20-bai/content.md và 10-kich-ban/narration.txt (số viết bằng chữ).\n' > "$RUN/20-bai/GOI-SKILL.md"; fi
log "1 VIẾT" "viet-giong-eroca" "20-bai/content.md" "$(md5s "$RUN/20-bai/content.md")"; in_lop 1 "VIẾT bài + kịch bản" "xong $(gio)" "content.md · narration.txt"
[ "$TOI" = viet ] && { echo "Dừng theo --toi viet. Thư mục: $RUN"; exit 0; }

# stage 2 ANH
if [ $KHO = 1 ]; then cp "$MAU/anh-01.png" "$RUN/30-anh/anh-01.png"; else printf '# GỌI SKILL: ve-anh-chon-duong\nĐề bài ảnh viết vào 30-anh/de-bai.md rồi gọi; nhớ < /dev/null khi gọi Codex. Ảnh ra 30-anh/anh-01.png (16:9).\n' > "$RUN/30-anh/GOI-SKILL.md"; fi
log "2 ẢNH" "ve-anh-chon-duong" "30-anh/anh-01.png" "$(md5s "$RUN/30-anh/anh-01.png")"; in_lop 2 "VẼ ảnh" "xong $(gio)" "anh-01.png"
[ "$TOI" = anh ] && { echo "Dừng theo --toi anh. Thư mục: $RUN"; exit 0; }

# stage 3 TIENG (child skill has no gate: ask once before calling in live mode)
if [ $KHO = 1 ]; then cp "$MAU/loi.mp3" "$RUN/40-video/loi.mp3" 2>/dev/null || : ; else printf '# GỌI SKILL: doc-thanh-tieng\nHỎI MỘT CÂU trước khi gọi (skill con không có cổng gật, tiêu một lượt chìa Gemini):\n  doc.sh "<lượt>/10-kich-ban/narration.txt" --output "<lượt>/40-video/loi.mp3"\n' > "$RUN/40-video/GOI-SKILL-TIENG.md"; fi
log "3 TIẾNG" "doc-thanh-tieng" "40-video/loi.mp3" "$(md5s "$RUN/40-video/loi.mp3")"; in_lop 3 "ĐỌC thành tiếng" "xong $(gio)" "loi.mp3"
[ "$TOI" = tieng ] && { echo "Dừng theo --toi tieng. Thư mục: $RUN"; exit 0; }

# stage 4 VIDEO (child skill has its own dry-run gate; live mode stops there)
if [ $KHO = 1 ]; then cp "$MAU/video-mau.mp4" "$RUN/40-video/video-mau.mp4"; else printf '# GỌI SKILL: video-omni-ads (hoặc video-slide-khop-loi)\nĐi qua CỔNG CHẠY KHÔ của skill con: in máy gì, số credit, chờ Owner gật. Video ra 40-video/.\n' > "$RUN/40-video/GOI-SKILL-VIDEO.md"; fi
log "4 VIDEO" "video-omni-ads" "40-video/video-mau.mp4" "$(md5s "$RUN/40-video/video-mau.mp4")"; in_lop 4 "DỰNG video" "xong $(gio)" "video-mau.mp4"
[ "$TOI" = video ] && { echo "Dừng theo --toi video. Thư mục: $RUN"; exit 0; }

# stage 5 DANG — HARD GATE
cp "$MAU/XEM-TRUOC.md" "$RUN/50-dang/XEM-TRUOC.md" 2>/dev/null || printf '# XEM TRƯỚC\n' > "$RUN/50-dang/XEM-TRUOC.md"
printf '\nChủ đề: %s · bài: 20-bai/content.md · ảnh: 30-anh/anh-01.png · video: 40-video/video-mau.mp4\n' "$CHU_DE" >> "$RUN/50-dang/XEM-TRUOC.md"
echo "[chặng 5/5] ĐĂNG · bản xem trước: XEM-TRUOC.md"
if [ $KHO = 1 ]; then
  log "5 ĐĂNG" "(khô)" "50-dang/XEM-TRUOC.md" "$(md5s "$RUN/50-dang/XEM-TRUOC.md")"
  echo "DỪNG: chế độ khô không đăng (kể cả có --dong-y). Thư mục: $RUN"; exit 0
fi
if [ $DONG_Y = 0 ]; then
  log "5 ĐĂNG" "DỪNG chờ Owner" "50-dang/XEM-TRUOC.md" "$(md5s "$RUN/50-dang/XEM-TRUOC.md")"
  echo "DỪNG: chưa có --dong-y của Owner. Muốn đăng, Owner gõ lại lệnh kèm --dong-y. Thư mục: $RUN"; exit 0
fi
echo "SẮP ĐĂNG LÊN TRANG THẬT — gọi: fanpage-post-demo (bắc cầu content.md) → fanpage-post (Owner Confirm) · video: dang-video-tiktok-short --dry-run trước."
printf '# GỌI SKILL: fanpage-post-demo → fanpage-post; dang-video-tiktok-short --dry-run rồi mới post\nOwner đã gõ --dong-y lúc %s London.\n' "$(gio)" > "$RUN/50-dang/GOI-SKILL.md"
log "5 ĐĂNG" "fanpage-post / dang-video-tiktok-short" "50-dang/GOI-SKILL.md" "$(md5s "$RUN/50-dang/GOI-SKILL.md")"
echo "Thư mục: $RUN"
