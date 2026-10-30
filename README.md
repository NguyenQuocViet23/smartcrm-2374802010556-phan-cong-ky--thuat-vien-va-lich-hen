# Smart CRM – Phân công kỹ thuật viên và lịch hẹn (L04)

**Đơn vị mô phỏng:** Mekong Mobile
**Sinh viên:** Nguyễn Quốc Việt – MSSV 2374802010556
**Track:** SE · Chuyên đề Tốt nghiệp 1 – Trường ĐH Văn Lang

## 1. Mô tả bài toán

Smart CRM hỗ trợ Quản lý trung tâm phân công phiếu bảo hành cho kỹ thuật viên cùng trung tâm, đủ tay nghề; hỗ trợ đặt lịch giao/nhận thiết bị và giúp Kỹ thuật viên cập nhật trạng thái phiếu. Hạn cam kết được đọc/hiển thị, không sửa trong luồng L04.

Luồng trạng thái: `MOI → DA_PHAN_CONG → DANG_XU_LY → CHO_LINH_KIEN → HOAN_TAT` (có thể đi thẳng `DANG_XU_LY → HOAN_TAT`).

## 2. Phạm vi

**Trong phạm vi:** danh sách phiếu mới, gợi ý kỹ thuật viên theo trung tâm/tay nghề/khối lượng, phân công và đổi kỹ thuật viên, phiếu của tôi, lịch hẹn giao/nhận có chống trùng, cập nhật trạng thái, xác thực demo, M1/M2/M3.

**Ngoài phạm vi:** UC8/báo cáo khối lượng toàn trung tâm, tiếp nhận phiếu L2, tồn kho/linh kiện, SMS/Zalo, điều chuyển trung tâm, hủy lịch hẹn trên UI, đóng/hủy phiếu.

## 3. Công nghệ và cấu trúc

| Thành phần | Công nghệ |
|---|---|
| Backend | Python, FastAPI, SQLAlchemy, psycopg |
| Cơ sở dữ liệu | PostgreSQL 16 |
| Frontend | React, Vite, React Router |
| Kiểm thử | pytest, TestClient, pytest-playwright, Pillow |
| Triển khai | Docker Compose |

```text
db/                         schema 6 bảng và migration
data/raw/                   CSV case-study (không commit)
data/sample/                mẫu dữ liệu (hiện chưa có CSV)
scripts/                    migration và seed
src/backend/app/            routers, schemas, services/repositories hiện có
src/frontend/src/           API client, components, pages
tests/                      kiểm thử
docs/                       SRS, sơ đồ, báo cáo và ảnh kiểm thử
```

## 4. Yêu cầu môi trường và cấu hình

- Python 3.11 trở lên, Node.js LTS (Docker frontend dùng Node 22), Git.
- PostgreSQL 16 hoặc Docker Desktop với Docker Compose v2.
- Chromium nếu chạy kiểm thử UI bằng Playwright.
- Sao chép `.env.example` thành `.env`, sau đó điền `DB_USER`, `DB_PASSWORD`, `SECRET_KEY` (ít nhất 32 ký tự), `DEMO_PASSWORD`, và `TEST_DATABASE_URL`. Không commit `.env`.
- API dùng `DATABASE_URL` nếu đặt; nếu không, dùng `DB_HOST`, `DB_PORT`, `DB_NAME`, `DB_USER`, `DB_PASSWORD`.
- Tài khoản demo được sinh trong `data/processed/demo_accounts.json`, mật khẩu được hash PBKDF2; file này không được commit.

## 5. Cài đặt, chạy và kiểm thử

### 5.1. Lấy mã nguồn

Chạy từ thư mục cha mà bạn muốn đặt repo.

**Windows PowerShell**

```powershell
git clone https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen.git
```
```powershell
Set-Location smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen
```
```powershell
Copy-Item .env.example .env
```

**macOS / Linux**

```bash
git clone https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen.git
```
```bash
cd smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen
```
```bash
cp .env.example .env
```

### 5.2. Cách 1 – Docker Compose

Điền `.env` trước khi chạy. Từ thư mục gốc repo:

```powershell
docker compose up -d --build
```

Frontend: http://localhost:5173 · Backend: http://localhost:8000 · Swagger: http://localhost:8000/docs

Compose tự khởi động PostgreSQL, áp dụng migration rồi chạy API và Vite. Docker không tự nạp dữ liệu mẫu: cần đủ CSV và seed thành công mới có thể đăng nhập demo. **Hiện dữ liệu log/lịch hẹn còn thiếu nên luồng demo đầy đủ chưa khả dụng.**

### 5.3. Cách 2 – Chạy thủ công trên Windows

Từ thư mục gốc repo:

```powershell
py -m venv .venv
```
```powershell
.\.venv\Scripts\Activate.ps1
```
```powershell
python -m pip install -r requirements-dev.txt
```
```powershell
psql -U postgres -c "CREATE DATABASE smartcrm;"
```
```powershell
psql -U postgres -c "CREATE DATABASE smartcrm_test;"
```
```powershell
python scripts\migrate.py
```
```powershell
$env:DB_NAME = "smartcrm_test"
```
```powershell
python scripts\migrate.py
```
```powershell
$env:DB_NAME = "smartcrm"
```

Khởi động backend trong cửa sổ terminal thứ nhất:

```powershell
python -m uvicorn app.main:app --app-dir src\backend --reload
```

Từ thư mục gốc, terminal thứ hai:

```powershell
Set-Location src\frontend
```
```powershell
npm ci
```
```powershell
npm run dev
```

### 5.4. Chạy thủ công trên macOS / Linux

Từ thư mục gốc repo:

```bash
python3 -m venv .venv
```
```bash
source .venv/bin/activate
```
```bash
python -m pip install -r requirements-dev.txt
```
```bash
createdb smartcrm
```
```bash
createdb smartcrm_test
```
```bash
python scripts/migrate.py
```
```bash
DB_NAME=smartcrm_test python scripts/migrate.py
```

Khởi động API trong terminal thứ nhất:

```bash
python -m uvicorn app.main:app --app-dir src/backend --reload
```

Khởi động UI trong terminal thứ hai:

```bash
cd src/frontend
```
```bash
npm ci
```
```bash
npm run dev
```

### 5.5. Dữ liệu và seed

Đặt bộ CSV case-study được cấp trên LMS vào `data/raw/`. Repo hiện có `service_centers.csv`, `issue_categories.csv`, `technicians.csv`, `technician_skills.csv`, `tickets_history.csv`, `customers_raw.csv`; **chưa có** `ticket_status_log.csv`, `appointments.csv` hoặc `gen_sample.py`/`tools/gen_sample.py`.

Kết quả khảo sát thực tế: 7.800 ticket nối được với khách qua `tickets_history.customer_id → customers_raw.record_id`; 483 phiếu không có số điện thoại hợp lệ sau chuẩn hóa và cần reject theo QT-02. Status hiện có trong CSV đã là mã không dấu; bộ chuẩn hóa chấp nhận cả mã này và alias có dấu theo prompt.

Seed đầy đủ hiện **chưa thể chạy**. Mặc định script dừng nếu không có mapping đã xác minh cho log và lịch hẹn; không tự sinh các dòng thay thế. Khi đã có đủ nguồn và mapping, lệnh dự kiến:

```powershell
python scripts\seed_real_data.py --csv-dir data\raw --seed 20261023
```

Chỉ để kiểm tra các bảng lõi trong môi trường thử nghiệm sau khi đã áp dụng migration (không dùng cho TC01–TC18):

```powershell
python scripts\seed_real_data.py --csv-dir data\raw --seed 20261023 --allow-incomplete --db-url $env:TEST_DATABASE_URL
```

`--allow-incomplete` báo seed là chưa hoàn chỉnh và trả mã thoát `2`. `data/sample/` hiện chưa chứa CSV; không dùng thư mục này để khẳng định có thể chạy nhanh. Báo cáo số liệu: [docs/bao-cao-nap-du-lieu.md](docs/bao-cao-nap-du-lieu.md).

### 5.6. Đăng nhập và API

Sau khi seed tạo tài khoản, tên đăng nhập Quản lý có dạng `QL_<center_code>`; Kỹ thuật viên dùng `technician_code`. Mật khẩu là giá trị `DEMO_PASSWORD` trong `.env`. Tệp tài khoản cục bộ nằm ở `data/processed/demo_accounts.json`.

| Phương thức | Endpoint | Nghiệp vụ |
|---|---|---|
| POST / GET | `/api/auth/login`, `/api/auth/me` | Đăng nhập và thông tin phiên |
| GET | `/api/tickets` | Danh sách phiếu theo trung tâm |
| GET | `/api/tickets/{id}/technician-suggestions` | Gợi ý kỹ thuật viên |
| POST / PUT | `/api/tickets/{id}/assignment` | Phân công / đổi người |
| GET | `/api/technicians/me/tickets` | Phiếu của kỹ thuật viên |
| POST | `/api/appointments` | Đặt lịch giao/nhận |
| PATCH | `/api/tickets/{id}/status` | Cập nhật trạng thái |

### 5.7. Kiểm thử, bằng chứng và trạng thái hiện tại

#### Kiểm thử giao diện bằng Playwright

Cài Chromium một lần cho môi trường Python hiện tại:

```powershell
python -m playwright install chromium
```

Để chạy test giao diện và quan sát cửa sổ Chromium:

1. Mở terminal thứ nhất tại thư mục gốc repo, khởi động frontend:

   ```powershell
   Set-Location src\frontend
   npm ci
   npm run dev
   ```

2. Đợi Vite sẵn sàng tại `http://localhost:5173`, rồi mở terminal thứ hai tại thư mục gốc repo và chạy:

   ```powershell
   python -m pytest tests\ui -v -m ui --headed --slowmo 500
   ```

Các test UI thao tác trên đăng nhập/đăng xuất, lọc và phân trang phiếu, điều hướng phân công, đặt lịch, cập nhật trạng thái; đồng thời kiểm tra đăng nhập sai, lỗi API/mất kết nối, lịch bị trùng, ngày/giờ không hợp lệ và khả năng thử lại. API được giả lập nên nhóm này không cần backend, PostgreSQL, tài khoản demo hoặc dữ liệu thật. `--headed` mở cửa sổ Chromium, còn `--slowmo 500` làm chậm thao tác để dễ quan sát. Bỏ `--headed` để chạy Chromium ẩn hoặc bỏ `--slowmo 500` để chạy nhanh hơn. Các test có marker `ui` được loại khỏi lệnh pytest mặc định để `python -m pytest -v` không yêu cầu frontend đang chạy.

#### Kiểm thử backend

```powershell
python -m pytest -v
```

Lệnh kiểm thử sẽ tự xóa ảnh cũ, chụp kết quả từng test và sinh:

- `export/test-evidence/_summary.png` và ảnh PNG từng test case.
- `export/testcase.md`, gồm đầy đủ số liệu, chi tiết từng test và cảnh báo.

Để dùng thư mục xuất khác, đặt biến `EXPORT_DIR` trước khi chạy:

```powershell
$env:EXPORT_DIR="export"
python -m pytest -v
```

Các test backend dùng `TestClient` để kiểm tra API và validation; lần xác minh gần nhất đạt `25 passed`. Lệnh này không cần frontend hoặc PostgreSQL.

Lần xác minh gần nhất: bộ UI chạy ở chế độ headed đạt `3 passed`; `npm run build` thành công. Test UI giả lập **không thay thế** 18 acceptance test tích hợp với PostgreSQL và dữ liệu thật. Hiện chưa có thư mục `tests\service`, và ảnh UI PASS chưa được tự động lưu vào `docs/test-evidence/`.

Các blockers trước khi có thể xác nhận đủ 18 acceptance test tích hợp gồm: bổ sung `ticket_status_log.csv` và dữ liệu/script lịch hẹn; chạy PostgreSQL; hoàn thiện nhập log/lịch hẹn, sinh phiếu MỚI và reset dữ liệu; tạo test TC01–TC18; nạp dữ liệu thật vào hai database.

## 6. Khai báo sử dụng công cụ AI

Claude đã hỗ trợ bản nháp SRS và sơ đồ theo khai báo ban đầu trong `docs/ai-declaration.md`. Copilot SDK trong VS Code được dùng để đọc prompt, triển khai các phần có thể xác minh, viết kiểm tra và cập nhật tài liệu. Kết quả chạy được ghi riêng; các phần thiếu dữ liệu hoặc chưa chạy không được khai báo là hoàn thành.
