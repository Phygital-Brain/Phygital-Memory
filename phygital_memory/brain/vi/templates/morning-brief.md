---
type: skill
status: active
tags: [morning-brief, planning]
---

Một kế hoạch ngắn cho ngày hôm nay. Có hai chế độ: **Bản tin** (khi được yêu cầu) và **Hẹn giờ** (mỗi ngày làm việc).

## Bản tin

Câu kích hoạt: "bản tin sáng", "morning brief", hoặc câu tương tự bằng {Language}.

1. Đọc `Nhật ký/việc-cần-làm.md`, nhật ký ngày mới nhất, phần "Tình hình và bước tiếp theo" của mọi dự án có `status: active`, và các quyết định có trạng thái `open` hoặc `waiting`.
2. Nếu đã kết nối lịch, đọc các sự kiện hôm nay.
3. Trả lời trong tối đa 6 dòng ngắn:
   - 3 việc quan trọng nhất hôm nay, mỗi việc kèm `[[liên kết]]` tới ghi chú của nó.
   - {Name} đang chờ ai làm gì.
   - Một quyết định cần đưa ra, nếu có.
   - Các sự kiện hôm nay, nếu đã kết nối lịch.
4. Không viết tệp nào. Nếu {Name} phản hồi với thông tin mới, lưu lại theo quy tắc gốc 9.

## Hẹn giờ

Câu kích hoạt: "cài bản tin sáng cho mình", "set up my morning brief", hoặc câu tương tự bằng {Language}.

1. Hỏi giờ (có nút bấm: 7:00, 8:00, 9:00, 10:00), vào các ngày làm việc của {Name}. Bỏ qua câu hỏi này nếu lúc thiết lập đã chọn giờ.
2. Tạo một tác vụ chạy theo lịch trong ứng dụng trợ lý AI, chạy trên thư mục này, với prompt sau:

   > Mở thư mục bộ não thứ hai của mình. Đọc `Kỹ năng/bản-tin-sáng/bản-tin-sáng.md` và gửi mình bản tin sáng.

3. Nếu không có tác vụ chạy theo lịch, hãy dặn {Name} nói "bản tin sáng" mỗi khi bắt đầu ngày mới.
