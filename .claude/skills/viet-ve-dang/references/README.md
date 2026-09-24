# references/ của viet-ve-dang
- `chay-viet-ve-dang.sh` — bộ khung: tạo thư mục lượt, nhật ký, in từng chặng cho lớp, chế độ khô, cửa đăng cứng (`--dong-y` do Owner gõ).
- `mau-demo/` — hiện vật mẫu một lượt (bài, lời đọc, ảnh, video giữ chỗ, mp3 giữ chỗ, xem trước).
- `KET-QUA-DA-CHAY.md` — lượt khô đã chạy thật + 5 ca thử phá cửa đăng.
Chạy thử nhanh: `references/chay-viet-ve-dang.sh "<chủ đề>" --kho`
- `mau-demo/nguon-zoom-mau.jpg` (ảnh Zoom Owner gửi 09:2x 24/09) + `mau-demo/anh-4x5-mau.png` (kết quả ghép, **Owner duyệt 09:4x 24/09**: «ghép hình 4:5 như vậy là ok») — bộ chạy lại: `python3 ghep-anh-4x5.py mau-demo/nguon-zoom-mau.jpg /tmp/thu.png --tieu-de "BÍ MẬT AI · BUỔI 1 · TỐI 24/9" --dong-duoi "<câu mở>"`. Lưu ý: hai ảnh mẫu có tên học viên trên ô Zoom (Owner quyết giữ) — bản zip gửi học viên phải bỏ hai ảnh này.

## Thêm 24/09/2026 11:1x (v2.8) — dóng lời + cổng khớp phụ đề
- `dong-loi-whisper.py <loi-doc.txt> <whisper loi.json> <loi-dong.json>` — mỗi từ trong lời có giây bắt đầu/kết thúc thật (whisper word_timestamps; từ không nhận dạng được thì nội suy giữa hai từ kề). Khớp < 60 % ⇒ exit 3.
- `kiem-khop-phu-de.py <props.json> <loi-dong.json> [0.5]` — cổng: cue nào hiện lệch quá 0,5 s so với lúc từ đầu của nó được đọc ⇒ exit 4, không gửi, không đăng. Đối chứng dương 24/09: bản chia-theo-chữ FAIL 13/15 cue.
- `rap-video-storyboard.py` tự đọc `40-video/dong-loi/loi-dong.json` nếu có; bản cũ chia theo chữ giữ ở `_cu/rap-video-storyboard-v2.7.py`.

## Thêm 24/09/2026 12:2x (v3.0) — thanh tra bài đăng
- `audit-bai-viet.py <lượt> [--out DIR] [--luat FILE] [--khong-hermes] [--ghe TÊN]` — soi `20-bai/content.md` theo 6 luật viết bài công khai (+ ký hiệu cấm, từ nên tránh, CTA), đọc link từ `50-dang/`, ra `60-audit/AUDIT-<stamp>.{md,html,pdf,json}`. Luật 1–5 là phép đo máy; luật 6 do Hermes marketer chấm trong 90 giây (tham khảo). PDF: Chrome headless, dự phòng LibreOffice.
- `mau-demo/AUDIT-MAU.pdf` (+ .md/.html) — bản mẫu chạy trên bài lớp nháp 24/09/2026.
- Chuông 10 phút sau khi gửi link: Owner nói «thanh tra»/«audit» chạy ngay; im 10 phút tự chạy.
