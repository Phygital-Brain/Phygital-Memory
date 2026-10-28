---
type: skill
status: active
tags: [brain-keeper, check-up]
---

Bước kiểm tra tổng thể của Quản gia: xem kỹ toàn bộ bộ não, khi {Name} yêu cầu. Không có gì thay đổi cho tới khi {Name} đồng ý. (Việc dọn dẹp hằng ngày nằm trong `dọn-dẹp-hằng-ngày.md`.)

Câu kích hoạt: "kiểm tra bộ não của mình", "dọn dẹp bộ não của mình", "kiểm tra tổng thể bộ não", "check up my brain", "tidy my brain", "brain check-up", hoặc câu tương tự bằng {Language}.

## 1. Xem xét (chưa đổi gì)

Tìm khắp thư mục và liệt kê các vấn đề theo những nhóm sau:

- **Liên kết hỏng**: `[[liên kết]]` trỏ tới ghi chú không tồn tại. Không bao giờ sửa bằng cách tạo một ghi chú trống: ghi chú thật có thể vẫn đang đồng bộ (quy tắc gốc 28).
- **Ghi chú mồ côi**: ghi chú không được ghi chú nào khác liên kết tới.
- **Ghi chú trống hoặc gần như trống**, và các chỗ giữ chỗ còn sót (`[name]`, `TBD`).
- **Sai chỗ**: tệp nằm ở thư mục gốc (trừ `CLAUDE.md`, `.claudeignore`, `.backups/` và tệp quy tắc một dòng của một trợ lý AI khác, như `AGENTS.md`), ghi chú không khớp với bảng Cái gì để ở đâu của thư mục chứa nó.
- **Bảng Cái gì để ở đâu bị lỗi thời**: một `CLAUDE.md` ghi những tệp hay thư mục không tồn tại, hoặc thiếu những cái đang có (các dòng có ghi "tạo khi dùng lần đầu" thì không sao).
- **Khối thông tin**: thiếu hoặc chưa đủ, so với `CLAUDE.md` của thư mục. Không có `status:`, ít hơn 2 `tags:`, ghi chú dự án không có `project:`, thẻ nhật ký ngày nằm ngoài danh sách cố định.
- **Dự án bị bỏ quên**: không cập nhật từ 60 ngày trở lên. Gợi ý cập nhật tình hình, đặt `paused`, hoặc lưu trữ.
- **Mục tiêu bị bỏ rơi**: mục tiêu trong `Hồ sơ/mục-tiêu.md` không có dự án nào đang chạy.
- **Quyết định cần xem lại**: `updated` đã quá 30 ngày và trạng thái chưa phải `closed`.
- **Mối quan hệ cũ**: `status: active` nhưng `last-contact` đã quá 12 tháng. Gợi ý đổi thành `dormant`.
- **Việc cũ**: việc chưa xong trong `Nhật ký/việc-cần-làm.md` đã quá 30 ngày.
- **Trùng lặp**: cùng một thông tin ở nhiều ghi chú, hoặc hai ghi chú cho cùng một người hay công ty.
- **Hiện trạng bị lỗi thời**: các trang Hồ sơ hoặc Danh bạ mà cập nhật cũ đè lấp tình hình hiện tại (quy tắc gốc 17).
- **Quy tắc mâu thuẫn**: các quy tắc trong `CLAUDE.md` gốc nói ngược nhau.
- **Riêng tư**: mật khẩu, khóa hay con số riêng tư nằm trong ghi chú bình thường (quy tắc gốc 25 và 26). Báo tên ghi chú, không bao giờ báo giá trị.
- **Câu chữ**: dấu gạch ngang dài và các kiểu viết trong phần Kiểm tra câu chữ có trong ghi chú.
- **Phiên bản mới**: so sánh phiên bản của bộ não này (dòng đầu tiên của `CLAUDE.md` gốc) với phiên bản Phygital Brain mới nhất. Nếu bạn lướt web được, bản mới nhất là bản phát hành gần nhất tại https://github.com/Phygital-Brain/phygital-brain/releases/latest. Nếu không, dùng phiên bản Phygital Brain đã cài trong trợ lý AI của bạn, nếu bạn xem được. Nếu không biết chắc, bỏ qua mục này.

## 2. Báo cáo

Một danh sách ngắn bằng lời dễ hiểu, chia nhóm như trên. Với mỗi vấn đề: ghi chú nào, sai ở đâu, bạn gợi ý sửa thế nào. Đưa những chỗ sửa đơn giản, an toàn lên đầu (dấu gạch ngang dài, thiếu thẻ, dòng trong bảng Cái gì để ở đâu).

Nếu đã có phiên bản mới hơn, mở đầu báo cáo bằng một dòng. Nếu trợ lý AI của bạn đã có bản đó: "Phygital Brain đã có phiên bản mới. Hãy nói 'nâng cấp bộ não thứ hai của mình' (Upgrade my second brain) để xem có gì mới." Nếu chưa: "Phygital Brain đã có phiên bản mới. Hãy cập nhật nó trong trợ lý AI của bạn trước, rồi nói 'nâng cấp bộ não thứ hai của mình' (Upgrade my second brain)."

## 3. Chỉ sửa những gì được duyệt

Trước lần sửa đầu tiên, sao lưu mọi tệp bạn sẽ sửa (Sao lưu và hoàn tác trong `CLAUDE.md` gốc).

Hỏi (có nút bấm nếu được): **Sửa hết những chỗ an toàn**, **Đi từng chỗ một**, **Chỉ cần báo cáo**.

- Không bao giờ xóa hay di chuyển khi chưa kiểm tra liên kết và chưa có câu đồng ý rõ ràng (quy tắc gốc 21).
- Khi còn phân vân, lưu trữ thay vì xóa.
- Ghi một dòng vào ghi chú hôm nay trong `Nhật ký/`: đã kiểm tra gì và sửa gì.
