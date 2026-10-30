# Thay đổi thiết kế – Buổi 10

Các thay đổi dưới đây chỉ bổ sung hành vi nằm trong phạm vi được phép ở Prompt Copilot Buổi 10. Lược đồ sáu bảng trong `db/schema.sql` được giữ nguyên.

## TD-01 – Bổ sung API xác thực và truy vấn phiếu

- **Phản hồi:** Buổi 10 yêu cầu đăng nhập, `/api/auth/me`, chi tiết phiếu và lịch hẹn theo phiếu; SRS hiện chỉ đặc tả bảy endpoint nghiệp vụ.
- **Quyết định:** **SỬA** – bổ sung hai endpoint auth, endpoint chi tiết phiếu và danh sách lịch hẹn; mở rộng danh sách phiếu với lọc và phân trang.
- **Lý do:** Đây là các endpoint được cho phép rõ ràng trong prompt để ba màn hình dùng API thật.
- **Ảnh hưởng:** Phản hồi dùng snake_case, phân quyền theo trung tâm/kỹ thuật viên và trả lỗi có mã. Không thêm bảng hay cột.

## TD-02 – Tài khoản demo không thêm bảng

- **Phản hồi:** ERD L04 có đúng sáu bảng, không có bảng nhân viên/tài khoản.
- **Quyết định:** **GIỮ** ERD; tài khoản demo được tạo trong `data/processed/demo_accounts.json`, mật khẩu lấy từ `DEMO_PASSWORD` và lưu ở dạng PBKDF2 hash.
- **Lý do:** Đáp ứng đăng nhập demo mà không thay đổi schema hoặc lưu mật khẩu rõ.
- **Ảnh hưởng:** Tệp JSON là dữ liệu sinh cục bộ, được `.gitignore`; `SECRET_KEY` phải có tối thiểu 32 ký tự. Chưa có tài khoản chạy thật vì chưa thể nạp dữ liệu vào PostgreSQL trong môi trường hiện tại.

## TD-03 – Ánh xạ và loại dòng dữ liệu

- **Phản hồi:** Prompt giả định status đầu vào có dấu; CSV thực tế trong repo đã dùng mã không dấu. `tickets_history.customer_id` thực tế nối đủ 7.800/7.800 dòng với `customers_raw.record_id`.
- **Quyết định:** **SỬA** – giữ nguyên status đã chuẩn hóa và chấp nhận thêm các alias có dấu nêu trong prompt; ánh xạ category qua `category_id` → `category_name`; chuẩn hóa số điện thoại về dạng `0xxxxxxxxx`.
- **Lý do:** Dùng đúng giá trị quan sát được trong CSV, không thay dữ liệu nguồn bằng dữ liệu tự tạo.
- **Ảnh hưởng:** Phiếu không có số điện thoại hợp lệ được ghi kèm lý do vào `data/rejects/tickets_rejected.csv`; không sửa schema. Bộ xử lý `ticket_status_log.csv` và `appointments.csv` chưa hoàn tất vì các nguồn tương ứng chưa có để xác minh header và quy tắc mapping.

## TD-04 – Đường dẫn wireframe thực tế

- **Phản hồi:** Prompt tham chiếu `docs/diagrams/wireframe.drawio`; tệp hiện có ở `docs/wireframe.drawio`.
- **Quyết định:** **GIỮ** cấu trúc thư mục hiện tại; đọc/dùng wireframe ở vị trí thực tế, không di chuyển tệp đã nộp.
- **Lý do:** Tránh thay đổi cấu trúc dự án nếu chưa có yêu cầu riêng.
- **Ảnh hưởng:** Các nhãn M1/M2/M3 và ngoại lệ được triển khai dựa trên tệp wireframe đang có.

## TD-05 – Phạm vi giao diện và quy tắc xung đột trạng thái

- **Phản hồi:** UC8 là mức COULD và nằm ngoài wireframe; wireframe không cung cấp thao tác hủy lịch hẹn. EX-8.1 minh họa chuyển lùi, trong khi API contract chỉ nhận các trạng thái đích hợp lệ của vòng đời.
- **Quyết định:** **GIỮ** – không thêm màn hình UC8 hoặc nút hủy lịch; API từ chối chuyển trạng thái sai chiều với thông báo “Không thể chuyển từ X sang Y”.
- **Lý do:** Bám sát phạm vi L04 và API contract thay vì tạo hành vi mới.
- **Ảnh hưởng:** Lịch hẹn vẫn tuân quy tắc QT-13 ở schema; UI không bổ sung thao tác ngoài wireframe.

## TD-06 – Hạn chế nguồn dữ liệu và phạm vi kiểm chứng

- **Phản hồi:** `data/raw/` thiếu `ticket_status_log.csv`; repo cũng không có `gen_sample.py`/`tools/gen_sample.py` hoặc `appointments.csv`. PostgreSQL không chạy/không kết nối được khi kiểm tra.
- **Quyết định:** **GIỮ** – seed mặc định dừng trước khi ghi dữ liệu nếu pipeline không thể bảo đảm nhập đủ log và lịch hẹn; `--allow-incomplete` chỉ dành cho nạp bảng lõi và trả mã thoát không thành công để tránh hiểu nhầm là dữ liệu hoàn chỉnh.
- **Lý do:** Prompt yêu cầu dữ liệu thật, không cho tạo vài dòng giả và yêu cầu không tuyên bố test PASS khi không chạy được.
- **Ảnh hưởng:** Báo cáo nạp dữ liệu đánh dấu chưa nạp; TC01–TC18, ảnh kiểm thử, reset và clone sạch chưa được xác minh.
