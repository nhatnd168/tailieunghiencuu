import Anthropic from "@anthropic-ai/sdk";
import fs from "fs";

const problem = process.argv[2];

if (!problem) {
  console.error("Cách dùng: node solver.js \"<mô tả vấn đề kinh doanh>\"");
  process.exit(1);
}

const client = new Anthropic();

const pdfFiles = [
  "BSC-OKR_2026_XCONSe&c_ban_hanh_030326_R1.pdf",
  "KẾ HOẠCH KPI DOANH THU VÀ SẢN LƯỢNG NĂM 2026.pdf",
];

const documents = [];
for (const file of pdfFiles) {
  if (fs.existsSync(file)) {
    const data = fs.readFileSync(file).toString("base64");
    documents.push({
      type: "document",
      source: { type: "base64", media_type: "application/pdf", data },
    });
  }
}

const userContent = [
  ...documents,
  {
    type: "text",
    text: `Vấn đề kinh doanh cần phân tích:\n\n${problem}`,
  },
];

console.log("Đang phân tích vấn đề...\n");

const stream = client.messages.stream({
  model: "claude-opus-4-8",
  max_tokens: 8192,
  thinking: { type: "adaptive" },
  system: `Bạn là chuyên gia tư vấn kinh doanh và chiến lược doanh nghiệp người Việt Nam.
Khi được cung cấp tài liệu kế hoạch kinh doanh, hãy sử dụng chúng làm ngữ cảnh để phân tích vấn đề.
Hãy trả lời bằng tiếng Việt, có cấu trúc rõ ràng với các mục:
1. Tóm tắt vấn đề
2. Phân tích nguyên nhân gốc rễ (Root Cause Analysis)
3. Tác động đến KPI và mục tiêu (nếu có tài liệu liên quan)
4. Giải pháp đề xuất (ngắn hạn và dài hạn)
5. Kế hoạch hành động cụ thể
Hãy cụ thể, thực tế và có tính khả thi cao.`,
  messages: [{ role: "user", content: userContent }],
});

stream.on("text", (text) => {
  process.stdout.write(text);
});

await stream.finalMessage();
console.log("\n");
