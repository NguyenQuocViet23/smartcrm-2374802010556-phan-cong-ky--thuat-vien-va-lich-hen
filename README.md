# Smart CRM – Phân công kỹ thuật viên và lịch hẹn (L04)

**Đơn vị mô phỏng:** Mekong Mobile
**Sinh viên:** Nguyễn Quốc Việt – MSSV 2374802010556
**Track:** SE · Chuyên đề Tốt nghiệp 1 – Trường ĐH Văn Lang

## 1. Mô tả bài toán và phạm vi

Smart CRM hỗ trợ Quản lý trung tâm phân công phiếu bảo hành cho kỹ thuật viên cùng trung tâm, đủ tay nghề; hỗ trợ đặt lịch giao/nhận thiết bị và giúp Kỹ thuật viên cập nhật trạng thái phiếu. Hạn cam kết được đọc/hiển thị, không sửa trong luồng L04.

Luồng trạng thái: `MOI → DA_PHAN_CONG → DANG_XU_LY → CHO_LINH_KIEN → HOAN_TAT` (có thể đi thẳng `DANG_XU_LY → HOAN_TAT`).

**Trong phạm vi:** danh sách phiếu mới, gợi ý kỹ thuật viên theo trung tâm/tay nghề/khối lượng, phân công và đổi kỹ thuật viên, phiếu của tôi, lịch hẹn giao/nhận có chống trùng, cập nhật trạng thái, xác thực demo, ba màn hình M1/M2/M3.

**Ngoài phạm vi:** UC8/báo cáo khối lượng toàn trung tâm, tiếp nhận phiếu L2, tồn kho/linh kiện, SMS/Zalo, điều chuyển trung tâm, hủy lịch hẹn trên UI, đóng/hủy phiếu. Phần đã cắt và lý do: [docs/thay-doi-thiet-ke.md](docs/thay-doi-thiet-ke.md).

## 2. Công nghệ và cấu trúc

| Thành phần | Công nghệ |
|---|---|
| Backend | Python 3.11+, FastAPI, SQLAlchemy, psycopg |
| Cơ sở dữ liệu | PostgreSQL 16 trở lên (đã chạy thử trên 18) |
| Frontend | React, Vite, React Router (Node.js LTS) |
| Kiểm thử | pytest, TestClient, pytest-playwright (Chromium) |
| Triển khai | Docker Compose (tùy chọn) |

```text
db/                         schema 6 bảng và migration
data/raw/                   CSV case-study lấy từ LMS (không commit)
data/sample/appointments.csv  lịch hẹn sinh với seed 20261102 (có commit)
scripts/                    migration, nạp dữ liệu, sinh tài khoản demo
src/backend/app/            routers (HTTP), services (quy tắc nghiệp vụ), core
src/frontend/src/           api/ (client.js + *.api.js), components/, pages/
tests/                      unit test; ui/ (API giả lập); integration/; e2e/
docs/                       SRS, sơ đồ, báo cáo, ảnh minh chứng (docs/test-evidence/)
```

## 3. Các bước dựng hệ thống

Cần cài sẵn: **Git**, **Python 3.11+**, **Node.js LTS**, **PostgreSQL 16+** (lệnh `psql` có trong PATH) và **bộ 7 tệp CSV case-study** tải từ LMS: `service_centers.csv`, `issue_categories.csv`, `technicians.csv`, `technician_skills.csv`, `tickets_history.csv`, `ticket_status_log.csv`, `customers_raw.csv`. Bộ CSV này không nằm trong repo (`data/raw/` bị `.gitignore`).

Mỗi bước là một lệnh, chạy từ thư mục gốc repo trừ khi có ghi chú khác.

### 3.1. Windows PowerShell

```powershell
# 1. Lấy mã nguồn
git clone https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen.git
# 2. Vào thư mục repo
Set-Location smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen
# 3. Tạo tệp cấu hình
Copy-Item .env.example .env
# 4. Điền DB_USER, DB_PASSWORD, SECRET_KEY (≥ 32 ký tự), DEMO_PASSWORD rồi lưu lại
notepad .env
# 5. Tạo môi trường ảo Python
py -m venv .venv
# 6. Kích hoạt môi trường ảo
.\.venv\Scripts\Activate.ps1
# 7. Cài thư viện backend và kiểm thử
python -m pip install -r requirements-dev.txt
# 8. Cài trình duyệt Chromium cho kiểm thử giao diện
python -m playwright install chromium
# 9. Chép 7 tệp CSV từ LMS vào data\raw\ (thay <thư-mục-CSV> bằng nơi bạn đã tải về)
Copy-Item <thư-mục-CSV>\*.csv data\raw\
# 10. Tạo database chính
psql -U postgres -c "CREATE DATABASE smartcrm;"
# 11. Tạo database kiểm thử
psql -U postgres -c "CREATE DATABASE smartcrm_test;"
# 12. Tạo 6 bảng trong database chính
python scripts\migrate.py
# 13. Nạp trung tâm, kỹ thuật viên, tay nghề
python scripts\load_catalog.py
# 14. Nạp phiếu và lịch sử trạng thái (tạo 30 phiếu MOI, seed 20260901)
python scripts\load_tickets.py
# 15. Nạp 300 lịch hẹn từ data\sample\appointments.csv
python scripts\load_appointments.py
# 16. Sinh tài khoản demo vào data\processed\demo_accounts.json
python scripts\generate_demo_accounts.py
# 17. Chuyển sang database kiểm thử cho các bước 18–21
$env:DB_NAME = "smartcrm_test"
# 18. Tạo 6 bảng trong database kiểm thử
python scripts\migrate.py
# 19. Nạp danh mục vào database kiểm thử
python scripts\load_catalog.py
# 20. Nạp phiếu vào database kiểm thử
python scripts\load_tickets.py
# 21. Nạp lịch hẹn vào database kiểm thử
python scripts\load_appointments.py
# 22. Trở lại database chính
Remove-Item Env:DB_NAME
# 23. Chạy backend (giữ cửa sổ này mở) → http://localhost:8000/docs
python -m uvicorn app.main:app --app-dir src\backend
```

Mở **cửa sổ PowerShell thứ hai** tại thư mục gốc repo:

```powershell
# 24. Vào thư mục frontend
Set-Location src\frontend
# 25. Cài thư viện frontend
npm ci
# 26. Chạy frontend → mở http://localhost:5173
npm run dev
```

Kết quả mong đợi sau bước 13–15 (in ra màn hình và kiểm chứng ở [docs/bao-cao-nap-du-lieu.md](docs/bao-cao-nap-du-lieu.md)): `service_center` 6, `technician` 38, `technician_skill` 159, `ticket` 7.317, `ticket_status_log` 35.719, `appointment` 300. Các script dùng `ON CONFLICT DO NOTHING`, chạy lại không nhân đôi dòng. Nếu `psql` báo database đã tồn tại ở bước 10–11 thì bỏ qua bước đó.

### 3.2. macOS / Linux

```bash
git clone https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen.git
cd smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen
cp .env.example .env                      # rồi điền DB_USER, DB_PASSWORD, SECRET_KEY, DEMO_PASSWORD
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-dev.txt
python -m playwright install chromium
cp <thư-mục-CSV>/*.csv data/raw/
createdb smartcrm
createdb smartcrm_test
python scripts/migrate.py
python scripts/load_catalog.py
python scripts/load_tickets.py
python scripts/load_appointments.py
python scripts/generate_demo_accounts.py
DB_NAME=smartcrm_test python scripts/migrate.py
DB_NAME=smartcrm_test python scripts/load_catalog.py
DB_NAME=smartcrm_test python scripts/load_tickets.py
DB_NAME=smartcrm_test python scripts/load_appointments.py
python -m uvicorn app.main:app --app-dir src/backend   # terminal 1
cd src/frontend && npm ci && npm run dev               # terminal 2
```

### 3.3. Tùy chọn: Docker Compose

`docker compose up -d --build` dựng PostgreSQL (cổng host `5433`), backend (tự chạy migration) và frontend. Compose **không** tự nạp dữ liệu: sau khi container chạy, thực hiện bước 13–16 ở mục 3.1 với `$env:DB_PORT = "5433"` (backend đọc `data/processed/demo_accounts.json` qua volume ở mỗi lần đăng nhập). Database trong Docker là database riêng, ban đầu trống. Phần này chưa được chạy lại trong lần cập nhật README gần nhất (Docker daemon không chạy trên máy kiểm tra); cách chạy được kiểm chứng là mục 3.1.

### 3.4. Sinh lại lịch hẹn (không bắt buộc)

`data/sample/appointments.csv` đã được sinh sẵn. Muốn sinh lại từ database đã nạp phiếu (seed `20261102`, 270 `DA_HEN` + 30 `DA_HUY`, từ 2026-11-03 đến 2027-01-30): `python scripts\gen_appointments.py`. Lý do không dùng `gen_sample.py` của case-study: TD-09.

## 4. Đăng nhập và API

Mật khẩu mọi tài khoản demo là giá trị `DEMO_PASSWORD` trong `.env`.

| Vai trò | Tên đăng nhập | Màn hình |
|---|---|---|
| Quản lý trung tâm | `QL_TT01` … `QL_TT06` | M1 Phiếu chờ phân công → M2 Phân công kỹ thuật viên |
| Kỹ thuật viên | `KT001` … `KT038` (mã `technician_code`) | M3 Phiếu của tôi |

Quản lý chỉ thấy phiếu của trung tâm mình; kỹ thuật viên chỉ thấy phiếu của chính mình (kể cả phiếu đã đóng/đã hủy, lọc bằng ô "Trạng thái").

| Phương thức | Endpoint | Nghiệp vụ |
|---|---|---|
| POST / GET | `/api/auth/login`, `/api/auth/me` | Đăng nhập và thông tin phiên |
| GET | `/api/tickets`, `/api/tickets/{id}` | Danh sách phiếu theo trung tâm, chi tiết phiếu |
| GET | `/api/tickets/{id}/technician-suggestions` | Gợi ý kỹ thuật viên |
| POST / PUT | `/api/tickets/{id}/assignment` | Phân công / đổi người |
| GET | `/api/technicians/me/tickets` | Phiếu của kỹ thuật viên |
| POST / GET | `/api/appointments`, `/api/tickets/{id}/appointments` | Đặt lịch giao/nhận, xem lịch của phiếu |
| PATCH | `/api/tickets/{id}/status` | Cập nhật trạng thái |

## 5. Kiểm thử và minh chứng

| Nhóm | Lệnh | Cần gì | Kết quả gần nhất |
|---|---|---|---|
| Unit (quy tắc nghiệp vụ, API bằng TestClient) | `python -m pytest` | Không cần DB/frontend | 65 passed |
| UI với API giả lập (TC19–TC21) | `python -m pytest tests\ui -m ui` | Frontend đang chạy | 3 passed |
| Integration PostgreSQL (TC22–TC25) | `$env:TEST_DB_NAME="smartcrm_test"; python -m pytest tests\integration -m integration` | `smartcrm`, `smartcrm_test` đã nạp | 4 passed |
| **End-to-end luồng chính** | `$env:TEST_DB_NAME="smartcrm_test"; python -m pytest tests\e2e -m e2e` | Frontend đang chạy, cổng 8000 trống | 1 passed |

- Unit test cho lớp nghiệp vụ nằm ở `tests/test_ticket_rules.py` (vòng đời trạng thái, điều kiện kỹ thuật viên, phạm vi xem phiếu) và `tests/test_appointment_validation.py` (giờ làm việc, biên 17:30–18:00), gồm ba loại: luồng đúng, giá trị biên, dữ liệu sai.
- Test e2e tự tạo lại database làm việc `smartcrm_work_test` từ `smartcrm_test`, tự chạy backend trên đó (không đụng `smartcrm`), điều khiển giao diện thật, kiểm tra kết quả bằng SQL và lưu ảnh vào [docs/test-evidence/](docs/test-evidence/). Diễn giải luồng, đầu vào/đầu ra và các chỗ đứt gãy: [docs/tich-hop-end-to-end.md](docs/tich-hop-end-to-end.md).
- Thêm `--headed --slowmo 500` để xem trình duyệt chạy. Đặt `EVIDENCE=1` để sinh báo cáo `export/testcase.md` và ảnh chụp trình duyệt của test UI vào `export/test-evidence/`.
- Integration/e2e báo database nguồn đang có kết nối khác: đóng Query Tool/Disconnect database tương ứng rồi chạy lại.

## 6. Khai báo sử dụng công cụ AI

Chi tiết theo BT1: [docs/ai-declaration.md](docs/ai-declaration.md). Kết quả chạy được ghi riêng; phần chưa chạy không được khai báo là hoàn thành.

| Công cụ AI | Dùng vào việc gì | Cách tự kiểm chứng |
|---|---|---|
| Claude | Bản nháp SRS, sơ đồ; viết prompt và hỗ trợ script nạp dữ liệu | Đối chiếu schema, xem diff Git, chạy truy vấn SELECT bất biến |
| GitHub Copilot | Sinh dữ liệu lịch hẹn, kiểm tra tài liệu và dữ liệu; hỗ trợ chỉnh sửa script, test, README | Số liệu SELECT, truy vấn bất biến, đối chiếu SRS/schema, `git diff` trước khi commit |
| Claude Code | Rà checklist Buổi 10; tách quy tắc nghiệp vụ sang `services/ticket_rules.py` và viết unit test; viết test e2e; bộ lọc trạng thái M3; cập nhật README và tài liệu | Chạy lại unit/UI/integration/e2e, xem từng ảnh minh chứng, đối chiếu số dòng bằng SQL, xem `git diff` |
