# Nhật ký lỗi (bug log)

Mỗi lỗi ghi theo quy trình 4 bước của Buổi 11: tái lập → khoanh vùng → sửa nguyên nhân → xác nhận. Link commit trỏ tới repo GitHub.

Repo: https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen

## BUG-01 – pytest dừng hẳn khi tên test có tiếng Việt

- **Triệu chứng:** `python -m pytest` báo `INTERNALERROR UnicodeEncodeError: 'charmap' codec can't encode character '\u1ed3'`, dừng sau test đầu tiên có docstring tiếng Việt; số test pass bị đếm thiếu (33 thay vì 58).
- **Tái lập:** chạy pytest trong Git Bash hoặc chuyển hướng đầu ra (`> log.txt`), khi đó stdout dùng bảng mã cp1252.
- **Khoanh vùng:** traceback chỉ vào `print(...)` trong hook `pytest_runtest_makereport` của `tests/conftest.py`, không phải trong test.
- **Nguyên nhân:** dòng in kết quả `[TCxx] PASS <tên test>` ghi thẳng tiếng Việt ra stdout cp1252.
- **Cách sửa:** hàm `_echo()` mã hoá theo bảng mã của stdout với `errors="replace"`.
- **Xác nhận:** chạy lại với stdout cp1252 và UTF-8 đều 58 passed, không còn INTERNALERROR.
- **Commit:** [eae4931](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/eae4931)

## BUG-02 – Màn hình M3 nhấp nháy "Đang tải dữ liệu…" khi chọn phiếu

- **Triệu chứng:** mỗi lần kỹ thuật viên chọn phiếu hoặc bấm đổi trạng thái, cả danh sách biến mất rồi hiện lại.
- **Tái lập:** đăng nhập KT033 (437 phiếu), lọc "Đang làm", bấm một phiếu.
- **Khoanh vùng:** trong `MyTicketsPage.jsx`, `load` được bọc `useCallback(..., [selected])` và `useEffect(() => load(), [load])`.
- **Nguyên nhân:** đổi `selected` tạo `load` mới → effect chạy lại → bật trạng thái loading cho toàn trang.
- **Cách sửa:** `load` không phụ thuộc `selected`; làm mới "ngầm" (`load({ silent: true })`) sau khi đổi trạng thái.
- **Xác nhận:** test e2e gắn `MutationObserver` theo dõi `[data-testid=state-loading]`; đưa lại mã cũ thì test FAIL đúng chỗ, mã mới thì PASS.
- **Commit:** [ebfbb35](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/ebfbb35)

## BUG-03 – Clone mới không chạy được bước chép dữ liệu trong README

- **Triệu chứng:** làm đúng README trên thư mục clone trống, lệnh `Copy-Item <thư-mục-CSV>\*.csv data\raw\` báo "The directory name is invalid".
- **Tái lập:** `git clone` repo vào thư mục mới, chạy đến bước 9 của README.
- **Khoanh vùng:** `data/raw/` không tồn tại trong bản clone dù có trên máy phát triển.
- **Nguyên nhân:** `.gitignore` bỏ qua cả thư mục `data/raw/`, Git không lưu thư mục rỗng.
- **Cách sửa:** đổi thành `data/raw/*` + `!data/raw/.gitkeep`; CSV vẫn không bị commit.
- **Xác nhận:** clone lại từ đầu, bước 9 chạy được; về sau bổ sung bộ mẫu `data/sample/` để clone không cần CSV từ LMS.
- **Commit:** [a947ed7](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/a947ed7)

## BUG-04 – Test PASS trên máy em nhưng lỗi trên bản clone ở thư mục sâu

- **Triệu chứng:** trên bản clone từ GitHub, `python -m pytest` báo 5 errors `DLL load failed while importing _immutabledict_cy: The filename or extension is too long`.
- **Tái lập:** clone vào thư mục có đường dẫn dài khoảng 174 ký tự, tạo venv, chạy pytest.
- **Khoanh vùng:** lỗi xảy ra khi import SQLAlchemy, không liên quan mã của dự án; đo đường dẫn tệp sâu nhất trong `.venv` là 297 ký tự.
- **Nguyên nhân:** Windows giới hạn 260 ký tự khi nạp DLL, kể cả khi đã bật LongPathsEnabled.
- **Cách sửa:** README thêm lưu ý clone vào thư mục có đường dẫn ngắn (ví dụ `D:\Projects`).
- **Xác nhận:** clone lại vào đường dẫn 97 ký tự: unit, UI, integration, e2e đều pass.
- **Commit:** [2febebd](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/2febebd)

## BUG-05 – Danh sách "Phiếu của tôi" dài hơn 20.000 px và hiện mã thô DA_DONG

- **Triệu chứng:** chạy luồng chính trên dữ liệu thật, M3 của KT033 hiện 437 dòng; cột trạng thái có chữ `DA_DONG` thay vì nhãn tiếng Việt.
- **Tái lập:** đăng nhập KT033 trên dữ liệu case-study đầy đủ, mở M3.
- **Khoanh vùng:** API `GET /api/technicians/me/tickets` trả mọi phiếu của kỹ thuật viên (đúng đặc tả); frontend chỉ có nhãn cho 4/7 mã trạng thái.
- **Nguyên nhân:** lỗi hợp đồng dữ liệu (thiếu nhãn) cộng với dữ liệu thật lớn hơn giả định (trung bình 192, tối đa 443 phiếu mỗi KTV).
- **Cách sửa:** thêm nhãn cho mọi mã; thêm bộ lọc trạng thái ở M3 (mặc định Tất cả), không ẩn phiếu đã đóng/đã hủy của chính kỹ thuật viên (TD-13).
- **Xác nhận:** test e2e lọc "Đã đóng" ra đúng 359/437 phiếu, bằng số phiếu `DA_DONG` của KT033 đếm bằng SQL.
- **Commit:** [7707702](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/7707702)

## BUG-06 – Service trả mã lỗi HTTP, vi phạm tách lớp

- **Triệu chứng:** rà mã theo tiêu chí C2 thấy `services/ticket_rules.py` raise `APIError(409, ...)`, router `tickets.py` chứa 15 câu SQL.
- **Tái lập:** `grep -n "APIError" src/backend/app/services` và `grep -n "text(" src/backend/app/routers`.
- **Khoanh vùng:** quy tắc nghiệp vụ, SQL và HTTP nằm chung trong router; service biết mã trạng thái HTTP.
- **Nguyên nhân:** lúc đầu dựng API nhanh trong router, chưa tách lớp repository và lỗi miền.
- **Cách sửa:** `DomainError(kind, code, message)` không có số HTTP; SQL chuyển sang `repositories/`; chỉ `app/main.py` ánh xạ `kind` → HTTP (TD-18).
- **Xác nhận:** hai lệnh `grep` trên trả rỗng; 18 TC, e2e, integration vẫn pass nên phản hồi API không đổi.
- **Commit:** [ee4013f](https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/commit/ee4013f)

## BUG-07 – API treo vài phút khi cơ sở dữ liệu không kết nối được

- **Triệu chứng:** thử "suy giảm có kiểm soát" bằng cách cho backend trỏ tới cổng CSDL không có PostgreSQL; `GET /api/tickets` không trả lời sau hơn 2 phút.
- **Tái lập:** đặt `DB_PORT=1`, chạy backend, đăng nhập rồi gọi `GET /api/tickets`.
- **Khoanh vùng:** đo riêng `psycopg.connect(port=1)`: không có `connect_timeout` thì treo > 2 phút; có `connect_timeout=3` thì báo lỗi sau 3 giây (6 giây với `localhost` vì thử cả IPv6 và IPv4).
- **Nguyên nhân:** engine SQLAlchemy không đặt thời gian chờ kết nối; trên Windows kết nối tới cổng đóng không bị từ chối ngay.
- **Cách sửa:** `get_engine()` truyền `connect_args={"connect_timeout": DB_CONNECT_TIMEOUT}` (mặc định 3 giây, khai báo trong `.env.example`).
- **Xác nhận:** gọi lại API: HTTP 503 `DATABASE_UNAVAILABLE` sau 3,0 giây, có dòng log; unit test `test_database_connection_has_a_timeout`.
- **Commit:** xem lịch sử commit của `src/backend/app/core/database.py` (thông điệp "fix: bound the database connect time").

