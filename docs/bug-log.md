# Nhật ký lỗi (Bug Log)

Repo: https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen

Mỗi bug ghi đủ **bảy dòng** theo mẫu Buổi 13 và được gỡ theo bốn bước của Buổi 11 (tái lập → khoanh vùng →
sửa nguyên nhân → xác nhận). Mức độ phân loại bằng ba câu hỏi: *người dùng có làm được việc không · dữ liệu có sai
hay bị lộ không · có cách làm tạm không*.

| Mã | Mức độ | Phát hiện bởi | Tóm tắt | Commit sửa (riêng cho bug) |
|---|---|---|---|---|
| [BUG-08](#bug-08) | **Major** | TC-07 (BT3) | Phiếu được tạo với tên khách, serial, mô tả chỉ có khoảng trắng | [224fd69](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/224fd6902da028a096100d077e80a1e752fbf600) |
| [BUG-07](#bug-07) | **Major** | Phép thử CSDL tắt (BT2, ảnh BT2_07) | API treo hơn 2 phút khi không kết nối được CSDL | [25e3d1e](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/25e3d1ebaa7eeba552f7bc05d0d379181a082546) |
| [BUG-03](#bug-03) | **Major** | Phép thử clone thư mục trống theo README | Bản clone mới không dựng được hệ thống theo README | [a947ed7](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/a947ed735765dc34ccd58b37b222f9b6c4cbdcf5) |
| [BUG-09](#bug-09) | Minor | Phép thử máy trắng Buổi 16 theo README mục 5.2 | Dựng DB kiểm thử qua `localhost` gần như treo (mỗi kết nối ~60 giây) | [146e4a5](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/146e4a5b28b5a312fd74e8733b10b496345375a2) |

Ba bug Major (BUG-08, 07, 03) là ba bug nộp cho BT3; BUG-09 (Minor) được tìm thêm ở phép thử máy trắng Buổi 16. Cả bốn bug: mỗi bug có một commit `fix…` chỉ chứa thay đổi của bug đó. Các bug BUG-01,
02, 04, 05, 06 ở cuối tệp là lịch sử Buổi 10–12; commit của chúng gộp với việc khác hoặc không phải commit `fix`,
nên không dùng làm minh chứng “một bug – một commit”.

---

## BUG-09

**BUG-09 — Hướng dẫn chạy test trỏ tới `localhost`, mỗi kết nối PostgreSQL của Docker mất khoảng 60 giây**

1. **Mã và mức độ:** BUG-09 · **MINOR** — người làm theo README mục 5.2 vẫn chạy được test nhưng bước dựng database
   kiểm thử gần như treo, rất dễ bỏ cuộc; không sai hay lộ dữ liệu, sản phẩm chạy trong Docker không bị ảnh hưởng, có
   cách làm tạm (dùng `127.0.0.1`).
2. **Phát hiện bởi:** phép thử máy trắng Buổi 16 (15/11/2026): clone sạch vào `C:\BT3pre`, làm đúng README mục 5.2.
3. **Triệu chứng:** `python scripts\setup_all.py --with-test-db` chạy hơn 10 phút chưa xong, trong khi `pg_stat_activity`
   không có truy vấn nào; tiến trình `load_appointments.py` đứng ở bước kết nối.
4. **Cách tái lập:** stack Docker đang chạy; `.env` đặt `DB_HOST=localhost`, `DB_PORT=5433`; đo
   `psycopg.connect(host=..., port=5433, connect_timeout=60)`: `127.0.0.1` → 0,0 giây, `localhost` → 60,0 giây.
5. **Nguyên nhân:** `docker-compose.yml` chỉ mở cổng PostgreSQL trên `127.0.0.1` (cố ý, mục 7 checklist bảo mật), còn
   `localhost` được phân giải thành `['::1', '127.0.0.1']`. Kết nối tới `::1:5433` (cổng đóng) trên Windows không bị từ chối
   ngay mà chờ hết thời gian chờ rồi mới thử IPv4 (cùng hiện tượng nền của BUG-07).
6. **Cách sửa:** README mục 5.2 hướng dẫn `DB_HOST=127.0.0.1` và giải thích lý do; không đổi cấu hình cổng của Docker để
   PostgreSQL vẫn chỉ nghe trên máy này.
7. **Commit và xác nhận:** [146e4a5](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/146e4a5b28b5a312fd74e8733b10b496345375a2) · làm lại mục 5.2 trên bản clone: `setup_all.py --with-test-db`
   xong trong 10 giây; `python -m pytest -m bt3` → 12 passed (145 giây), unit 104 passed, integration 7 passed.

## BUG-08

**BUG-08 — Phiếu được tạo khi tên khách, serial và mô tả chỉ có khoảng trắng**

1. **Mã và mức độ:** BUG-08 · **MAJOR** — dữ liệu sai được lưu thật vào bảng `ticket`: phiếu không có tên khách,
   serial, mô tả nên kỹ thuật viên không biết máy nào, lỗi gì (người dùng phía sau *không làm được việc*). Không phải
   Critical vì không lộ dữ liệu, không mất dữ liệu cũ, và có cách làm tạm (Quản lý sửa lại phiếu khi còn MỚI).
2. **Phát hiện bởi:** TC-07 (b), lần chạy 1 ngày 08/11/2026, commit `9cccebd` — mong đợi 400, nhận 201.
3. **Triệu chứng:** `POST /api/tickets` trả **201** và tạo phiếu BH-007801/2026 với `customer_name = ""`,
   `serial_no = ""`, `issue_desc = ""`; bảng ticket 7317 → 7318. `PUT /api/tickets/{id}` có cùng lỗi (dùng chung hàm).
4. **Cách tái lập:** đăng nhập QL_TT01; gọi `POST /api/tickets` với
   `{"customer_name": "   ", "customer_phone": "0912345678", "serial_no": "   ", "issue_desc": "   ",
   "category_code": "PIN", "priority": "CAO", "due_date": "<hôm nay + 3 ngày>+07:00"}`;
   `SELECT count(*) FROM ticket WHERE btrim(customer_name) = ''` ra 1. Ảnh:
   [trước sửa (a)](screenshots/BUG-08_truoc-sua_TC-07.png), [trước sửa (b)](screenshots/BUG-08_truoc-sua_TC-07_b.png),
   [kết quả lần chạy 1](screenshots/BUG-08_truoc-sua_ket-qua-chay.md).
5. **Nguyên nhân:** `TicketRequest` (`src/backend/app/schemas/tickets.py`) chỉ kiểm `min_length=1`, mà `"   "` dài
   3 ký tự nên qua được; sau đó `_clean_fields` trong `src/backend/app/services/ticket_service.py` gọi `.strip()` biến
   chúng thành chuỗi rỗng nhưng không kiểm lại. Cột trong CSDL là `NOT NULL` nên chuỗi rỗng vẫn được nhận.
6. **Cách sửa:** thêm quy tắc thuần `require_text_fields()` trong `src/backend/app/services/ticket_rules.py`: cắt khoảng
   trắng ba trường và ném `DomainError(INVALID, "REQUIRED_FIELD_BLANK", …, fields=[…])` nêu tên mọi trường trống;
   `_clean_fields` dùng kết quả của hàm này cho cả tạo và sửa phiếu; `app/main.py` đã ánh xạ sẵn INVALID → 400.
   Thêm 4 unit test trong `tests/test_crud_rules.py` (một luồng đúng, ba dữ liệu sai) để bug không quay lại.
7. **Commit và xác nhận:**
   [224fd69](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/224fd6902da028a096100d077e80a1e752fbf600)
   · chạy lại TC-07 → (b) HTTP 400 `REQUIRED_FIELD_BLANK`, `fields = [customer_name, serial_no, issue_desc]`, bảng
   ticket 7317 → 7317 → **PASS** ([TC-07_b.png](screenshots/TC-07_b.png)). Luồng đúng không hỏng: TC-11 vẫn tạo được
   phiếu hợp lệ (201) → PASS; integration `test_ticket_create_read_update_cancel` → PASS; toàn bộ unit
   `python -m pytest` → 104 passed ([BUG-08-fixed.png](screenshots/BUG-08-fixed.png)).

## BUG-07

**BUG-07 — API treo vài phút khi cơ sở dữ liệu không kết nối được**

1. **Mã và mức độ:** BUG-07 · **MAJOR** — khi CSDL gặp sự cố, mọi màn hình quay chờ hơn 2 phút rồi mới lỗi:
   người dùng *không làm được việc* và không biết hệ thống đang hỏng; không có cách làm tạm phía người dùng. Không
   Critical vì không sai hay lộ dữ liệu.
2. **Phát hiện bởi:** phép thử “suy giảm có kiểm soát” của BT2 (tắt CSDL rồi gọi API, ảnh
   `docs/bt2-evidence/BT2_07_M1_csdl_tat_503_thu_lai.png`); nay được giữ bởi unit test
   `test_database_connection_has_a_timeout`.
3. **Triệu chứng:** backend trỏ tới cổng CSDL không có PostgreSQL; `GET /api/tickets` không trả lời sau hơn 2 phút,
   giao diện M1 hiện “Đang tải…” mãi.
4. **Cách tái lập:** đặt `DB_PORT=1` trong `.env`, chạy backend, đăng nhập QL_TT01 rồi gọi `GET /api/tickets`.
5. **Nguyên nhân:** engine SQLAlchemy không đặt thời gian chờ kết nối; trên Windows kết nối tới cổng đóng không bị
   từ chối ngay. Đo riêng `psycopg.connect(port=1)`: không `connect_timeout` thì treo > 2 phút, có `connect_timeout=3`
   thì lỗi sau 3 giây.
6. **Cách sửa:** `get_engine()` trong `src/backend/app/core/database.py` truyền
   `connect_args={"connect_timeout": DB_CONNECT_TIMEOUT}` (mặc định 3 giây, khai báo trong `.env.example`);
   lỗi kết nối đã được `app/main.py` ánh xạ thành 503 `DATABASE_UNAVAILABLE`.
7. **Commit và xác nhận:**
   [25e3d1e](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/25e3d1ebaa7eeba552f7bc05d0d379181a082546)
   · gọi lại API: HTTP 503 `DATABASE_UNAVAILABLE` sau 3,0 giây, có dòng log; unit test
   `test_database_connection_has_a_timeout` → PASS (nằm trong 104 passed ngày 08/11/2026).

## BUG-03

**BUG-03 — Bản clone mới không dựng được hệ thống theo README**

1. **Mã và mức độ:** BUG-03 · **MAJOR** — người khác (giảng viên) làm đúng README trên thư mục trống thì *không dựng
   được hệ thống*; không sai/lộ dữ liệu; cách làm tạm là tự tạo thư mục `data/raw` (người mới không biết).
2. **Phát hiện bởi:** phép thử clone vào thư mục trống và làm theo README từng bước (Buổi 11).
3. **Triệu chứng:** đến bước chép dữ liệu, `Copy-Item <thư-mục-CSV>\*.csv data\raw\` báo “The directory name is invalid”.
4. **Cách tái lập:** `git clone` repo vào thư mục mới, làm theo README đến bước chép CSV vào `data\raw\`.
5. **Nguyên nhân:** `.gitignore` có dòng `data/raw/` bỏ qua cả thư mục; Git không lưu thư mục rỗng nên bản clone
   không có `data/raw/`.
6. **Cách sửa:** `.gitignore` đổi thành `data/raw/*` + `!data/raw/.gitkeep` và thêm `data/raw/.gitkeep`; CSV vẫn
   không bị commit. (Về sau thêm bộ mẫu `data/sample/` để clone không cần CSV từ LMS – TD-19.)
7. **Commit và xác nhận:**
   [a947ed7](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/a947ed735765dc34ccd58b37b222f9b6c4cbdcf5)
   · clone lại từ đầu: bản clone có `data/raw/`, bước chép dữ liệu chạy được, `setup_all.py` nạp xong. Hiện TC-12 kiểm
   bước dựng CSDL từ bộ mẫu chạy hai lần không nhân đôi → PASS.

---

## Lịch sử Buổi 10–12 (không dùng làm bug nộp BT3)

### BUG-01 — pytest dừng hẳn khi tên test có tiếng Việt

1. **Mã và mức độ:** BUG-01 · Minor — chỉ ảnh hưởng người chạy test trong Git Bash; làm tạm bằng terminal UTF-8.
2. **Phát hiện bởi:** chạy `python -m pytest` trong Git Bash / chuyển hướng ra tệp.
3. **Triệu chứng:** `INTERNALERROR UnicodeEncodeError: 'charmap' codec can't encode character 'ồ'`; đếm 33 thay vì 58 test.
4. **Cách tái lập:** chạy pytest với stdout cp1252 (`> log.txt`).
5. **Nguyên nhân:** `print(...)` trong hook `pytest_runtest_makereport` của `tests/conftest.py` ghi tiếng Việt ra stdout cp1252.
6. **Cách sửa:** hàm `_echo()` mã hoá theo bảng mã của stdout với `errors="replace"`.
7. **Commit và xác nhận:** [eae4931](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/eae4931) (gộp với commit thêm unit test) · cp1252 và UTF-8 đều 58 passed.

### BUG-02 — Màn hình M3 nhấp nháy “Đang tải dữ liệu…” khi chọn phiếu

1. **Mã và mức độ:** BUG-02 · Minor — gây khó chịu, kỹ thuật viên vẫn làm được việc.
2. **Phát hiện bởi:** test e2e luồng chính trên M3.
3. **Triệu chứng:** mỗi lần chọn phiếu hoặc đổi trạng thái, cả danh sách biến mất rồi hiện lại.
4. **Cách tái lập:** đăng nhập KT033, lọc “Đang làm”, bấm một phiếu.
5. **Nguyên nhân:** `load` trong `MyTicketsPage.jsx` phụ thuộc `selected` → đổi phiếu tạo `load` mới → effect chạy lại, bật loading toàn trang.
6. **Cách sửa:** `load` không phụ thuộc `selected`; làm mới ngầm `load({ silent: true })` sau khi đổi trạng thái.
7. **Commit và xác nhận:** [ebfbb35](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/ebfbb35) (gộp ba thay đổi giao diện) · test e2e với `MutationObserver` PASS, mã cũ FAIL.

### BUG-04 — Test lỗi trên bản clone ở thư mục đường dẫn dài

1. **Mã và mức độ:** BUG-04 · Minor — làm tạm bằng cách clone vào đường dẫn ngắn.
2. **Phát hiện bởi:** phép thử clone từ GitHub.
3. **Triệu chứng:** `DLL load failed while importing _immutabledict_cy: The filename or extension is too long`.
4. **Cách tái lập:** clone vào thư mục đường dẫn khoảng 174 ký tự, tạo venv, chạy pytest.
5. **Nguyên nhân:** Windows giới hạn 260 ký tự khi nạp DLL; tệp sâu nhất trong `.venv` dài 297 ký tự.
6. **Cách sửa:** README cảnh báo clone vào đường dẫn ngắn.
7. **Commit và xác nhận:** [2febebd](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/2febebd) (commit tài liệu) · clone vào đường dẫn 97 ký tự: mọi nhóm test pass.

### BUG-05 — “Phiếu của tôi” dài hơn 20.000 px và hiện mã thô DA_DONG

1. **Mã và mức độ:** BUG-05 · Minor — dùng được nhưng khó tìm phiếu; không sai dữ liệu.
2. **Phát hiện bởi:** e2e luồng chính trên dữ liệu thật.
3. **Triệu chứng:** M3 của KT033 hiện 437 dòng, cột trạng thái có chữ `DA_DONG`.
4. **Cách tái lập:** đăng nhập KT033 trên dữ liệu đầy đủ, mở M3.
5. **Nguyên nhân:** frontend chỉ có nhãn cho 4/7 mã trạng thái; dữ liệu thật lớn hơn giả định.
6. **Cách sửa:** nhãn cho mọi mã và bộ lọc trạng thái ở M3 (TD-13).
7. **Commit và xác nhận:** [7707702](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/7707702) (commit `feat`) · lọc “Đã đóng” ra 359/437, khớp SQL.

### BUG-06 — Service trả mã lỗi HTTP, vi phạm tách lớp

1. **Mã và mức độ:** BUG-06 · Minor — lỗi thiết kế, người dùng không thấy.
2. **Phát hiện bởi:** rà mã theo tiêu chí C2 của BT2.
3. **Triệu chứng:** `services/ticket_rules.py` raise `APIError(409, …)`, router chứa 15 câu SQL.
4. **Cách tái lập:** `grep -n "APIError" src/backend/app/services` và `grep -n "text(" src/backend/app/routers`.
5. **Nguyên nhân:** API dựng nhanh trong router, chưa có lớp repository và lỗi miền.
6. **Cách sửa:** `DomainError` không mang mã HTTP, SQL sang `repositories/`, chỉ `app/main.py` ánh xạ (TD-18).
7. **Commit và xác nhận:** [ee4013f](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/ee4013f) (commit `refactor`) · hai lệnh grep rỗng; 18 TC, e2e, integration pass.
