# DỰ PHÒNG TỪNG CHẶNG — «skill luôn có fallback» (Owner 10:0x 24/09/2026)

Owner: *«sao video remotion thiếu audio google tts em ơi… thêm audio vào em nhé. google tts không được thì fallback về omnivoice nhé. nói chung skill luôn có fallback»*. Từ v2.3 mỗi chặng chế độ LỚP có đường chính và đường lui, ghi cứng ở đây; ghế chạy KHÔNG được dừng lại hỏi khi đường chính hỏng — đi đường lui rồi NÓI RÕ đã lui trong dòng in cho lớp.

| chặng | đường chính | dấu hiệu hỏng | đường lui | đo 24/09 |
|---|---|---|---|---|
| 0 ảnh vào | Owner gửi ảnh | không có | `tim-anh-zoom-moi.sh` tìm ảnh 2 phút trên Desktop; vẫn không có ⇒ câu hỏi duy nhất «anh chụp màn hình rồi gọi lại» | đối chứng 2 chiều đạt 10:05 |
| 1 caption | Hermes `-p marketer` (45 giây) | tệp rỗng / lỗi | `goi-gemini-xoay.sh` (khoá đầu treo 10 phút, có về) ⇒ lui nữa: `hermes -p cskh` | Hermes 45 giây · Gemini 10 phút |
| 2 ảnh 4:5 | `ghep-anh-4x5.py` (Pillow) | Pillow lỗi/font thiếu | `sips` cắt 4:5 thô từ ảnh gốc (không chữ) và nói rõ thiếu tiêu đề | Pillow đạt |
| 3a tiếng | `doc-thanh-tieng/scripts/doc.sh` (Gemini TTS, giọng Algieba) | exit ≠ 0 hoặc không ra mp3 (429 hết quota, 400 câu quá dài) | **OmniVoice** local: `~/Development/video-studio/scripts/gen-voice-omni.py` (giọng brand `voices/omni-seed-nam-tram.wav`) theo `info-short-omnivoice` §6; lui nữa: `say -v Linh` của macOS (giọng máy, nói rõ) | Gemini TTS 36,7 giây cho 465 ký tự |
| 3b video | Remotion `CaptionOverVideo` nền ảnh + cue theo tỉ lệ độ dài câu, rồi `ffmpeg` mux mp3 | render lỗi | ffmpeg `drawtext` chữ tĩnh trên nền + mp3 (không hoạt hình) | Remotion 17,5 giây câm ⇒ 36,7 giây có tiếng |
| 4 fanpage | AIBOSS.VN «Doanh Nhân Thời AI» (`MAKE_FANPAGE_AIBOSS_WEBHOOK`) | trả lời không có `post_id` / HTTP ≠ 200 | đề xuất trang «Eroca Thanh» (`MAKE_FANPAGE_V2_WEBHOOK`), đăng khi Owner gật | AIBOSS đạt 09:47 |
| 5 Short | YouTube qua `autopost.py --platforms youtube` (tệp phải trong `AI Video Renders/`) | không có `url=` | `--platforms tiktok` (Zernio); lui nữa: giao Owner tải tay, in đường dẫn tệp | YouTube đạt 09:49 |
| 6 quà zip | zip skill (bỏ `_cu`, hai ảnh mẫu Zoom) | — | — | zip v01 95 KB |

Nâng cấp đã ghi, chưa làm: dùng `CaptionReel` + `sinh-caption-props.py` của `info-short-codex-google-tts` để căn phụ đề theo lời chính xác từng câu (hiện căn theo tỉ lệ độ dài câu).

## Bổ sung 10:5x 24/09 — TIẾNG CÂM SAU MUX
- Triệu chứng: ffprobe thấy luồng aac, nghe không có gì. Đo `volumedetect` ra ≈ −91 dB.
- Gốc: render Remotion mang luồng tiếng câm stereo; ffmpeg không `-map` thì chọn luồng nhiều kênh hơn.
- Sửa tại chỗ (không cần chạy lại render): mux lại với `-map 0:v:0 -map 1:a:0`, đo lại volumedetect, rồi mới chép lên kệ/đăng.
- Cổng bắt buộc trước khi đăng: mean_volume > −50 dB. Ffprobe «có luồng» KHÔNG phải cổng.

## Bổ sung 11:1x 24/09 — DÓNG LỜI + CỔNG KHỚP PHỤ ĐỀ
- whisper không chạy / khớp < 60 % ⇒ `rap-video-storyboard.py` tự chia đều theo chữ; **phải ghi «phụ đề chia theo chữ, có thể lệch tới 4 giây» vào nhật ký và tin gửi Owner**, không im.
- `kiem-khop-phu-de.py` trả exit 4 ⇒ không gửi, không đăng; dựng lại props từ dóng lời. Trước khi tin thước: chạy nó trên bản chia-theo-chữ phải ra FAIL (đối chứng dương, 24/09: 13/15 cue).
- Kiểm cả tệp CUỐI: whisper lại mp4 sau mux, mốc từ đầu/giữa/cuối phải trùng mp3 (24/09: 0,00 s).

## Bổ sung 12:2x 24/09 — THANH TRA (bước 8)
- Hermes không trả lời trong 90 giây / không đúng khuôn ⇒ báo cáo vẫn ra, phần luật 6 ghi «người đọc tự chấm». Không chờ.
- Chrome headless hỏng ⇒ LibreOffice `soffice --convert-to pdf`. Cả hai hỏng ⇒ gửi Owner bản `.md` + `.html`, nói rõ thiếu PDF.
- Thiếu `posted.json`/log YouTube ⇒ mục đường dẫn ghi «không đọc được», báo cáo vẫn ra.
