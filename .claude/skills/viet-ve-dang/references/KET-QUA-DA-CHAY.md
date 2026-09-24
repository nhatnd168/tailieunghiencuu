# KẾT QUẢ ĐÃ CHẠY — lượt khô lúc dựng skill (chờ Owner duyệt làm bản mẫu chính thức)
Chạy lúc 09:00 24/09/2026 London · lệnh: `chay-viet-ve-dang.sh "Hệ thống hoá doanh nghiệp một người" --kho`
Thư mục lượt: `~/DU-AN/aiboss-business-os-org/viet-ve-dang/he-thong-hoa-doanh-nghiep-mot-nguoi-20260924-090050`

## Nhật ký lượt (chép nguyên)
```
# NHẬT KÝ LƯỢT — he-thong-hoa-doanh-nghiep-mot-nguoi
giờ | chặng | skill gọi | hiện vật | md5
09:00 | 1 VIẾT | viet-giong-eroca | 20-bai/content.md | cb3db80ee038
09:00 | 2 ẢNH | ve-anh-chon-duong | 30-anh/anh-01.png | a59d2b4aab5e
09:00 | 3 TIẾNG | doc-thanh-tieng | 40-video/loi.mp3 | 85006b168782
09:00 | 4 VIDEO | video-omni-ads | 40-video/video-mau.mp4 | b6897094539a
09:00 | 5 ĐĂNG | (khô) | 50-dang/XEM-TRUOC.md | be45888c3b06
```

## Thử phá cửa đăng (đo 09:00 London, thư mục thử riêng ngoài dự án)
| ca | lệnh | kết quả | đạt |
|---|---|---|---|
| A | `--kho` | dừng chặng 5, 50-dang chỉ có XEM-TRUOC.md | đạt |
| B | sống, không `--dong-y` | «DỪNG: chưa có --dong-y của Owner» | đạt |
| C | sống, có `--dong-y` (đối chứng dương) | in «SẮP ĐĂNG LÊN TRANG THẬT» + ghi 50-dang/GOI-SKILL.md | đạt — cửa đọc cờ đúng |
| D | `--kho --dong-y` | vẫn dừng «chế độ khô không đăng» | đạt |
| E | `--kho --toi anh` | dừng sau chặng 2 | đạt |
Quét riêng tư (demo-truoc-lop/quet-rieng-tu.py) trên lượt khô: xem dòng in ở lượt dựng. Ký hiệu cấm: 0.

## Hiện vật mẫu (references/mau-demo/)
- content.md (bài fanpage mẫu, không tên người thật) · narration.txt (lời đọc, số viết bằng chữ) · anh-01.png (tấm 10 bộ K4, 16:9) · video-mau.mp4 (3 giây, dựng từ ảnh bằng ffmpeg, chỉ giữ chỗ) · loi.mp3 (2 giây im lặng, giữ chỗ) · XEM-TRUOC.md.
- Lượt SỐNG đầu tiên trước lớp sẽ thay các tệp giữ chỗ bằng hiện vật thật; khi Owner duyệt, chép lượt đó về đây làm bản mẫu chính thức.

## Bổ sung v1.1 (09:16 London 24/09) — vá theo soi của trợ lý AI 09:15
Lỗi: cờ đứng ở vị trí chủ đề (`chay… --kho`) bị nhận làm chủ đề, chế độ khô rơi, in «Chế độ: SỐNG». Vá: từ chối `$1` rỗng hoặc bắt đầu bằng `--`, thoát mã 2.
| ca | lệnh | kết quả | đạt |
|---|---|---|---|
| 1 | `--kho` (không chủ đề) | in cách dùng, mã thoát 2 | đạt |
| 2 | không tham số | mã thoát 2 | đạt |
| 3 | `"chủ đề" --kho` | chạy khô, dừng chặng 5 | đạt |
| 4 | `"chủ đề"` (sống, không cờ) | DỪNG chờ Owner | đạt |
| 5 | `--dong-y "chủ đề"` (cờ đứng đầu) | mã thoát 2, không chạy | đạt |

## Lượt LỚP nháp 24/09/2026 09:37–09:49 London (đăng thật theo lệnh Owner 09:2x)
Thư mục: `~/DU-AN/aiboss-business-os-org/viet-ve-dang/lop-bimatai-buoi-1-20260924-093706` · caption: máy viết khác hãng 45 giây (Gemini khoá đầu treo 10 phút) · ảnh 4:5 1080×1350 có dấu giờ + tên ghế (Owner duyệt 09:4x) · Remotion 7 cue 17,5 giây · bài AIBOSS post_id 1149968288195769_122124783645311722 (09:47) · Short https://www.youtube.com/shorts/ni0RSJVeR6Q (09:49). Lỗi đã vá: bộ đăng YouTube từ chối tệp ngoài AI Video Renders ⇒ chép vào đó. Owner 10:0x: «đã thấy bài đăng fanpage tốt chuẩn».
Nhật ký lượt:
```
# NHẬT KÝ LƯỢT LỚP — 20260924-093706 (lượt NHÁP, Owner 09:2x)
giờ | chặng | máy | hiện vật | md5
09:46 | 1 VIẾT | máy viết khác hãng (gemini treo từ 09:37) | 20-bai/content.md | b0351dc875af
09:46 | 2 ẢNH | Pillow ghép 4:5 + dấu giờ + tên ghế | 30-anh/anh-4x5.jpg | 4901824aa853
09:46 | 3 VIDEO | Remotion CaptionOverVideo | 40-video/short-9x16.mp4 | 3635cb4988a8
09:47 | 4 ĐĂNG FB | fanpage-post make-webhook-v2 (aiboss) | 50-dang/posted.json | bd56c21b735d
09:48 | 5 ĐĂNG YT | dang-video-tiktok-short (youtube) | 50-dang/youtube-log.txt | 20eb63ce742a
09:49 | 5 ĐĂNG YT (lần 2, tệp trong renders-dir) | dang-video-tiktok-short (youtube) | 50-dang/youtube-log.txt | ccfc71e31269
```

### Sửa 10:0x–10:11 (Owner bắt video thiếu tiếng)
- Tiếng: Google TTS qua `doc-thanh-tieng` 36,7 giây (giọng Algieba) ⇒ mux vào Short. Bản 1 có tiếng (EvTGkaSGIIc) bị cắt mép phụ đề vì 12 từ/cue và phụ đề đè lên chân ảnh; bản 2 (DxrKhe5sMwg) đặt ảnh cao y=110, cue ≤ 5 từ — đạt, mở khung 5 giây và 20 giây nhìn.
- Bài học: PM đã sót skill `info-short-codex-google-tts` (Google TTS + Remotion có sẵn) khi dựng v2.0; từ v2.3 mọi chặng có bảng dự phòng `DU-PHONG-TUNG-CHANG.md`.

### Nâng cấp storyboard 10:2x–10:3x (Owner 10:3x)
- 6 hình 16:9 Codex gpt-6-astra song song: cả 6 nhận trong 30 giây, xong sau ~3,5 phút, đều 1920×1080; mỗi hình 5,3–6,3 giây trên lời 36,7 giây; 3 giây đầu hình 4:5. Ráp bằng `rap-video-storyboard.py`, phụ đề Remotion ≤5 từ/cue theo mốc storyboard, mux tiếng. Short: https://www.youtube.com/shorts/KN06Kg0ZXdQ

### Phụ đề hai dòng + dòng chữ trên 10:4x–10:5x (Owner 10:4x «phụ đề chạy 2 dòng và vị trí phụ đề cao lên vì có thêm 1 dòng chữ ở trên nữa»)
- Bố cục Remotion mới `CaptionOverVideoHigh` (tệp riêng, `CaptionOverVideo` cũ giữ nguyên cho skill khác). 6 hình 9:16 Codex (1080×1920, xong 10:43) + 3 giây hình 4:5 thu 860 px ghim trên.
- Bản sb2 (chia 9 từ cứng): 15 cue, có cue lẻ một chữ («bạn.» · «tin.») và phụ đề đè chân hình 4:5 trong 3 giây đầu ⇒ loại.
- Bản sb3 (chia đều ≤ 9 từ): 15 cue 5–9 từ; tệp `40-video/short-9x16-sb3.mp4` md5 <md5>, 36,67 giây có tiếng; 8 khung trích đúng: dòng vàng trên, hai dòng phụ đề, không đè hình. KHÔNG đăng Short thứ 5 vì Owner chưa bảo; bản đăng khi lên lớp sẽ là bản chạy thật.
- 10:5x Owner: «tôi thấy video hình ok rồi nhưng sao không nghe tiếng». Đo: bản sb3 có luồng aac nhưng mean_volume −91 dB (câm); `loi.mp3` −17,9 dB; bản Remotion trần có sẵn luồng tiếng câm 2 kênh 48 kHz; lời mono 24 kHz ⇒ ffmpeg không `-map` chọn luồng câm. Bản storyboard đăng sáng (KN06Kg0ZXdQ) đo −17,9 dB, có tiếng. Sửa: mux ghim `-map` ⇒ `short-9x16-sb3-tieng.mp4` md5 <md5>, −20,9 dB; chép lên `AI Video Renders/omni/viet-ve-dang/short-9x16-2dong-co-tieng-1055.mp4`, xoá bản câm. Skill v2.7 thêm CỔNG TIẾNG.

### Khớp phụ đề với tiếng 11:0x–11:1x (Owner 11:1x «gửi video xong phải ngồi check lại phụ đề và âm thanh đã khớp chưa, skill gốc hình như có bước này»)
- Skill gốc `info-short-codex-google-tts` v1.2 dòng 58 tự khai «timing XẤP XỈ, chia đều theo chữ; cần khớp từng từ thì thêm bước dóng lời whisper sau» — bước đó chưa từng được làm. Nay làm: whisper small word_timestamps (14 s), `dong-loi-whisper.py` khớp 100/105 từ.
- Đối chứng dương: bản sb3 (chia theo chữ) qua `kiem-khop-phu-de.py` FAIL 13/15 cue, lệch lớn nhất 4,39 s. Bản sb4 theo tiếng: PASS, lệch lớn nhất 0,03 s. Mux có `-map`: −20,9 dB. Whisper lại mp4 cuối: 105 từ, 0,00 s dịch so mp3. Dải 15 khung tại mốc từng cue: từ nhấn đúng từ đang đọc.
- Tệp: `40-video/short-9x16-sb4-tieng.mp4` md5 <md5> → kệ `AI Video Renders/omni/viet-ve-dang/short-9x16-khop-tieng-1109.mp4`; bản 1055 (câm, lệch) đã xoá khỏi kệ. Chưa đăng Short mới.
- 11:2x Owner: «video mới nhất đã ok» (bản khớp tiếng 1109). Owner giao chuyển 4 Short thử sáng nay sang private ⇒ đã đổi qua YouTube Data API (cùng chìa với autopost.py), đọc lại từng video: private. Kênh sạch trước lớp. Lời dặn Owner cho lúc demo (đưa vào tấm nhắc mở video, eeat soạn): «video này không phải video AI người thật, chỉ là video thông tin, nhưng nó rẻ vì miễn phí — không tốn tiền API hay credit».
- 11:4x Owner: «ưu tiên giữ hình chụp màn hình gốc có cả comment của học viên ở zoom» ⇒ bộ ghép mặc định giữ cột chat (v2.9). Ghép thử ảnh mẫu Zoom giữ nguyên gốc: `30-anh/anh-4x5-giu-chat.png` 1080×1350, bản mẫu chép vào `mau-demo/anh-4x5-mau-giu-chat.png`. Bản cắt chat cũ giữ ở `mau-demo/anh-4x5-mau.png` (Owner duyệt 09:5x) để đối chiếu.

### Thanh tra bài đăng 12:2x (Owner 12:2x: audit khi nói «thanh tra/audit» hoặc im 10 phút; làm mẫu PDF)
- `audit-bai-viet.py` chạy trên bài lớp nháp (`20-bai/content.md` md5 theo báo cáo): 8/8 mục ĐẠT (tên công khai · «Thanh» 3 lần · chữ ký · «bạn» 4 lần, 0 «anh chị» · 0 bảng · 0 ký hiệu · 0 từ nên tránh · có CTA). máy viết khác hãng chấm giọng 8/10, gợi thay «cùng bạn khám phá». PDF 2 trang qua Chrome headless (~32 giây cả Hermes). Mẫu chép vào `mau-demo/AUDIT-MAU.pdf`.
- Lỗi bắt trong lượt đầu: Hermes ECHO lại đề nên regex lấy trúng khuôn mẫu «DIEM: <số 1-10>» thay vì câu trả lời ⇒ lấy khối CUỐI không chứa «<». 
