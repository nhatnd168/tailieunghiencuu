# Dự Án Tailieu Nghiencuu

## Tổng quan
Dự án xử lý tài liệu nghiên cứu và phân tích dữ liệu với các công cụ Excel chuyên nghiệp.

## Skills Sẵn Có

### skill_tao_excel
Skill xử lý Excel toàn diện:
- Tạo và chỉnh sửa file .xlsx/.xlsm/.csv/.tsv
- Xây dựng mô hình tài chính với công thức Excel chuẩn
- Định dạng bảng tính theo chuẩn ngành (màu sắc, số, phông chữ)
- Kiểm tra lỗi công thức bằng scripts/recalc.py
- Làm sạch dữ liệu và phân tích

**Sử dụng khi:**
- File bảng tính là đầu vào hoặc đầu ra chính
- Cần xây dựng mô hình tài chính, dự báo
- Làm sạch và định dạng dữ liệu
- Thêm công thức, biểu đồ vào Excel

## Quy ước

### Tiêu chuẩn Excel
- Luôn kiểm tra lỗi công thức: #REF!, #DIV/0!, #VALUE!, #N/A, #NAME?
- Dùng công thức Excel, không hardcode giá trị đã tính
- Ghi chú nguồn cho mọi số liệu cứng (hardcode)
- Giữ định dạng và quy ước của template gốc khi chỉnh sửa

### Thư viện và công cụ
- **pandas:** phân tích dữ liệu, thao tác hàng loạt
- **openpyxl:** công thức, định dạng, tính năng Excel
- **scripts/recalc.py:** tính lại công thức (bắt buộc sau khi tạo/chỉnh sửa)

### Git
- Phát triển trên nhánh: `claude/charming-archimedes-zqum0o`
- Commit message rõ ràng, mô tả nội dung thay đổi
- Push sau khi hoàn thành tính năng
