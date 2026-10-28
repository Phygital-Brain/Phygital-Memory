Mỗi dự án là một thư mục lớn dần theo thông tin mới. `README.md` là cửa vào duy nhất.

## Cái gì để ở đâu

| Nội dung | Để ở |
|---|---|
| Tổng quan, tình hình, hạn chót, bước tiếp theo | `Dự án/{name}/README.md` |
| Ghi chú làm việc của {Name} | `Dự án/{name}/ghi-chú/{topic}.md` |
| Nghiên cứu | `Dự án/{name}/nghiên-cứu/{topic}.md` |
| Brief, bản mô tả kỹ thuật, yêu cầu | `Dự án/{name}/brief/{name}.md` |
| Bản nháp, kịch bản, nội dung viết | `Dự án/{name}/bản-nháp/{name}.md` |
| Ý tưởng | `Dự án/{name}/ý-tưởng/{name}.md` |
| Góp ý | `Dự án/{name}/góp-ý/{name}.md` |
| Hình ảnh và video | `Dự án/{name}/hình-ảnh-video/` |
| Tài liệu cũ của dự án này | `Dự án/{name}/lưu-trữ/` |

Tên thư mục viết chữ thường, nối bằng gạch nối, không đánh số ở đầu (`nghiên-cứu/`, không phải `01-Nghiên-cứu/`). Một dự án có thể thêm thư mục riêng khi không thư mục nào ở trên phù hợp.

## Bố cục README

1. Khối thông tin (bên dưới), có `description`.
2. `## Dự án này là gì`: một hoặc hai dòng, liên kết tới [[mục-tiêu]].
3. `## Tình hình và bước tiếp theo`: dự án đang ở đâu, bước tiếp theo là gì.
4. `## Cách vận hành`: chỉ khi có thứ gì tự động viết vào đây (một tác vụ chạy theo lịch, một đoạn script).
5. `## Mọi thứ nằm ở đâu`: chỉ khi đã có thư mục con. Một bảng nhỏ liên kết tới từng thư mục.

## Khối thông tin (frontmatter)

```yaml
---
type: notes
date: 2026-10-13
status: active
project: Website-Redesign
tags: [website-redesign, notes]
---
```

- `type`: `project` (README, có thêm `created`, `updated` và `description`), `notes`, `research`, `brief`, `draft`, `idea`, `feedback`, `plan`.
- `status`: `active`, `paused` hoặc `done`. Trạng thái của README là trạng thái của dự án.
- `project`: tên thư mục dự án.
- `tags`: tên dự án, rồi tới loại ghi chú.

## Quy tắc

- Một dự án mới chỉ có một tệp `README.md`. Chỉ tạo thư mục con khi có nội dung cần đến nó, và liên kết thư mục đó từ README.
- README là mục lục. Đừng lặp lại nội dung của thư mục con trong đó.
- Không có `CLAUDE.md` bên trong một dự án. Quy tắc riêng cho một dự án để ở phần "Quy tắc riêng từng dự án" bên dưới.
- Thêm `project:` vào khối thông tin của mọi ghi chú liên quan.
- Một dự án đã xong chỉ được chuyển vào `Trí nhớ/lưu-trữ/{name}/` khi {Name} bảo.
- Dự án nào cũng nên phục vụ một mục tiêu trong [[mục-tiêu]]. Khi kiểm tra tổng thể, đánh dấu những mục tiêu không có dự án và những dự án không có mục tiêu.

## Quy tắc riêng từng dự án

<!-- Rules for one project only. Add a line when a project needs its own rule: "**Project-Name:** the rule." -->
