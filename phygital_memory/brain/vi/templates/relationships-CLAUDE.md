<!-- ADAPTING (for the agent, leave this comment out of the file):
Remove the "Where a new lead goes" section if there's no `Khách hàng/` folder. Remove subfolder rows that weren't created.
Each subfolder gets its own `CLAUDE.md` from `relationships-subfolder-CLAUDE.md`.
-->

Tất cả những người {Name} làm việc cùng: mỗi người hoặc tổ chức một ghi chú.

## Thư mục con

| Thư mục | Ai để ở đây |
|---|---|
| `Khách hàng/` | Người và công ty mà {Name} làm việc cho |
| `Cộng sự/` | Bạn đồng hành sáng tạo, trao đổi qua lại, không dính tới tiền |
| `Nhóm/` | Những người làm cùng hoặc làm cho {Name} (freelancer, trợ lý) |
| `Đối tác/` | Những tổ chức giúp {Name} có mặt và được biết đến (báo chí, địa điểm, nền tảng) |

## Khách tiềm năng mới để ở đâu

- Lần liên hệ đầu tiên, chưa có brief thật: một dòng dưới `## Mới` trong `Khách hàng/_Khách-tiềm-năng.md` (tạo khi dùng lần đầu).
- Một câu trả lời kiểu "để sau nhé": một dòng dưới `## Giữ liên lạc` trong `Khách hàng/_Khách-tiềm-năng.md`.
- Đã có brief thật, có cuộc gọi hoặc đang báo giá: một ghi chú khách hàng `Khách hàng/{client-name}.md` với `status: prospect`.

Khi một khách tiềm năng tiến thêm một bước, chuyển họ sang chỗ tiếp theo và xóa khỏi chỗ cũ.

## Khối thông tin (frontmatter)

Mọi ghi chú ở đây (trừ các tệp `CLAUDE.md` và `_Khách-tiềm-năng.md`) đều bắt đầu bằng:

```yaml
---
type: client
status: active
last-contact: 2026-10
tags: [relationship, client, fashion, brazil]
description: "Một câu đơn giản nói họ là ai và mối quan hệ với {Name}."
---
```

- `type`: `client`, `collaborator`, `team` hoặc `partner`.
- `status`: `active` (có làm việc hoặc liên lạc trong 12 tháng qua), `prospect` (đang trao đổi, chưa từng làm cùng), `dormant` (không liên lạc từ 12 tháng trở lên), `closed` (đã dừng hẳn).
- `last-contact`: tháng gần nhất có liên lạc hay làm việc thật sự, dạng `YYYY-MM`. Để trống nếu không biết.
- `tags`: `relationship`, rồi loại, rồi 2 đến 5 thẻ chủ đề (ngành, quốc gia, loại công việc), bằng tiếng Anh, chữ thường, nối bằng gạch nối.
- `description`: một câu, trong dấu ngoặc kép. Luôn là dòng cuối.
- Không bắt buộc: `aliases` (những tên khác dùng để gọi họ), `project` (dự án hiện tại).

## Quy tắc

- **Không trùng lặp.** Trước khi tạo ghi chú, tìm tên đó và các cách viết khác (có dấu, không dấu, tên ngắn, tên thương hiệu và tên công ty). Nếu đã có ghi chú, dùng nó và thêm cách viết mới vào `aliases`. Không bao giờ tạo ghi chú thứ hai cho cùng một người hay công ty.
- **Định dạng "hiện trạng ở trên, căn cứ ở dưới"** (quy tắc gốc 17): họ là ai và tình hình hiện tại ở trên cùng, lịch sử có ghi ngày ở bên dưới.
- **Luôn cập nhật.** Khi {Name} có liên lạc thật với ai đó (một email, một cuộc gọi, giao một sản phẩm), cập nhật `last-contact` thành tháng này, và cả `status` nếu nó thay đổi.
- **Người liên hệ** ở một công ty (người đại diện, quản lý, biên tập viên) được viết thành chữ trơn bên trong ghi chú của công ty, không bao giờ là `[[liên kết]]`, và không có ghi chú riêng. Muốn nhắc tới họ ở chỗ khác, hãy liên kết tới công ty: `[[Tên công ty|Tên người liên hệ]]`.
- **Thông tin riêng tư** (số điện thoại, email, địa chỉ nhà) chỉ nằm trong ghi chú của chính người hoặc công ty đó. Không bao giờ chép sang nhật ký ngày hay ghi chú khác.
- Liên kết tới người từ dự án và nhật ký ngày bằng `[[wikilink]]`.
- Chỉ tạo thư mục con mới khi xuất hiện một kiểu quan hệ mới. Hỏi trước.
