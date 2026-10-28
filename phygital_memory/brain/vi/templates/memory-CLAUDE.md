Những hiểu biết tích lũy dần theo thời gian: quyết định, nghiên cứu, hồ sơ ứng tuyển và kho lưu trữ.

## Cái gì để ở đâu

| Nội dung | Để ở |
|---|---|
| Quyết định kèm lý do, hoặc một lần tìm hiểu thứ bên ngoài (ứng dụng, website, khóa học, đối thủ) | `quyết-định/YYYY-MM-DD-{title}.md` |
| Nghiên cứu (thị trường, xu hướng, các lựa chọn) | `nghiên-cứu/{topic}.md` |
| Ứng tuyển: việc làm, quỹ tài trợ, giải thưởng, open call (tạo khi dùng lần đầu) | `ứng-tuyển/{name}/` |
| Hồ sơ đối thủ (tạo khi dùng lần đầu) | `đối-thủ/{name}.md` |
| Tiền bạc: hóa đơn, thuế, thanh toán. Riêng tư | `tài-chính/` |
| Quyết định đã lưu trữ | `lưu-trữ/quyết-định/` |
| Nghiên cứu đã xong hoặc đã cũ | `lưu-trữ/nghiên-cứu/` |
| Dự án đã xong | `lưu-trữ/{name}/` |
| Ghi chú cuộc họp | `quyết-định/` nếu cuộc họp đưa ra quyết định, nếu không thì để trong nhật ký `Nhật ký/` của ngày hôm đó. Chỉ gợi ý tạo thư mục riêng cho cuộc họp khi đã có rất nhiều. |

## Khối thông tin (frontmatter)

```yaml
---
type: research
date: 2026-10-13
status: active
tags: [research, pricing]
---
```

- `type`: `decision`, `research`, `application`, `competitor`.
- `date`: ngày viết ghi chú.
- `status`: với quyết định và hồ sơ ứng tuyển, xem bên dưới. Mọi loại khác: `active` hoặc `closed`.
- `tags`: loại ghi chú, rồi tới chủ đề.
- Không bắt buộc: `project`, `deadline`, `description` (một câu, trong dấu ngoặc kép, ở dòng cuối).

## Ghi chú quyết định

Luôn ghi lý do: những ai tham gia, điều gì dẫn tới quyết định, đã chấp nhận đánh đổi gì. Dùng `> [!important]` cho chính quyết định và `> [!warning]` cho những rủi ro đã biết.

Quyết định còn có thêm `updated:` ngay sau `date:`. `date` là ngày tạo, `updated` là lần gần nhất được xem lại hoặc thay đổi.

```yaml
---
type: decision
date: 2026-09-02
updated: 2026-10-13
status: open
tags: [decision, website]
---
```

- `status`: `open` (vẫn đang cân nhắc hoặc đang làm), `waiting` (đang chờ người khác), `paused`, `closed`.
- Quyết định nào có `updated` đã quá 30 ngày thì cần xem lại. Quản gia sẽ đánh dấu nó cho tới khi {Name} giữ lại, đóng lại hoặc lưu trữ (mỗi cách đều đặt `updated` thành ngày hôm đó).
- Một quyết định chỉ được chuyển vào `lưu-trữ/quyết-định/` khi {Name} bảo.

## Ứng tuyển

Mỗi lần ứng tuyển một thư mục: `ứng-tuyển/{name}/`, với một `README.md` ghi hạn chót, đường link, trạng thái và những gì đã gửi. Các tệp khác (câu trả lời, bài giới thiệu) để ngay bên cạnh.

- `status`: `draft`, `submitted`, `accepted`, `rejected` hoặc `withdrawn`.
- Giữ câu trả lời ở dạng markdown. PDF lớn và slide để ngoài bộ não: tóm tắt chúng trong một ghi chú.

## Quy tắc

- Nghiên cứu mặc định là trung lập (quy tắc gốc 23).
- Nghiên cứu đã bị thay thế thì chuyển vào `lưu-trữ/nghiên-cứu/` thay vì xóa.
- `tài-chính/` là riêng tư và có trong `.claudeignore`. Chỉ mở khi {Name} yêu cầu một tệp cụ thể (quy tắc gốc 8).
