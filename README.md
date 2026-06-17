# 🤖 Hệ Thống Tự Động Lead Generation & Cold Email — n8n + AI

Tự động hoá **toàn bộ vòng đời** của một chiến dịch cold email B2B: từ tìm lead → chấm điểm → gửi email cá nhân hoá → follow-up → phân loại reply. **0 thao tác tay**, chỉ cần duyệt lead mỗi sáng.

---

## Kiến Trúc Hệ Thống

```
[Apollo.io] ──→ WF1: Lead Discovery & AI Qualification
                    │
                    ▼
               [Airtable CRM] ←──── 🔔 Telegram: "Review lead mới!"
                    │
              [Human Review] ← Approve/Reject trong Airtable
                    │
                    ▼ (Status = Approved)
               WF2: Email Campaign Sender
                    │ GPT-4o viết email cá nhân hoá
                    ▼
               [Gmail] ──sends──→ [Lead's Inbox]
                    │                    │
                    ▼                    │ (reply)
               WF3: Follow-up            │
               Automation   ◄────────────┤
                    │                    │
                    │              WF4: Reply Handler
                    │                    │
                    └────────────────────┘
                                         │
                                    [AI classifies]
                                         │
                              ┌──────────┴──────────┐
                              ▼                     ▼
                    🔥 Interested             ❌ Others
                    (Priority alert)     (Auto-update CRM)
```

---

## 4 Workflows

### WF1 — Lead Discovery & AI Qualification
**Chạy:** 9:00 AM, T2–T6

```
Apollo Search → Extract Leads → Deduplicate (Airtable) 
    → AI Score (GPT-4o-mini) → Score ≥ 7? 
    → Save to Airtable + Telegram Alert
```

- Gọi Apollo API với tiêu chí tùy chỉnh (title, location, industry, headcount)
- Loại trùng với Airtable theo email + Apollo ID
- AI chấm điểm 1–10 kèm giải thích bằng tiếng Việt
- Lead dưới 7 điểm bị bỏ qua tự động
- Lead từ 7+ → lưu Airtable (Status: "Pending Review") + ping Telegram để review

### WF2 — Email Campaign Sender
**Chạy:** 10:00 AM, T2–T6

```
Get Approved Leads (Airtable) → AI Write Personalized Email (GPT-4o) 
    → Send Gmail → Update Airtable (Status: "Email Sent")
```

- Lấy tất cả leads Status = "Approved"
- GPT-4o viết email cá nhân hoá riêng cho từng người (tên, công ty, ngành, pain point)
- Gửi qua Gmail, lưu Thread ID để reply đúng thread
- Delay 30s giữa các email để tránh spam filter

### WF3 — Follow-up Automation
**Chạy:** 11:00 AM, T2–T6

```
Get Follow-up Queue (Airtable) → Check Timing → AI Write Follow-up 
    → Reply to Same Gmail Thread → Update Airtable
```

- Lịch follow-up: +3 ngày → +5 ngày → +7 ngày (tối đa 3 lần)
- AI viết email follow-up khác góc nhìn, ngắn hơn
- Email 3 = email cuối, nêu rõ đây là lần cuối liên hệ
- Gửi trong cùng thread với email gốc

### WF4 — Reply Handler & Intent Classifier
**Chạy:** Mỗi phút (polling Gmail)

```
New Email → Find Lead in Airtable → AI Classify Intent 
    → Update Status → Route to Telegram (intent-specific)
```

4 loại intent được phân loại tự động:
| Intent | CRM Status | Telegram |
|--------|-----------|---------|
| Quan tâm | Replied - Interested | 🔥 PRIORITY ALERT |
| Không quan tâm | Replied - Not Interested | ❌ Thông báo nhẹ |
| Nhầm người | Replied - Wrong Person | ⚠️ Cần tìm đúng người |
| Nghỉ phép | Replied - On Leave | 🏖️ Sẽ follow-up lại |

---

## Cấu Trúc Thư Mục

```
├── workflows/
│   ├── WF1_lead_discovery_qualification.json   # Import vào n8n
│   ├── WF2_email_campaign_sender.json
│   ├── WF3_followup_automation.json
│   └── WF4_reply_handler.json
├── config/
│   └── airtable_schema.json                    # Schema cho Airtable
├── docs/
│   └── setup_guide.md                          # Hướng dẫn setup chi tiết
└── README.md
```

---

## Credentials Cần Setup

| Service | Type trong n8n | Dùng trong WF |
|---------|---------------|--------------|
| Apollo.io | HTTP Header Auth | WF1 |
| OpenAI | OpenAI API | WF1, WF2, WF3, WF4 |
| Airtable | Airtable Token API | WF1, WF2, WF3, WF4 |
| Gmail | Gmail OAuth2 | WF2, WF3, WF4 |
| Telegram | Telegram API | WF1, WF4 |

---

## Variables Cần Thay Thế

Sau khi import workflows, tìm và thay thế:

| Placeholder | Thay bằng | Có trong WF |
|------------|----------|------------|
| `YOUR_AIRTABLE_BASE_ID` | Base ID từ URL Airtable | WF1,2,3,4 |
| `YOUR_TELEGRAM_CHAT_ID` | Chat/Group ID | WF1, WF4 |
| `YOUR_EMAIL@gmail.com` | Gmail của bạn | WF4 |
| `YOUR_REPLY_TO_EMAIL@company.com` | Email reply-to | WF2 |
| `XCONS` | Tên công ty bạn | WF2, WF3 |
| Apollo search criteria | Tiêu chí tìm lead | WF1 |
| ICP definition | Định nghĩa khách hàng lý tưởng | WF1 |

---

## Quy Trình Hàng Ngày (5 phút)

```
9:30 AM  → Mở Telegram, xem leads mới từ WF1
           Vào Airtable view "Pending Review"
           Approve hoặc Reject từng lead

Cả ngày  → Khi Telegram báo "🔥 HOT LEAD"
           Vào Gmail, reply người đang quan tâm
           
Không cần → Theo dõi inbox (WF4 đọc và phân loại tự động)
           Nhớ gửi follow-up (WF3 tự gửi đúng lịch)
           Cập nhật CRM (tất cả tự động)
```

---

## Setup

Xem hướng dẫn chi tiết tại **[docs/setup_guide.md](docs/setup_guide.md)**

**Thời gian setup:** ~45-60 phút cho người đã dùng n8n trước.

---

## Chi Phí Ước Tính / Tháng

| Service | Chi phí |
|---------|--------|
| n8n.cloud (Starter) | ~$20/tháng |
| Apollo.io (Basic) | ~$49/tháng |
| OpenAI API | ~$5-15/tháng (tùy volume) |
| Airtable | Free (đủ dùng) |
| Gmail | Free |
| Telegram | Free |
| **Tổng** | **~$75-85/tháng** |
