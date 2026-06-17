# Hướng Dẫn Setup Chi Tiết

## Yêu Cầu Hệ Thống

| Thành phần | Yêu cầu |
|-----------|---------|
| n8n | Version 1.0+ (self-hosted hoặc n8n.cloud) |
| Apollo.io | Account có API access (Paid plan) |
| OpenAI | API key với access GPT-4o |
| Airtable | Free plan đủ dùng |
| Gmail | Google account (cần cấp OAuth) |
| Telegram | Bot token + Chat/Group ID |

---

## Bước 1: Tạo Airtable Base

### 1.1 Tạo Base mới
1. Vào [airtable.com](https://airtable.com) → **Create a base**
2. Đặt tên: `Lead Generation CRM`

### 1.2 Tạo Table "Leads"
Tạo các field theo thứ tự sau (xem `config/airtable_schema.json` để có đầy đủ thông tin):

| Field Name | Field Type | Ghi chú |
|-----------|------------|---------|
| Name | Single line text | |
| Email | Email | |
| Company | Single line text | |
| Title | Single line text | |
| Industry | Single line text | |
| Website | URL | |
| LinkedIn_URL | URL | |
| Country | Single line text | |
| Apollo_ID | Single line text | **Quan trọng** - dùng deduplicate |
| AI_Score | Number (no decimals) | |
| AI_Score_Reasoning | Long text | |
| AI_Fit_Factors | Single line text | |
| Status | Single select | Thêm đủ các options (xem schema) |
| Email_Subject | Single line text | |
| Email_Thread_ID | Single line text | |
| Email_Sent_Date | Date (YYYY-MM-DD) | |
| Last_Email_Date | Date (YYYY-MM-DD) | |
| Follow_up_Count | Number (no decimals) | Default: 0 |
| Reply_Intent | Single select | |
| Reply_Summary | Single line text | |
| Last_Reply_Content | Long text | |
| Reply_Date | Date (YYYY-MM-DD) | |
| Notes | Long text | |
| Created_Date | Date (YYYY-MM-DD) | |

### 1.3 Lấy thông tin kết nối
- **Base ID**: Trong URL của Airtable `https://airtable.com/appXXXXXXXX/...` → phần `appXXXXXXXX` là Base ID
- **Personal Access Token**: Settings → Developer Hub → Personal access tokens → Create token (cấp quyền `data.records:read`, `data.records:write`)

---

## Bước 2: Setup Apollo.io API

### 2.1 Lấy API Key
1. Đăng nhập [apollo.io](https://app.apollo.io)
2. Settings → Integrations → API → **Copy API Key**

### 2.2 Cấu hình Search Criteria trong WF1
Trong node **"Set Search Config"** của WF1, chỉnh sửa `apolloConfig`:

```javascript
{
  page: 1,
  per_page: 25,
  // Chức danh muốn nhắm tới
  person_titles: ["CEO", "Founder", "CTO", "VP Sales"],
  // Địa điểm
  person_locations: ["Vietnam", "Singapore"],
  // Trạng thái email (chỉ lấy email verified)
  contact_email_status: ["verified", "likely to engage"],
  // Quy mô công ty (nhân viên)
  organization_num_employees_ranges: ["1,50", "51,200"],
  // Ngành (tìm trong Apollo để lấy đúng ID)
  // organization_industry_tag_ids: ["technology", "saas"],
  // Từ khóa (tuỳ chọn)
  // q_keywords: "SaaS startup Vietnam"
}
```

---

## Bước 3: Setup Credentials trong n8n

### 3.1 Apollo API Key (HTTP Header Auth)
1. n8n → Settings → Credentials → New → **Header Auth**
2. Name: `Apollo API Key`
3. Header Name: `X-Api-Key`
4. Header Value: `[Apollo API Key của bạn]`

### 3.2 OpenAI API
1. n8n → Settings → Credentials → New → **OpenAI**
2. Name: `OpenAI API`
3. API Key: `sk-...`

### 3.3 Airtable
1. n8n → Settings → Credentials → New → **Airtable Token API**
2. Name: `Airtable Token`
3. Access Token: `pat...` (Personal Access Token)

### 3.4 Gmail (OAuth2)
1. Vào [Google Cloud Console](https://console.cloud.google.com)
2. Tạo project mới → Enable Gmail API
3. OAuth 2.0 credentials → Desktop App
4. n8n → Settings → Credentials → New → **Gmail OAuth2**
5. Điền Client ID và Client Secret → Authorize

### 3.5 Telegram Bot
1. Tìm `@BotFather` trên Telegram
2. `/newbot` → Đặt tên → Copy Bot Token
3. Tìm Chat ID: Vào group/channel của bạn → Forward message cho `@userinfobot`
4. n8n → Settings → Credentials → New → **Telegram API**
5. Name: `Telegram Bot`
6. Bot Token: `[token từ BotFather]`

---

## Bước 4: Import Workflows vào n8n

### 4.1 Import từng workflow
1. n8n → **+** (Add workflow) → **Import from file**
2. Import theo thứ tự:
   - `WF1_lead_discovery_qualification.json`
   - `WF2_email_campaign_sender.json`
   - `WF3_followup_automation.json`
   - `WF4_reply_handler.json`

### 4.2 Cập nhật Credentials trong mỗi workflow
Sau khi import, mỗi node có dấu màu đỏ (credential chưa set):
- Click vào node → chọn credential đã tạo ở Bước 3

### 4.3 Cập nhật Airtable Base ID
Tìm tất cả Airtable nodes và thay `YOUR_AIRTABLE_BASE_ID` bằng Base ID thực của bạn.

---

## Bước 5: Cấu Hình Thông Tin Công Ty

### 5.1 Trong WF2 - Node "Prepare Email Data"
Cập nhật các biến sau:
```javascript
const myCompany = 'TÊN CÔNG TY CỦA BẠN';
const myProduct = 'mô tả sản phẩm/dịch vụ';
const myValueProp = 'giá trị mang lại cho khách hàng';
const myName = 'Tên của bạn';
const myTitle = 'Chức danh của bạn';
```

### 5.2 Trong WF3 - Node "Check Timing & Prepare Prompt"
Cập nhật tương tự.

### 5.3 Trong WF4 - Node "Extract Email Info"
```javascript
const myEmail = 'EMAIL_CUA_BAN@gmail.com'; // Email bạn dùng để gửi campaign
```

### 5.4 Cập nhật Telegram Chat ID
Trong tất cả Telegram nodes, thay `YOUR_TELEGRAM_CHAT_ID` bằng ID thực.

---

## Bước 6: Cấu Hình ICP (Ideal Customer Profile)

### 6.1 Trong WF1 - Node "Prepare AI Scoring Prompt"
Chỉnh sửa phần ICP trong prompt:
```
ICP (Ideal Customer Profile) của chúng tôi:
- Ngành: [Ngành của bạn]
- Quy mô: [Số nhân viên]
- Chức danh: [Chức danh target]
- Địa điểm: [Địa lý target]
```

---

## Bước 7: Test và Activate

### 7.1 Test WF1 (Lead Discovery)
1. **Không activate** ngay
2. Click **Execute Workflow** (nút tam giác)
3. Kiểm tra:
   - Apollo có trả về leads không?
   - AI có chấm điểm được không?
   - Airtable có nhận record không?
   - Telegram có nhận notification không?

### 7.2 Test WF2 (Email Sender)
1. Vào Airtable, thay đổi 1 lead test thành Status = `Approved`
2. Execute WF2
3. Kiểm tra Gmail có gửi email không

### 7.3 Test WF4 (Reply Handler)
1. Tự reply email test
2. WF4 sẽ trigger (chạy mỗi phút)
3. Kiểm tra Airtable có update không, Telegram có notification không

### 7.4 Activate tất cả workflows
Sau khi test OK:
- Toggle **Active** cho WF1, WF2, WF3, WF4

---

## Lịch Chạy Tự Động

| Workflow | Lịch | Hành động |
|---------|------|----------|
| WF1 | 9:00 sáng (T2-T6) | Tìm lead mới, chấm điểm, lưu CRM |
| WF2 | 10:00 sáng (T2-T6) | Gửi email cho leads đã approve |
| WF3 | 11:00 sáng (T2-T6) | Gửi follow-up cho leads cần thiết |
| WF4 | Mỗi phút | Xử lý reply emails |

---

## Quy Trình Hàng Ngày Cho Người Dùng

### 9:30 AM - Review Leads (5-10 phút)
1. Mở Telegram → Xem notifications từ WF1
2. Vào Airtable → View **"🔔 Pending Review"**
3. Với mỗi lead:
   - **Approve**: Đổi Status → `Approved`
   - **Reject**: Đổi Status → `Rejected`

### Trong ngày - Reply Interested Leads
- Khi nhận notification "🔥 HOT LEAD - QUAN TÂM!" từ WF4
- Vào Gmail, reply thread với người đó
- Không cần làm gì khác, WF4 đã update Airtable

---

## Giới Hạn Và Điều Chỉnh

### Giới hạn gửi email
- WF2 & WF3 có delay 30-45 giây giữa các email
- Gmail free: ~500 emails/ngày
- Nên giới hạn approve ≤ 20 leads/ngày để an toàn

### Điều chỉnh Follow-up intervals
Trong WF3, node **"Check Timing & Prepare Prompt"**:
```javascript
const intervals = [3, 5, 7]; // ngày
// intervals[0] = ngày sau email đầu mới gửi follow-up 1
// intervals[1] = ngày sau follow-up 1 mới gửi follow-up 2
// intervals[2] = ngày sau follow-up 2 mới gửi follow-up 3
```

### Điều chỉnh AI model
Trong các HTTP Request nodes gọi OpenAI:
- `gpt-4o-mini` = Rẻ hơn, đủ tốt cho scoring và classification
- `gpt-4o` = Tốt hơn cho viết email
- Đổi `model` parameter nếu muốn

---

## Xử Lý Lỗi Thường Gặp

### WF1: Apollo trả về 401
→ API key sai hoặc hết hạn → Kiểm tra credential Apollo

### WF1: Airtable 422 Unprocessable Entity  
→ Field name sai → Kiểm tra tên field trong Airtable khớp với workflow

### WF2/WF3: Gmail "Quota exceeded"
→ Gửi quá nhiều email → Giảm số leads approve mỗi ngày

### WF4: Không trigger khi có email
→ Kiểm tra Gmail Trigger đang Active → Kiểm tra poll time settings

### AI trả về JSON lỗi
→ OpenAI thỉnh thoảng không trả đúng format → Code nodes đã có fallback values
