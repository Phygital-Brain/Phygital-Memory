<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the `clients` tag line if BUSINESS = off.
-->

Nhật ký hằng ngày của {Name}. Mỗi ngày một tệp: `YYYY-MM-DD.md`. Việc cần làm nằm trong `việc-cần-làm.md`.

## Khối thông tin (frontmatter)

Mọi nhật ký ngày đều bắt đầu bằng khối này. Không có ngoại lệ.

```yaml
---
type: daily
date: 2026-10-13
day: Tuesday
week: W42
month: October
status: active
tags: [daily, meeting]
---
```

- `type`: luôn là `daily`.
- `date`: ngày của ghi chú, dạng `YYYY-MM-DD`.
- `day`: thứ trong tuần, bằng tiếng Anh (Monday, Tuesday...).
- `week`: số tuần theo ISO, dạng `WNN`.
- `month`: tháng, bằng tiếng Anh (January, February...).
- `status`: `active` khi ngày đó còn đang mở, `completed` khi đã qua từ 2 ngày trở lên.
- `tags`: luôn có `daily`, cộng thêm những thẻ trong danh sách cố định này nếu chuyện đó có xảy ra trong ngày. Không bao giờ tự đặt thẻ khác.
  - `problem`: có gì hỏng hoặc trục trặc
  - `clients`: làm việc cho khách hàng hoặc liên lạc với khách hàng
  - `meeting`: một cuộc gọi hoặc cuộc họp
  - `money`: hóa đơn, thanh toán, thuế, đầu tư
  - `research`: có tìm hiểu hoặc có phát hiện mới
  - `decision`: {Name} đã quyết định một chuyện
  - `travel`: {Name} đang đi xa
  - `personal`: sức khỏe, đời sống, mọi thứ ngoài công việc

## Quy tắc

- Ngày tháng theo quy tắc gốc 30 (múi giờ của máy tính trước, rồi tới {Time zone}).
- Ai tạo ghi chú (trợ lý AI của bạn hay một tác vụ chạy theo lịch) thì viết khối thông tin trước tiên. Ghi chú nào chưa có khối thông tin thì được thêm vào trên cùng ở lần sửa tiếp theo.
- Không có tiêu đề `# YYYY-MM-DD`. Tên tệp chính là tiêu đề.
- Nhật ký ngày giữ tình hình hiện tại của ngày đó: mỗi ngày một tài liệu gọn gàng, các phần được cập nhật tại chỗ, không bao giờ là một đống mục lặp đi lặp lại.
- Nhật ký phiên làm việc: một tiêu đề in đậm và 1 hoặc 2 câu, người và dự án viết thành `[[wikilink]]`, chi tiết để trong ghi chú được liên kết.
- Nhật ký hôm nay chỉ ghi việc của hôm nay. Việc cần làm từ những ngày trước để trong `việc-cần-làm.md`. Không bao giờ chép chúng sang ngày mới.
- Khi tạo nhật ký hôm nay, xem các ghi chú của 2, 3 và 4 ngày trước. Ghi chú nào vẫn `status: active` thì đổi thành `completed`, và gắn thẻ trong danh sách cố định cho những gì rõ ràng đã xảy ra hôm đó. Không xem xa hơn.

## `việc-cần-làm.md`

Những việc cần làm không thuộc dự án nào. Việc của một dự án để trong README của dự án đó ("Tình hình và bước tiếp theo"). Tạo khi dùng lần đầu:

```markdown
---
type: tasks
status: active
tags: [tasks, daily]
---

## Chưa xong

- [ ] 2026-10-13: Gửi hóa đơn cho [[Lan]]

## Đã xong

- [x] 2026-10-12: Đặt lịch khám răng (xong 2026-10-13)
```

- Việc chưa xong mới nhất ở trên cùng, kèm ngày thêm vào.
- Khi xong một việc, đánh dấu tick, thêm ngày hoàn thành, và chuyển nó xuống `## Đã xong`.
- Việc đã xong quá 30 ngày có thể xóa đi (hỏi trước, quy tắc gốc 9).
