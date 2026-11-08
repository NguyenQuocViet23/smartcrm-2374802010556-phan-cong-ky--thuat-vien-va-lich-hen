# Smart CRM – Phân công kỹ thuật viên và lịch hẹn (L04)

**Đơn vị mô phỏng:** Mekong Mobile
**Sinh viên:** Nguyễn Quốc Việt – MSSV 2374802010556 – Lớp 261_71ITGR40203_05
**Track:** SE · Chuyên đề Tốt nghiệp 1 – Trường ĐH Văn Lang · Bài tập 3: tag `v1.0` (Bài tập 2: tag `v0.2`)

## 1. Mô tả bài toán và phạm vi

Smart CRM hỗ trợ Quản lý trung tâm phân công phiếu bảo hành cho kỹ thuật viên cùng trung tâm, đủ tay nghề; hỗ trợ đặt lịch giao/nhận thiết bị và giúp Kỹ thuật viên cập nhật trạng thái phiếu. Hạn cam kết được đọc/hiển thị, không sửa trong luồng phân công.

Luồng trạng thái: `MOI → DA_PHAN_CONG → DANG_XU_LY → CHO_LINH_KIEN → HOAN_TAT` (có thể đi thẳng `DANG_XU_LY → HOAN_TAT`); phiếu còn MỚI có thể bị hủy mềm (`DA_HUY`).

**Trong phạm vi:** danh sách phiếu mới, gợi ý kỹ thuật viên theo trung tâm/tay nghề/khối lượng, phân công và đổi kỹ thuật viên, phiếu của tôi, lịch hẹn giao/nhận có chống trùng, cập nhật trạng thái, CRUD phiếu và lịch hẹn (hủy mềm), xác thực demo, ba màn hình M1/M2/M3.

**Ngoài phạm vi:** UC8/báo cáo khối lượng toàn trung tâm, luồng tiếp nhận phiếu L2 đầy đủ, tồn kho/linh kiện, SMS/Zalo, điều chuyển trung tâm. Phần đã cắt và lý do: [docs/thay-doi-thiet-ke.md](docs/thay-doi-thiet-ke.md).

## 2. Công nghệ, phiên bản và cấu trúc

| Thành phần | Công nghệ | Phiên bản đã kiểm |
|---|---|---|
| Backend | Python, FastAPI, SQLAlchemy, psycopg | Python 3.12 (Docker) và 3.14 (máy); thư viện khoá trong `requirements.txt` |
| Cơ sở dữ liệu | PostgreSQL | 16 (Docker) và 18 (máy) |
| Frontend | React, Vite, React Router | Node.js 22 (Docker) và 24 (máy); khoá trong `package-lock.json` |
| Kiểm thử | pytest, TestClient, pytest-playwright (Chromium) | khoá trong `requirements-dev.txt` |
| Triển khai | Docker Compose (tùy chọn) | Docker 29 |

Kiến trúc backend ba lớp: `routers/` (chỉ HTTP) → `services/` (nghiệp vụ, raise `DomainError`, không biết HTTP) → `repositories/` (toàn bộ SQL). Chỉ `app/main.py` đổi `DomainError` thành mã HTTP.

```text
db/                          schema 6 bảng và migration
data/sample/                 bộ mẫu trích từ dữ liệu thật (có commit) + appointments.csv
data/raw/                    bộ CSV case-study đầy đủ từ LMS (tùy chọn, không commit)
scripts/setup_all.py         dựng database một lệnh (tạo DB → migrate → nạp → tài khoản)
scripts/                     migrate, load_catalog, load_tickets, load_appointments, …
src/backend/app/             routers/, services/, repositories/, domain/, core/
src/frontend/src/            api/ (client.js + *.api.js), components/, pages/
tests/                       unit test; integration/; service/ + ui/ (TC01–TC18); e2e/
docs/                        SRS, sơ đồ, thay đổi thiết kế, nhật ký lỗi, khai báo AI, minh chứng
```

## 3. Các bước dựng hệ thống

Cần cài sẵn: **Git**, **Python 3.12+**, **Node.js 22+**, **PostgreSQL 16+** đang chạy (biết user/mật khẩu, mặc định `postgres`). Không cần tải thêm dữ liệu: repo có sẵn bộ mẫu `data/sample/`. Nếu có bộ 7 CSV case-study đầy đủ từ LMS, chép vào `data/raw/` trước bước 9 thì hệ thống tự dùng bộ đầy đủ.

> **Windows:** clone vào thư mục có đường dẫn ngắn (ví dụ `D:\Projects`). Tên repo đã dài 66 ký tự; nếu đường dẫn tới thư mục repo vượt khoảng 130 ký tự, tệp trong `.venv` vượt giới hạn 260 ký tự và pytest báo `DLL load failed ... The filename or extension is too long` (BUG-04).

### 3.1. Windows PowerShell (mỗi dòng một lệnh, chạy từ thư mục gốc repo)

```powershell
# 1. Lấy mã nguồn đúng phiên bản nộp bài
git clone --branch v1.0 https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen.git smartcrm
# 2. Vào thư mục repo
Set-Location smartcrm
# 3. Tạo tệp cấu hình từ mẫu
Copy-Item .env.example .env
# 4. Sửa DB_USER, DB_PASSWORD (theo PostgreSQL của máy), SECRET_KEY (≥ 32 ký tự), DEMO_PASSWORD rồi lưu
notepad .env
# 5. Tạo môi trường ảo Python
py -m venv .venv
# 6. Kích hoạt môi trường ảo
.\.venv\Scripts\Activate.ps1
# 7. Cài thư viện (phiên bản đã khoá)
python -m pip install -r requirements-dev.txt
# 8. Chạy kiểm thử đơn vị: phải thấy "104 passed"
python -m pytest
# 9. Dựng database: tạo DB smartcrm nếu chưa có, migrate, nạp dữ liệu, tạo tài khoản demo
python scripts\setup_all.py
# 10. Chạy backend (giữ cửa sổ này mở) → http://localhost:8000/docs
python -m uvicorn app.main:app --app-dir src\backend
```

Mở **cửa sổ PowerShell thứ hai** tại thư mục repo:

```powershell
# 11. Vào thư mục frontend
Set-Location src\frontend
# 12. Cài thư viện frontend (phiên bản đã khoá)
npm ci
# 13. Chạy frontend → mở http://localhost:5173, đăng nhập QL_TT01 / mật khẩu DEMO_PASSWORD
npm run dev
```

Kết quả mong đợi của bước 9 (in ra màn hình): `NGUỒN DỮ LIỆU: data/sample (bộ mẫu trong repo)`, `ticket=939, ticket_status_log=3237`, `appointment=300`, 30 phiếu MOI (mỗi trung tâm 5), các truy vấn bất biến đều 0. Chạy lại bước 9 lần hai: mọi dòng `NẠP: … = 0`, số dòng không đổi (không nhân đôi). Với bộ CSV đầy đủ trong `data/raw/`: `ticket=7317, ticket_status_log=35719`.

### 3.2. macOS / Linux

```bash
git clone --branch v1.0 https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen.git smartcrm
cd smartcrm
cp .env.example .env                      # rồi sửa DB_USER, DB_PASSWORD, SECRET_KEY, DEMO_PASSWORD
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m pytest
python scripts/setup_all.py
python -m uvicorn app.main:app --app-dir src/backend   # terminal 1
cd src/frontend && npm ci && npm run dev               # terminal 2
```

### 3.3. Cách nhanh nhất: Docker Compose (2 lệnh, không cần cài Python/PostgreSQL/Node)

Cần Docker Desktop đang chạy; cổng 5173, 8000 và 5433 phải trống. Sau bước 1–2 của mục 3.1:

```powershell
# 1. Tạo tệp cấu hình (giá trị mẫu đủ cho chạy thử; đổi mật khẩu/khoá khi triển khai thật)
Copy-Item .env.example .env
# 2. Dựng PostgreSQL → nạp bộ mẫu + tạo tài khoản demo (dịch vụ init) → backend → frontend
docker compose up -d --build
```

Kiểm tra: `docker compose ps` (db, backend, frontend `healthy`; init `exited (0)`), mở http://localhost:5173, đăng nhập `QL_TT01` / `DEMO_PASSWORD`. Dừng: `docker compose down`; xoá cả dữ liệu: `docker compose down -v`. Chi tiết, xử lý sự cố: [docs/deployment-guide.md](docs/deployment-guide.md) (TD-24).

### 3.4. Lệnh tham khảo

- Từng bước riêng của `setup_all.py`: `python scripts\migrate.py`, `load_catalog.py`, `load_tickets.py`, `load_appointments.py`, `generate_demo_accounts.py`.
- Chọn nguồn dữ liệu: biến `DATA_DIR` (để trống: `data/raw/` nếu đủ 7 CSV, ngược lại `data/sample/`).
- Tạo lại bộ mẫu từ dữ liệu đầy đủ: `python scripts\make_sample_data.py`. Sinh lại lịch hẹn: `python scripts\gen_appointments.py` (seed 20261102, TD-09).

## 4. Đăng nhập và API

Mật khẩu mọi tài khoản demo là giá trị `DEMO_PASSWORD` trong `.env`.

| Vai trò | Tên đăng nhập | Màn hình |
|---|---|---|
| Quản lý trung tâm | `QL_TT01` … `QL_TT06` | M1 Phiếu chờ phân công → M2 Phân công kỹ thuật viên |
| Kỹ thuật viên | Mã `technician_code` từ `KT001` đến `KT038`, trừ 3 người đã nghỉ việc (`KT001`, `KT011`, `KT031`) | M3 Phiếu của tôi |

Quản lý chỉ thấy phiếu của trung tâm mình; kỹ thuật viên chỉ thấy phiếu của chính mình (kể cả phiếu đã đóng/đã hủy, lọc bằng ô "Trạng thái"). Thử API trực tiếp tại http://localhost:8000/docs (đăng nhập `POST /api/auth/login`, dán token vào nút Authorize).

| Thực thể | Create | Read | Update | Delete (hủy mềm, QT-13) |
|---|---|---|---|---|
| Phiếu (Quản lý) | `POST /api/tickets` | `GET /api/tickets`, `GET /api/tickets/{id}` | `PUT /api/tickets/{id}` (khi còn MỚI) | `DELETE /api/tickets/{id}` → `DA_HUY` (khi còn MỚI) |
| Lịch hẹn | `POST /api/appointments` | `GET /api/appointments`, `GET /api/appointments/{id}`, `GET /api/tickets/{id}/appointments` | `PUT /api/appointments/{id}` (đổi giờ, chống trùng) | `DELETE /api/appointments/{id}` → `DA_HUY` |

Nghiệp vụ khác: `GET /api/tickets/{id}/technician-suggestions` (gợi ý), `POST`/`PUT /api/tickets/{id}/assignment` (phân công/đổi KTV), `PATCH /api/tickets/{id}/status` (cập nhật trạng thái), `GET /api/technicians/me/tickets` (phiếu của tôi), `POST /api/auth/login`, `GET /api/auth/me`.

Lỗi trả về dạng `{"error": "<MÃ>", "message": "<thông báo>"}`: dữ liệu sai 400, chưa đăng nhập 401, không có quyền 403, không tìm thấy 404, xung đột trạng thái/trùng lịch 409, CSDL tạm thời không khả dụng 503.

## 5. Kiểm thử và minh chứng

| Nhóm | Lệnh | Cần gì | Kết quả gần nhất |
|---|---|---|---|
| **Unit** (quy tắc nghiệp vụ, ánh xạ lỗi, API bằng TestClient) | `python -m pytest` | Không cần DB/frontend | 104 passed |
| **12 test case BT3 TC-01…TC-12** (5 loại, Swagger thật, ảnh `docs/screenshots/`) | `python -m pytest -m bt3` (một case: `-k tc05`) | `.env` có `TEST_DB_NAME=smartcrm_test`, `smartcrm_test` đã nạp, cổng 8000 trống, frontend chạy (TC-11) | 12 passed sau khi sửa BUG-08 |
| Integration PostgreSQL (CRUD, chạy lại không nhân đôi, TC22–TC25) | `python scripts\setup_all.py --with-test-db` một lần, rồi `python -m pytest tests\integration -m integration` | PostgreSQL | 7 passed |
| **18 test case TC01–TC18** (nghiệp vụ + giao diện + e2e) | `python -m pytest -m system` | Frontend đang chạy, cổng 8000 trống, `smartcrm_test` đã nạp | 18 passed (~4 phút) |
| End-to-end luồng chính (có tắt backend thật) | `python -m pytest tests\e2e -m e2e` | như trên | 1 passed |
| UI với API giả lập (TC19–TC21) | `python -m pytest tests\ui -m ui` | Frontend đang chạy | 3 passed |

- Unit test gồm ba loại (luồng đúng, giá trị biên, dữ liệu sai): `tests/test_ticket_rules.py` (vòng đời trạng thái, tay nghề đúng bằng 3, phạm vi xem phiếu), `tests/test_crud_rules.py` (SĐT, hạn cam kết, sửa/hủy phiếu và lịch hẹn, khung giờ trống), `tests/test_appointment_validation.py` (giờ làm việc, biên 17:30–18:00), `tests/test_error_handling.py` (ánh xạ lỗi, 503 khi CSDL tắt, 500 không lộ traceback).
- TC01–TC18 giữ nguyên mã, tên và kỳ vọng của báo cáo Buổi 10 (`tests/tc_catalog.json`); mỗi test tạo lại `smartcrm_work_test` từ `smartcrm_test`, tự chạy backend trên bản sao và chụp ảnh trình duyệt thật vào [docs/test-evidence/](docs/test-evidence/) kèm báo cáo tự sinh [testcase.md](docs/test-evidence/testcase.md). Cách chạy từng test: TD-16.
- Database kiểm thử phải có tên kết thúc bằng `_test`; test không bao giờ ghi vào `smartcrm`.
- Thêm `--headed --slowmo 500` để xem trình duyệt chạy. Integration/e2e báo database đang có kết nối khác: đóng Query Tool/Disconnect rồi chạy lại.

## 6. Tài liệu

- **Bài tập 3:** [Test Plan](docs/test-plan.md) · [Test Report](docs/test-report.md) · [Bug Log](docs/bug-log.md) · [Deployment Guide (EN)](docs/deployment-guide.md) · [Security checklist (EN)](docs/security-checklist.md) · [API reference (EN)](docs/api.md) · [tệp .http](docs/api-requests.http) · ảnh [docs/screenshots/](docs/screenshots/)
- Báo cáo Bài tập 2: [docs/BT2_2374802010556_NguyenQuocViet_V.0.2.1.pdf](docs/BT2_2374802010556_NguyenQuocViet_V.0.2.1.pdf) (ảnh minh chứng gốc: [docs/bt2-evidence/](docs/bt2-evidence/))
- Thay đổi so với thiết kế BT1: [docs/thay-doi-thiet-ke.md](docs/thay-doi-thiet-ke.md) (TD-01 … TD-24; phản hồi BT2: TD-20 … TD-24)
- Nhật ký lỗi: [docs/bug-log.md](docs/bug-log.md)
- Khai báo sử dụng công cụ AI: [docs/ai-disclosure.md](docs/ai-disclosure.md)
- Tích hợp luồng chính và chạy thử clone mới: [docs/tich-hop-end-to-end.md](docs/tich-hop-end-to-end.md)
- Báo cáo nạp dữ liệu: [docs/bao-cao-nap-du-lieu.md](docs/bao-cao-nap-du-lieu.md) · Đặc tả: [docs/srs.md](docs/srs.md)
