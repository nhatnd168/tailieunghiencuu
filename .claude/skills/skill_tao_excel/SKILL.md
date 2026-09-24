---
name: skill_tao_excel
description: "Dùng khi file bảng tính là đầu vào hoặc đầu ra chính: mở, đọc, sửa, tạo mới file .xlsx/.xlsm/.csv/.tsv; làm sạch dữ liệu; công thức, định dạng, biểu đồ, mô hình tài chính."
---

# Skill: Tạo & Xử Lý Excel (bản đầy đủ)

## Yêu cầu bắt buộc cho mọi file Excel

### Font chuyên nghiệp
Dùng font nhất quán, chuyên nghiệp (Arial, Times New Roman...) trừ khi Anh Nhật yêu cầu khác hoặc file gốc đã có font riêng.

### Không được có lỗi công thức
Mọi file Excel giao cho người dùng phải có **ZERO lỗi công thức**: #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?.

### Giữ nguyên quy ước template có sẵn
Khi chỉnh sửa file đã có, phải nghiên cứu và khớp chính xác định dạng, phong cách, quy ước hiện tại. Không áp đặt chuẩn mới lên file đã có quy ước riêng — quy ước của file gốc luôn được ưu tiên.

## Mô hình tài chính

### Quy chuẩn màu sắc (theo chuẩn ngành)
| Màu chữ | Ý nghĩa |
|---|---|
| Xanh dương (RGB 0,0,255) | Số liệu đầu vào cứng, số người dùng sẽ thay đổi cho các kịch bản |
| Đen (RGB 0,0,0) | Toàn bộ công thức và phép tính |
| Xanh lá (RGB 0,128,0) | Liên kết kéo từ sheet khác trong cùng workbook |
| Đỏ (RGB 255,0,0) | Liên kết ngoài đến file khác |
| Nền vàng (RGB 255,255,0) | Giả định quan trọng cần chú ý hoặc ô cần cập nhật |

### Quy tắc định dạng số
- Năm: định dạng dạng text ("2024", không phải "2,024").
- Tiền tệ: `$#,##0`; LUÔN ghi rõ đơn vị trên tiêu đề cột (ví dụ "Doanh thu (triệu VNĐ)").
- Số 0: định dạng để hiển thị thành "-", kể cả với phần trăm.
- Phần trăm: mặc định 1 chữ số thập phân (0.0%).
- Bội số định giá (EV/EBITDA, P/E...): định dạng 0.0x.
- Số âm: dùng dấu ngoặc đơn (123), không dùng dấu trừ.

### Nguyên tắc xây dựng công thức

**Vị trí đặt giả định:** Đặt TẤT CẢ giả định (tỷ lệ tăng trưởng, biên lợi nhuận, bội số...) vào ô riêng biệt. Dùng tham chiếu ô trong công thức thay vì số cứng.
Ví dụ: dùng `=B5*(1+$B$6)` thay vì `=B5*1.05`.

**Phòng tránh lỗi công thức:**
- Kiểm tra lại toàn bộ tham chiếu ô.
- Kiểm tra lỗi lệch một đơn vị (off-by-one) trong vùng dữ liệu (range).
- Đảm bảo công thức nhất quán trên toàn bộ các kỳ dự phóng.
- Kiểm thử với trường hợp biên (giá trị 0, số âm).
- Kiểm tra không có tham chiếu vòng (circular reference) ngoài ý muốn.

**Ghi chú nguồn cho số liệu hardcode:** Thêm comment hoặc ghi chú bên cạnh ô, theo định dạng: "Nguồn: [Hệ thống/Tài liệu], [Ngày], [Tham chiếu cụ thể], [URL nếu có]".

## Quy trình làm việc chuẩn

1. **Chọn công cụ:** pandas cho phân tích dữ liệu; openpyxl cho công thức/định dạng.
2. **Tạo/Mở file:** tạo workbook mới hoặc mở file có sẵn.
3. **Chỉnh sửa:** thêm/sửa dữ liệu, công thức, định dạng.
4. **Lưu file.**
5. **Tính lại công thức (BẮT BUỘC nếu có dùng công thức):**
```bash
python scripts/recalc.py output.xlsx
```
6. **Kiểm tra và sửa lỗi:** script trả về JSON có trạng thái; nếu `status` là `errors_found`, xem `error_summary` để biết loại lỗi và vị trí cụ thể, sửa rồi chạy lại.

### Nguyên tắc cốt lõi: dùng công thức Excel, không hardcode giá trị

**Sai:**
```python
total = df['Sales'].sum()
sheet['B10'] = total # hardcode kết quả 5000
```

**Đúng:**
```python
sheet['B10'] = '=SUM(B2:B9)'
```
Nguyên tắc này áp dụng cho MỌI phép tính — tổng, phần trăm, tỷ lệ, chênh lệch... Bảng tính phải luôn có khả năng tính lại khi dữ liệu nguồn thay đổi.

### Ví dụ tạo file mới với openpyxl
```python
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

wb = Workbook()
sheet = wb.active
sheet['A1'] = 'Hello'
sheet.append(['Row', 'of', 'data'])
sheet['B2'] = '=SUM(A1:A10)'
sheet['A1'].font = Font(bold=True, color='FF0000')
sheet['A1'].fill = PatternFill('solid', start_color='FFFF00')
sheet['A1'].alignment = Alignment(horizontal='center')
sheet.column_dimensions['A'].width = 20
wb.save('output.xlsx')
```

### Chỉnh sửa file có sẵn (giữ nguyên công thức và định dạng)
```python
from openpyxl import load_workbook
wb = load_workbook('existing.xlsx')
sheet = wb.active
sheet['A1'] = 'New Value'
sheet.insert_rows(2)
wb.save('modified.xlsx')
```

## Danh sách kiểm tra công thức trước khi giao file

**Kiểm tra thiết yếu:**
- Thử 2-3 tham chiếu mẫu để xác nhận đúng giá trị trước khi build toàn bộ mô hình.
- Đối chiếu đúng cột Excel (ví dụ cột thứ 64 là BL, không phải BK).
- Nhớ Excel đánh số hàng từ 1 (DataFrame row 5 = Excel row 6).

**Lỗi thường gặp cần tránh:**
- Xử lý giá trị NaN bằng `pd.notna()`.
- Dữ liệu năm tài chính (FY) thường nằm ở các cột rất xa bên phải (cột 50+).
- Tìm tất cả các kết quả trùng khớp, không chỉ kết quả đầu tiên.
- Kiểm tra mẫu số trước khi chia (#DIV/0!).
- Kiểm tra đúng cú pháp tham chiếu chéo sheet (Sheet1!A1).

## Đọc kết quả từ scripts/recalc.py
```json
{
 "status": "success",
 "total_errors": 0,
 "total_formulas": 42,
 "error_summary": {
 "#REF!": { "count": 2, "locations": ["Sheet1!B5", "Sheet1!C10"] }
 }
}
```

## Nguyên tắc chọn thư viện
- **pandas:** phù hợp phân tích dữ liệu, thao tác hàng loạt, xuất dữ liệu đơn giản.
- **openpyxl:** phù hợp định dạng phức tạp, công thức, tính năng đặc thù của Excel.

## Phong cách code khi xử lý Excel
- Viết code Python ngắn gọn, súc tích, không comment thừa.
- Tránh tên biến dài dòng, không lặp thao tác không cần thiết.
- Trong file Excel: thêm ghi chú cho công thức phức tạp/giả định quan trọng, ghi rõ nguồn số liệu hardcode.

*Ghi chú: đây là bản cập nhật đầy đủ hơn của skill Excel, thay thế bản tóm tắt trước đó trong cùng thư mục.*
