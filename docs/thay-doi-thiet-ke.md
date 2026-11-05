# Thay đổi thiết kế – Buổi 10

Các thay đổi thiết kế phát sinh khi hiện thực Sprint 2 (Buổi 10), mỗi mục ghi vấn đề, quyết định (SỬA/GIỮ), lý do và ảnh hưởng. Lược đồ sáu bảng trong `db/schema.sql` được giữ nguyên.

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
- **Cập nhật (đã giải quyết):** `ticket_status_log.csv` được bổ sung từ bộ dataset vào `data/raw/`; lịch hẹn sinh bằng `scripts/gen_appointments.py` (TD-09). Pipeline `load_catalog` → `load_tickets` → `load_appointments` thay cho seed cũ (đã chuyển sang `scripts/legacy/`) và đã nạp đủ sáu bảng (xem TD-07, TD-08, `docs/bao-cao-nap-du-lieu.md`). TC01–TC18 vẫn chưa được viết (TD-15).

## TD-07 – Loại phiếu thiếu số điện thoại hợp lệ

- **Vấn đề phát hiện:** Có 483 phiếu (6,2% của 7.800) không có `customer_phone` hợp lệ trong tập dữ liệu nguồn.
- **Quyết định:** **SỬA** – loại 483 phiếu vì `customer_phone` là NOT NULL và bắt buộc khớp QT-02 (`^0[0-9]{9}$`); không tạo số điện thoại giả. Loại kèm 2.363 dòng trong `ticket_status_log`.
- **Lý do:** Không thể nạp hợp lệ các phiếu thiếu dữ liệu bắt buộc mà không vi phạm schema và QT-02.
- **Ảnh hưởng:** Kết quả nạp giữ 7.317 phiếu và 35.719 dòng log.

## TD-08 – Seed phiếu MOI 20260901

- **Vấn đề phát hiện:** Cần tạo tập MOI ổn định để phục vụ demo seed `20260901`.
- **Quyết định:** **SỬA** – chọn 30 phiếu MOI, mỗi trung tâm 5 phiếu, từ pool 227 phiếu `DA_PHAN_CONG` hợp lệ; lưu danh sách tại `reports/moi_tickets_seed20260901.csv`. Cắt log từ thời điểm chuyển sang `DA_PHAN_CONG` để lịch sử kết thúc ở `MOI`.
- **Lý do:** Tập mẫu cố định giúp lặp lại được seed và lịch sử không còn trạng thái sau `MOI`.
- **Ảnh hưởng:** Không thêm dòng chuyển `DA_PHAN_CONG -> MOI`, vì vi phạm QT-06.

## TD-09 – Sinh lịch hẹn thay thế gen_sample.py

- **Vấn đề phát hiện:** `gen_sample.py` có thể sinh dữ liệu không tương thích schema và không mô phỏng quy tắc L04.
- **Quyết định:** **GIỮ** schema hiện tại và sử dụng `scripts/gen_appointments.py` cho seed `20261102`; sinh 300 lịch gồm 270 `DA_HEN` và 30 `DA_HUY`, từ 2026-11-03 đến 2027-01-30, thứ Hai–thứ Bảy, khung 08:00–17:30 theo slot 30 phút, từ pool 943 phiếu `DA_PHAN_CONG`/`DANG_XU_LY`/`CHO_LINH_KIEN`; `appointment.technician_id` phải bằng `ticket.technician_id`.
- **Lý do:** `gen_sample.py` sinh các status `DA_DAT`, `DA_XAC_NHAN`, `HOAN_TAT`, `KHACH_HUY`, `KHACH_KHONG_DEN`, các loại không có trong schema và khung 2 giờ; thiếu các trường bắt buộc; gắn KTV/trung tâm ngẫu nhiên độc lập; không chống trùng lịch và không lọc trạng thái phiếu. Schema chỉ nhận `DA_HEN`/`DA_HUY` và `GIAO`/`NHAN`.
- **Ảnh hưởng:** Tệp mẫu được giữ tại `data/sample/appointments.csv`; dữ liệu sinh tuân đúng trạng thái, loại lịch, khoảng thời gian, pool phiếu và KTV của phiếu.

## TD-10 – Không tạo lịch cho phiếu HOAN_TAT

- **Vấn đề phát hiện:** Để tạo lịch cho phiếu cần kiểm tra điều kiện trạng thái của SRS UC6 và cách đối chiếu với tiêu chí GWT trong tài liệu L04.
- **Quyết định:** **GIỮ** – không tạo lịch cho phiếu `HOAN_TAT`.
- **Lý do:** SRS UC6 chỉ cho phép đặt lịch từ trạng thái `DA_PHAN_CONG` trở đi nhưng không bao gồm sau khi hoàn tất.
- **Ảnh hưởng:** `L04_TieuChi_GWT EX-7.3` hiện mới chỉ từ chối `MOI`, `DA_DONG`, `DA_HUY` và đang mâu thuẫn SRS; điểm này cần sửa ở BT3.

## TD-11 – Chuẩn hoá kiểu dữ liệu nạp

- **Vấn đề phát hiện:** Một số trường nguồn có kiểu/xuất dữ liệu không khớp lược đồ PostgreSQL hoặc cần ánh xạ danh mục qua mã.
- **Quyết định:** **SỬA** – ép trực tiếp `changed_by` sang BIGINT khi cả 60 giá trị quan sát đều là số nguyên; kiểm tra rồi chuyển kiểu `is_active`, `proficiency` trong khoảng 1..5 và `level`. Ánh xạ `category_id` sang `category_code` bằng `issue_categories.csv`.
- **Lý do:** Các phép đổi kiểu phải được kiểm chứng trước khi nạp, tránh tạo dữ liệu ngoại lệ hoặc giá trị giả.
- **Ảnh hưởng:** Giảm lỗi ép kiểu khi nạp và bảo đảm danh mục phiếu có mã category đúng schema.

## TD-12 – Cô lập integration trên PostgreSQL

- **Vấn đề phát hiện:** Test ghi nghiệp vụ có thể thay đổi dữ liệu `smartcrm` hoặc dữ liệu chuẩn `smartcrm_test`.
- **Quyết định:** **SỬA** – test chỉ đọc chạy trên `smartcrm_test`; test ghi tạo lại database cố định `smartcrm_work_test` từ template `smartcrm_test` trước mỗi test. Guard chỉ cho phép tên database làm việc chính xác `smartcrm_work_test` và test cổng từ chối các tên không kết thúc bằng `_test`.
- **Lý do:** Mỗi test ghi cần dữ liệu nguồn ổn định, có thể lặp lại, đồng thời bảo vệ database dữ liệu thật.
- **Ảnh hưởng:** Fixture cần kết nối bảo trì tới database `postgres`, dispose engine SQLAlchemy trước DROP/CREATE và kiểm tra số dòng `smartcrm_test`/`smartcrm` trước và sau phiên kiểm thử.

## TD-13 – Bộ lọc trạng thái ở M3 "Phiếu của tôi"

- **Vấn đề phát hiện:** Chạy luồng chính trên dữ liệu thật, mỗi kỹ thuật viên giữ trung bình 192 phiếu (tối đa 443), phần lớn đã `DA_DONG`. M3 liệt kê tất cả, không lọc được; frontend thiếu nhãn cho `DA_DONG`/`DA_HUY` nên hiện mã thô.
- **Quyết định:** **SỬA** – thêm ô lọc "Trạng thái" phía giao diện (Tất cả · Đang làm · Hoàn tất · Đã đóng · Đã hủy), mặc định Tất cả; bổ sung nhãn tiếng Việt cho mọi trạng thái. **GIỮ** API `GET /api/technicians/me/tickets` trả đủ phiếu của chính kỹ thuật viên.
- **Lý do:** Kỹ thuật viên vẫn có quyền xem phiếu đã đóng/đã hủy của chính mình, nhưng không được xem phiếu của tài khoản khác. Lọc giúp tìm phiếu cần làm mà không ẩn dữ liệu.
- **Ảnh hưởng:** Không đổi API hay schema. Quy tắc phạm vi xem phiếu có unit test (`tests/test_ticket_rules.py`); test e2e kiểm số dòng lọc "Đã đóng" bằng đúng số phiếu `DA_DONG` của kỹ thuật viên trong DB.

## TD-14 – Tách quy tắc nghiệp vụ khỏi router

- **Vấn đề phát hiện:** Quy tắc vòng đời trạng thái, điều kiện kỹ thuật viên (tay nghề ≥ 3, cùng trung tâm, đang làm việc), điều kiện đổi kỹ thuật viên và phạm vi xem phiếu nằm lẫn với SQL trong `routers/tickets.py`, nên chỉ kiểm được khi có PostgreSQL.
- **Quyết định:** **SỬA** – chuyển các quy tắc thành hàm thuần trong `src/backend/app/services/ticket_rules.py`; router chỉ đọc/ghi dữ liệu và gọi các hàm này.
- **Lý do:** Unit test cho lớp nghiệp vụ không cần cơ sở dữ liệu (yêu cầu Buổi 10).
- **Ảnh hưởng:** Phản hồi API giữ nguyên (mã lỗi, thông báo, thứ tự kiểm tra); đã chạy lại integration TC22–TC25 và e2e để xác nhận.

## TD-15 – Phần đã cắt hoặc hoãn trong Sprint 2

| Hạng mục | Quyết định | Lý do |
|---|---|---|
| UC8 – khối lượng toàn trung tâm | Hoãn | Mức COULD, ngoài wireframe M1–M3 (TD-05) |
| Hủy lịch hẹn trên giao diện | Hoãn | Wireframe không có thao tác hủy (TD-05) |
| Màn hình thứ tư trở đi, trang chi tiết phiếu riêng | Cắt | Chi tiết phiếu đã nằm trong M2 và M3; ưu tiên luồng chính chạy end-to-end |
| TC01–TC18 (acceptance test theo báo cáo Word) | Hoãn sang Buổi 12 | Ưu tiên test lớp nghiệp vụ và một test e2e luồng chính trên dữ liệu thật |
| Khoá phiên bản thư viện (`requirements*.txt`, Docker) | Hoãn sang Buổi 11 | Nội dung quản lý phụ thuộc của Buổi 11 |