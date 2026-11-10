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
- **Cập nhật (BT3, 10/11/2026):** bốn sơ đồ `wireframe`, `erd`, `usecase`, `architecture` (.drawio) đã chuyển vào `docs/diagrams/`, khớp đường dẫn trong prompt.

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
- **Cập nhật (đã giải quyết):** `ticket_status_log.csv` được bổ sung từ bộ dataset vào `data/raw/`; lịch hẹn sinh bằng `scripts/gen_appointments.py` (TD-09). Pipeline `load_catalog` → `load_tickets` → `load_appointments` thay cho seed cũ (đã xoá ở Buổi 12, TD-19) và đã nạp đủ sáu bảng (xem TD-07, TD-08, `docs/bao-cao-nap-du-lieu.md`). TC01–TC18 đã viết và chạy ở Buổi 10 (TD-16).

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
| Nút hủy lịch hẹn trên giao diện | Hoãn | Wireframe không có thao tác hủy (TD-05); từ Buổi 12 đã có API hủy mềm `DELETE /api/appointments/{id}` (TD-17) |
| Màn hình thứ tư trở đi, trang chi tiết phiếu riêng | Cắt | Chi tiết phiếu đã nằm trong M2 và M3; ưu tiên luồng chính chạy end-to-end |
| Khoá phiên bản thư viện (`requirements*.txt`, Docker) | Hoãn sang Buổi 11 | Nội dung quản lý phụ thuộc của Buổi 11 |
## TD-16 – Cách chạy 18 test case TC01–TC18 trên hệ thống thật

- **Vấn đề phát hiện:** Đặc tả 18 test (báo cáo Word Buổi 10) giả định một số điều kiện không khớp hệ thống thật: test nghiệp vụ chạy trong giao dịch rồi rollback, ảnh kết quả nhóm A là thẻ PASS/FAIL vẽ bằng Pillow, dữ liệu nạp chừa một trung tâm không có phiếu MỚI, và giao diện cho phép nhập 09:15 hay lý do rỗng.
- **Quyết định:** **SỬA cách chạy, GIỮ nguyên mã, tên, loại, truy vết và kỳ vọng** (lưu nguyên văn ở `tests/tc_catalog.json`):
  - Trình duyệt và backend dùng kết nối riêng nên không rollback được: mỗi test tạo lại `smartcrm_work_test` từ `smartcrm_test` và khởi động backend trên bản sao đó; kịch bản (khối lượng 5/2/8, tay nghề 2 hoặc 3, KTV nghỉ việc…) dựng bằng SQL trên bản sao từ bản ghi thật.
  - Ảnh chỉ chụp bằng `page.screenshot()` trên giao diện React hoặc Swagger của backend thật; không còn ảnh vẽ, `_summary.png`, `results.json`. Báo cáo tự sinh: `docs/test-evidence/testcase.md`.
  - Dùng Swagger ở bước mà giao diện chặn trước khi gọi API: TC06 (M2 chỉ cho chọn người tay nghề ≥ 3), TC09 (ô giờ bước 30 phút không nhận 09:15), TC11 (M3 chỉ hiện nút chuyển hợp lệ), TC12 (a) (nút Lưu bị vô hiệu khi lý do rỗng), TC13 (c) (M3 không có đường mở phiếu người khác).
  - TC15: pipeline giữ 5 phiếu MOI ở mọi trung tâm, nên test xoá 5 phiếu MOI của trung tâm cuối trên bản sao.
  - TC07: dữ liệu demo có một tài khoản Quản lý mỗi trung tâm, nên hai phiên trình duyệt dùng cùng tài khoản đó.
  - `page.route` chỉ dùng cho TC14 (giữ request 3 giây), TC16 (abort), TC17 (trả 401).
- **Lý do:** Giữ nguyên ý nghĩa kiểm thử và dữ liệu thật, đồng thời mọi ảnh là ảnh trình duyệt thật và chạy lại được nhiều lần.
- **Ảnh hưởng:** Lệnh `python -m pytest -m system` (cần frontend đang chạy, cổng 8000 trống) cho 18 passed. Để đáp ứng kỳ vọng b3/b4/b7 của TC18 và TC12, giao diện được bổ sung: thông báo thành công khi phân công/đổi KTV/đổi trạng thái, bảng lịch hẹn ở M2, nhãn "ĐỔI KỸ THUẬT VIÊN" trong lịch sử.

## TD-17 – CRUD đủ cho hai thực thể Phiếu và Lịch hẹn (Buổi 12)

- **Vấn đề phát hiện:** Tiêu chí S1 của BT2 (track SE) yêu cầu đủ CRUD cho ít nhất hai thực thể; API chỉ có tạo/xem lịch hẹn và xem/đổi trạng thái phiếu.
- **Quyết định:** **SỬA** – bổ sung:
  - Phiếu: `POST /api/tickets` (Quản lý tạo phiếu MỚI ở trung tâm của mình, chuẩn hoá SĐT theo QT-02, sinh mã `BH-<id 6 số>/<năm>`, ghi log), `PUT /api/tickets/{id}` (sửa thông tin khi còn MỚI), `DELETE /api/tickets/{id}` (hủy mềm: `DA_HUY`, `closed_at`, ghi log `MOI → DA_HUY`, chỉ khi còn MỚI).
  - Lịch hẹn: `GET /api/appointments` (Quản lý: lịch của trung tâm; KTV: lịch của mình), `GET /api/appointments/{id}`, `PUT /api/appointments/{id}` (đổi loại/giờ/ghi chú, kiểm lại giờ làm việc và chống trùng, theo KTV hiện tại của phiếu), `DELETE /api/appointments/{id}` (hủy mềm `DA_HUY`, giải phóng khung giờ).
- **Lý do:** QT-13 cấm xoá vật lý phiếu và lịch sử, lịch hẹn hủy chỉ đánh dấu, nên "Delete" là hủy mềm. Tạo phiếu ở đây là bản tối giản phục vụ CRUD; luồng tiếp nhận đầy đủ (L2) vẫn ngoài phạm vi.
- **Ảnh hưởng:** Không đổi schema (`DA_HUY` đã có ở cả hai bảng). Quy tắc mới là hàm thuần trong `ticket_rules.py`, `appointment_rules.py` có unit test; `tests/integration/test_crud.py` chạy đủ vòng tạo → đọc → sửa → hủy trên PostgreSQL.

## TD-18 – Tách ba lớp và lỗi miền không chứa mã HTTP (Buổi 12)

- **Vấn đề phát hiện:** Tiêu chí C2 yêu cầu service không có req/res/mã trạng thái HTTP; mã cũ để SQL trong router và `ticket_rules.py` raise `APIError(409, …)`.
- **Quyết định:** **SỬA** – `routers/` chỉ nhận request và gọi service; `services/` (`ticket_service`, `appointment_service`, `ticket_rules`, `appointment_rules`) chứa nghiệp vụ và raise `DomainError(kind, code, message)` với `kind` ∈ {INVALID, UNAUTHENTICATED, FORBIDDEN, NOT_FOUND, CONFLICT, UNAVAILABLE}; `repositories/` chứa toàn bộ SQL; chỉ `app/main.py` ánh xạ `kind` → mã HTTP. Thêm xử lý CSDL tắt (503 `DATABASE_UNAVAILABLE`) và lỗi ngoài dự kiến (500 `INTERNAL_ERROR`, không lộ traceback, ghi log).
- **Lý do:** Tách lớp để test nghiệp vụ không cần CSDL/HTTP và để suy giảm có kiểm soát khi CSDL tắt.
- **Ảnh hưởng:** Phản hồi API (mã lỗi, thông báo, mã HTTP) giữ nguyên, kiểm bằng 18 TC, e2e và integration chạy lại sau khi tách.

## TD-19 – Bộ dữ liệu mẫu trong repo, dựng hệ thống một lệnh, khoá phiên bản (Buổi 12)

- **Vấn đề phát hiện:** Giảng viên clone repo theo tag `v0.2` và chạy theo README tại lớp; bộ CSV case-study không nằm trong repo nên bản clone chạy lên nhưng trống. `requirements.txt` chưa khoá phiên bản.
- **Quyết định:** **SỬA** – thêm `data/sample/` (462 KB) do `scripts/make_sample_data.py` trích từ dữ liệu thật: đủ trung tâm, KTV, tay nghề; mọi phiếu ĐÃ PHÂN CÔNG (để 30 phiếu MOI theo seed 20260901 trùng dữ liệu đầy đủ); mọi phiếu mà `appointments.csv` tham chiếu. Loader dùng `data/raw/` khi đủ 7 CSV, ngược lại dùng bộ mẫu (`scripts/data_source.py`). `scripts/setup_all.py` tạo database nếu chưa có → migrate → nạp → tạo tài khoản, chạy lại không nhân đôi. Khoá `requirements*.txt` bằng `pip freeze` từ venv sạch; `.env.example` đủ tên biến với giá trị mẫu. Xoá `scripts/legacy/seed_real_data.py` (đã thay bằng pipeline mới), chuyển phần ánh xạ trạng thái có dấu sang `load_tickets.py`.
- **Lý do:** Mục CỐT LÕI C1 (clone chạy theo README) và C5 (chạy lại không nhân đôi).
- **Ảnh hưởng:** Bộ mẫu cho 939 phiếu, 3.237 dòng log, 300 lịch hẹn; fixture integration chấp nhận cả số dòng của bộ mẫu và bộ đầy đủ; `tests/integration/test_idempotent_load.py` chạy `setup_all.py` hai lần và so số dòng.

## Buổi 14 – Phản hồi BT2 và quyết định xử lý (BT3)

Không có văn bản nhận xét riêng cho BT2; các mục dưới đây đối chiếu sáu phản hồi thường gặp mà giảng viên nêu ở
Buổi 14 với repo này, mỗi mục có quyết định và dẫn chứng.

## TD-20 – Tệp khoá phiên bản

- **Phản hồi:** “Chưa commit tệp khoá phiên bản.”
- **Quyết định:** **GIỮ** – đã có từ Buổi 12 (TD-19).
- **Lý do / dẫn chứng:** `requirements.txt`, `requirements-dev.txt` ghi phiên bản cố định (`pip freeze` từ venv sạch); `src/frontend/package-lock.json` được Git theo dõi (`git ls-files | grep lock`). Ngày 08/11/2026 cài lại `requirements-dev.txt` vào venv rồi chạy `python -m pytest`: 100 passed.
- **Ảnh hưởng:** không đổi.

## TD-21 – Secret trong lịch sử commit

- **Phản hồi:** “Có secret trong lịch sử commit” (repo BT3 phải PUBLIC).
- **Quyết định:** **GIỮ** – không có secret cần đổi khoá.
- **Lý do / dẫn chứng:** `git log --all -- .env` rỗng (tệp `.env` chưa từng được commit, `.gitignore` dòng đầu); quét `git log --all -p` tìm dòng thêm `…PASSWORD=`/`SECRET_KEY=` có giá trị (trừ `.env.example`): 0 kết quả. `.env.example` chỉ chứa giá trị mẫu (`doi-mat-khau-…`, `thay-bang-chuoi-…`). Mật khẩu demo chỉ lưu dạng băm PBKDF2 trong `data/processed/demo_accounts.json` (cũng bị `.gitignore`).
- **Ảnh hưởng:** ghi vào [security-checklist.md](security-checklist.md) mục 1–2.

## TD-22 – “Test quá ít, chỉ test luồng đúng”

- **Phản hồi:** cần thêm test biên, dữ liệu sai, bảo mật.
- **Quyết định:** **SỬA** – thêm bộ 12 test case BT3 (`tests/bt3/`, marker `bt3`) theo năm loại, chạy trên backend thật và dữ liệu thật, có ảnh Swagger trong `docs/screenshots/` ([test-plan.md](test-plan.md), [test-report.md](test-report.md)).
- **Lý do:** Buổi 13–14 yêu cầu ít nhất hai test biên, hai test dữ liệu sai kiểm cả mã và nội dung, và năm mục OWASP.
- **Ảnh hưởng:** TC-07 phát hiện BUG-08 (phiếu nhận trường bắt buộc chỉ có khoảng trắng), đã sửa ở commit `224fd69` và thêm quy tắc `require_text_fields()` (mã lỗi mới `REQUIRED_FIELD_BLANK`, 400). Không đổi schema.

## TD-23 – Mâu thuẫn đặt lịch cho phiếu HOÀN TẤT (tiếp TD-10)

- **Phản hồi:** TD-10 ghi `L04_TieuChi_GWT EX-7.3` chỉ từ chối `MOI`, `DA_DONG`, `DA_HUY`, mâu thuẫn SRS UC6, “cần sửa ở BT3”.
- **Quyết định:** **GIỮ** hành vi của mã, theo SRS: không đặt lịch cho phiếu chưa có KTV (`TICKET_NOT_ASSIGNED`) hoặc đã kết thúc `HOAN_TAT`/`DA_DONG`/`DA_HUY` (`TICKET_CLOSED`), cả hai trả 400 (`appointment_rules.check_ticket_accepts_appointment`, unit test `test_ticket_without_technician_or_finished_cannot_be_booked`).
- **Lý do:** SRS là tài liệu đặc tả được duy trì trong repo; GWT EX-7.3 là bảng tiêu chí nộp ở BT1, không nằm trong repo. Ghi nhận EX-7.3 phải hiểu là bao gồm `HOAN_TAT`.
- **Ảnh hưởng:** không đổi mã.

## TD-24 – Đóng gói dựng lại bằng ≤ 2 lệnh (TP4)

- **Phản hồi:** BT3 TP4 yêu cầu dựng lại hệ thống từ thư mục trống bằng tối đa hai lệnh; README BT2 cần Python, PostgreSQL cài sẵn và khoảng mười lệnh.
- **Quyết định:** **SỬA** – Docker Compose có thêm dịch vụ `init` chạy `scripts/setup_all.py` (tạo DB → migrate → nạp bộ mẫu → sinh tài khoản demo vào volume dùng chung), backend chờ `init` xong; healthcheck cho db, backend, frontend. Hai lệnh: `cp .env.example .env` và `docker compose up -d --build` ([deployment-guide.md](deployment-guide.md)).
- **Lý do:** người chấm không cần cài Python/PostgreSQL; bộ mẫu `data/sample/` có sẵn trong repo.
- **Ảnh hưởng:** cách dựng thủ công ở README vẫn giữ cho phát triển và chạy test.
