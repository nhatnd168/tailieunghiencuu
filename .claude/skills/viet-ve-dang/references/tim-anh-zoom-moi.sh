#!/bin/bash
# Find the newest screenshot Owner just took (class mode, when no image path was given).
# Owner 10:0x 24/09/2026: if no image link is sent, look in the usual screenshot folder for a Zoom
# screenshot from the last 1-2 minutes; if found, announce it and continue without asking.
# Usage: tim-anh-zoom-moi.sh [--phut N] [--thu-muc DIR]   (default: 2 minutes, ~/Desktop)
# Exit 0 + prints the path when found; exit 1 + message when nothing recent exists.
set -u
export LC_ALL=en_US.UTF-8
PHUT=2
DIR="$(defaults read com.apple.screencapture location 2>/dev/null || true)"
[ -n "$DIR" ] && [ -d "${DIR/#\~/$HOME}" ] && DIR="${DIR/#\~/$HOME}" || DIR="$HOME/Desktop"
while [ $# -gt 0 ]; do
  case "$1" in
    --phut) PHUT="$2"; shift 2 ;;
    --thu-muc) DIR="$2"; shift 2 ;;
    *) echo "cờ lạ: $1" >&2; exit 2 ;;
  esac
done
NEWEST=$(find "$DIR" -maxdepth 1 -type f \( -iname '*.png' -o -iname '*.jpg' -o -iname '*.jpeg' \) -mmin -"$PHUT" -print0 2>/dev/null | xargs -0 ls -t 2>/dev/null | head -1)
if [ -z "$NEWEST" ]; then
  echo "KHÔNG thấy ảnh chụp màn hình nào trong $PHUT phút gần đây ở $DIR — Owner chụp màn hình Zoom rồi gọi lại, hoặc gửi đường dẫn ảnh." >&2
  exit 1
fi
GIO=$(stat -f '%Sm' -t '%H:%M:%S' "$NEWEST")
echo "Có thấy hình chụp Zoom ở thư mục quy định ($DIR) trong $PHUT phút gần đây: $(basename "$NEWEST") (lúc $GIO) — viết bài và đăng theo quy trình, không hỏi thêm." >&2
printf '%s\n' "$NEWEST"
