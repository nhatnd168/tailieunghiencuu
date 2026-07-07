# Xcons Group — Dashboard KQKD (Google Apps Script)

Dashboard nội bộ đọc trực tiếp từ Google Sheet **"Bản sao của Xcons Group_KQKD Q1.26"**
(`1VXFUQhCGy48lk1FmO-zhjb73hezpuwdP8QWGmSMH5nk`) và hiển thị dưới dạng Web App:
KQKD (P&L) kế hoạch/thực hiện/chênh lệch theo quý, sản lượng & lương, hợp đồng tồn
(tổng hợp + chi tiết thiết kế/thi công), chi phí (CP cố định, KMP, kết xuất kế toán),
nhân sự & lương cố định, khấu hao CCDC, thuế & dự phòng.

## Vì sao không phải "dashboard tổng quát theo kiểu cột"

File KQKD này không phải bảng dữ liệu phẳng — mỗi sheet là một báo cáo có cấu trúc
riêng (dòng tiêu đề, mục KẾ HOẠCH/THỰC HIỆN/CHÊNH LỆCH, nhóm La Mã, mã phí phân cấp…).
Vì vậy backend không dùng "dò kiểu cột chung" mà đọc đúng cấu trúc thật của từng sheet
(xem `Parsers.gs`), tương tự cách một kế toán đọc báo cáo. Mọi range đều được đọc động
qua `getLastRow()`/`getDataRange()` — không hardcode số dòng — nên báo cáo quý sau vẫn
chạy đúng khi số dòng thay đổi, miễn cấu trúc mốc (TT, KẾ HOẠCH/THỰC HIỆN/CHÊNH LỆCH,
mã La Mã, "Mã dự án", "Mã THCP"…) không đổi.

## Cấu trúc file

| File | Vai trò |
|---|---|
| `Code.gs` | `doGet()` phục vụ web app, `getDashboardData()` — endpoint duy nhất client gọi |
| `Parsers.gs` | Toàn bộ logic đọc & phân tích từng sheet (không hardcode range) |
| `index.html` | Toàn bộ giao diện: CSS, bảng dữ liệu có tìm kiếm/sắp xếp/phân trang, biểu đồ Chart.js, tìm kiếm toàn cục |
| `appsscript.json` | Manifest (múi giờ, quyền truy cập web app) |

## Cách triển khai

1. Mở https://script.google.com → **New project**.
2. Đổi tên project (ví dụ "Xcons Dashboard KQKD").
3. Xoá nội dung `Code.gs` mặc định, dán nội dung file `Code.gs` ở đây.
4. Tạo thêm file script mới (**+ → Script**) đặt tên `Parsers`, dán nội dung `Parsers.gs`.
5. Tạo file HTML mới (**+ → HTML**) đặt tên đúng là `index`, dán nội dung `index.html`.
6. Mở **Project Settings** (⚙️) → dán nội dung `appsscript.json` vào file manifest
   (hoặc bật "Show appsscript.json" rồi chỉnh trực tiếp).
7. Bấm **Deploy → New deployment**:
   - Type: **Web app**
   - Execute as: **User accessing the web app**
   - Who has access: chọn theo nhu cầu nội bộ (ví dụ "Anyone within [tổ chức]")
8. Lần đầu chạy sẽ hiện màn hình xin cấp quyền (đọc Google Sheets) — bấm **Authorize**,
   chọn tài khoản có quyền truy cập Sheet nguồn.
9. Copy URL Web app vừa deploy, mở để xem dashboard. Mỗi lần Sheet cập nhật số liệu,
   bấm **↻ Làm mới** trên dashboard (hoặc tải lại trang) để lấy dữ liệu mới nhất —
   dashboard không cache phía server, luôn đọc trực tiếp từ Sheet khi bấm làm mới/tải trang.

### Cập nhật code sau này

Sửa trực tiếp trong trình soạn Apps Script rồi **Deploy → Manage deployments →
Edit (biểu tượng bút) → New version → Deploy**. Sửa code mà không tạo version mới
sẽ không phản ánh lên URL web app đã publish.

## Ghi chú vận hành

- Người xem dashboard cần có ít nhất quyền **Viewer** trên Google Sheet nguồn (vì
  deploy ở chế độ "Execute as: User accessing the web app").
- Nếu muốn mọi người xem được dù không có quyền trên Sheet, đổi **Execute as** thành
  **Me** khi deploy — khi đó dashboard chạy bằng quyền của người deploy, nhưng cần
  cân nhắc vì dữ liệu tài chính sẽ lộ cho bất kỳ ai có URL theo quyền truy cập đã chọn.
- Sheet ẩn "Chi tiết 1 số khoản mục phí" vẫn được đọc bình thường (Apps Script đọc
  được sheet ẩn) và hiển thị trong tab **Chi phí → Chi tiết một số khoản mục**.
