# Smart CRM – Phân công kỹ thuật viên và lịch hẹn (Luồng L04)

**Sinh viên:** Nguyễn Quốc Việt – MSSV: 2374802010556
**Track:** SE
**Học phần:** Chuyên đề Tốt nghiệp 1 – Trường ĐH Văn Lang
**Repo:** https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen

## 1. Mô tả bài toán

Mekong Mobile là chuỗi bán lẻ điện thoại, máy tính bảng, phụ kiện kèm dịch vụ bảo hành – sửa chữa (24 cửa hàng, 6 trung tâm bảo hành, 38 kỹ thuật viên, khoảng 260 yêu cầu bảo hành mỗi tháng). Hiện việc phân công kỹ thuật viên do quản lý làm thủ công theo trí nhớ nên:

- **V3:** khối lượng công việc lệch nhau (có người 40 phiếu/tháng, có người 12 phiếu/tháng).
- **V2:** khoảng 15% phiếu quá hạn cam kết (SLA) mà không được cảnh báo.

**Luồng nghiệp vụ (bắt đầu → kết thúc):**

> Phiếu bảo hành ở trạng thái **MỚI** (tạo từ luồng L2) → Quản lý trung tâm xem danh sách phiếu chờ phân công → hệ thống gợi ý kỹ thuật viên phù hợp (cùng trung tâm, tay nghề ≥ 3, khối lượng công việc ít nhất) → Quản lý xác nhận phân công → đặt lịch hẹn giao/nhận thiết bị có kiểm tra trùng lịch → Kỹ thuật viên cập nhật trạng thái phiếu đến **HOÀN TẤT**.

- **Actor:** Quản lý trung tâm, Kỹ thuật viên.
- **Đối tượng:** Phiếu bảo hành (`ticket`), Kỹ thuật viên (`technician`), Lịch hẹn (`appointment`).
- **Kết thúc khi:** phiếu được gán đúng một kỹ thuật viên, lịch hẹn được lưu, trạng thái phiếu và lịch sử chuyển trạng thái được ghi thành công vào CSDL.

Vòng đời trạng thái (phạm vi L04):

```
MỚI → ĐÃ PHÂN CÔNG → ĐANG XỬ LÝ → (CHỜ LINH KIỆN) → HOÀN TẤT
```

Không được quay lại trạng thái trước (QT-06).

## 2. Phạm vi

### Làm

| Mã | User Story | MoSCoW |
|---|---|---|
| US1 | Xem danh sách phiếu MỚI của trung tâm, sắp theo mức ưu tiên rồi hạn cam kết | SHOULD |
| US2 | Gợi ý kỹ thuật viên phù hợp cho phiếu (QT-08, khối lượng công việc) | **MUST** |
| US3 | Gán kỹ thuật viên cho phiếu, chuyển sang ĐÃ PHÂN CÔNG, ghi lịch sử | **MUST** |
| US4 | Đổi kỹ thuật viên, bắt buộc nhập lý do (QT-07) | SHOULD |
| US5 | Kỹ thuật viên xem phiếu được gán cho mình, sắp theo hạn cam kết | SHOULD |
| US6 | Đặt lịch hẹn giao/nhận thiết bị, chặn trùng lịch | **MUST** |
| US7 | Kỹ thuật viên cập nhật trạng thái phiếu đúng vòng đời, lưu lịch sử (QT-06) | SHOULD |
| US8 | Xem số phiếu đang giữ và quá hạn của từng kỹ thuật viên | COULD (chỉ ghi vào hướng mở rộng) |

**Nghiệp vụ có logic xử lý chính:** thuật toán gợi ý/phân công kỹ thuật viên (cùng trung tâm, tay nghề ≥ 3, khối lượng ít nhất), kiểm tra trùng lịch hẹn, kiểm soát vòng đời trạng thái trong một giao dịch, xử lý xung đột khi 2 quản lý phân công đồng thời.

**Quy tắc nghiệp vụ áp dụng:** QT-04 (chỉ đọc/hiển thị hạn cam kết), QT-06, QT-07, QT-08, QT-13, QT-14, QT-15.

### Không làm

| # | Hạng mục ngoài phạm vi |
|---|---|
| W1 | Tiếp nhận, tạo phiếu, phân loại nhóm sự cố và mức ưu tiên (thuộc L2) |
| W2 | Quản lý tồn kho, xuất linh kiện (thuộc L5) |
| W3 | Chuyển phiếu sang ĐÃ ĐÓNG / ĐÃ HỦY, gửi khảo sát hài lòng (thuộc L2/L8) |
| W4 | Gửi SMS/Zalo nhắc lịch hẹn cho khách hàng |
| W5 | Tự động chuyển phiếu sang trung tâm khác khi không có kỹ thuật viên phù hợp |
| W6 | Báo cáo tổng hợp quá hạn toàn công ty, dashboard Ban giám đốc (thuộc L6) |
| W7 | Tối ưu lộ trình, tính thời gian di chuyển của kỹ thuật viên |

## 3. Công nghệ sử dụng

| Thành phần | Công nghệ |
|---|---|
| Ngôn ngữ / Runtime | Python 3.11+ |
| Framework API | FastAPI |
| Truy cập dữ liệu (ORM) | SQLAlchemy |
| Cơ sở dữ liệu | PostgreSQL 16 |
| Frontend | ReactJS (Vite) |
| Kiểm thử | pytest |
| Tài liệu API | OpenAPI do FastAPI tự sinh (`/docs`) |
| Đóng gói | Dockerfile + docker-compose |
| Công cụ phát triển | VS Code, Postman, Git/GitHub |

## 4. Cấu trúc thư mục

```
smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen/
├── docs/                    # SRS, tiêu chí GWT, khai báo AI
│   └── diagrams/            # Use case, ERD, file .drawio gốc
├── data/
│   └── sample/              # Mẫu nhỏ vài trăm dòng (CSV lớn KHÔNG commit)
├── src/
│   ├── backend/             # FastAPI: routers, services, models, schemas
│   └── frontend/            # ReactJS (Vite)
├── tests/                   # pytest (unit + API + đồng thời)
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

## 5. Hướng dẫn cài đặt & chạy

> Mục này được hoàn thiện dần theo tiến độ hiện thực. Mục tiêu (NFR5): người khác clone về và chạy được bằng đúng 2 lệnh.

### 5.1. Yêu cầu

- Git, Docker Desktop (chạy bằng docker-compose)
- Nếu chạy thủ công: Python 3.11+, Node.js LTS, PostgreSQL 16

### 5.2. Lấy mã nguồn và cấu hình

```bash
git clone https://github.com/NguyenQuocViet23/smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen.git
cd smartcrm-2374802010556-phan-cong-ky--thuat-vien-va-lich-hen
cp .env.example .env        # Windows: copy .env.example .env, rồi điền giá trị thật
```

### 5.3. Chạy bằng Docker (khuyến nghị)

```bash
docker-compose up -d --build
```

- Backend: http://localhost:8000 · Tài liệu API: http://localhost:8000/docs
- Frontend: http://localhost:5173

### 5.4. Chạy thủ công (phát triển)

```bash
# Backend
python -m venv .venv
# Windows: .venv\Scripts\activate    macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.backend.main:app --reload

# Frontend
cd src/frontend
npm install
npm run dev
```

### 5.5. Dữ liệu

- **Dữ liệu có sẵn (Mekong Mobile, dữ liệu mô phỏng):** `service_centers.csv`, `technicians.csv`, `technician_skills.csv`, `issue_categories.csv`, `tickets_history.csv` (7.800 phiếu), `ticket_status_log.csv`. Tải bộ đầy đủ trên LMS, đặt vào `data/raw/` (không commit); chỉ commit mẫu nhỏ trong `data/sample/`.
- **Dữ liệu sinh bổ sung** (lịch hẹn, gắn với phiếu có thật):

```bash
python gen_sample.py --entity appointment --rows 300 --seed <SEED> \
       --link tickets_history.csv --out appointments.csv
```

  **Seed sử dụng:** `<điền giá trị seed>` (ghi lại để tái lập kết quả).

### 5.5. Kiểm thử

```bash
pytest
```

### 5.6. API chính

| Phương thức | Đường dẫn | Mục đích | Story |
|---|---|---|---|
| GET | `/api/tickets?status=MOI` | Danh sách phiếu chờ phân công | US1 |
| GET | `/api/tickets/{id}/technician-suggestions` | Gợi ý kỹ thuật viên | US2 |
| POST | `/api/tickets/{id}/assignment` | Gán kỹ thuật viên | US3 |
| PUT | `/api/tickets/{id}/assignment` | Đổi kỹ thuật viên (có lý do) | US4 |
| GET | `/api/technicians/me/tickets` | Phiếu gán cho tôi | US5 |
| POST | `/api/appointments` | Tạo lịch hẹn | US6 |
| PATCH | `/api/tickets/{id}/status` | Cập nhật trạng thái | US7 |

## 6. Khai báo sử dụng công cụ AI

| Công cụ | Dùng vào việc gì | Cách tự kiểm chứng |
|---|---|---|
| Claude (Anthropic) | Soạn bản nháp SRS, tiêu chí chấp nhận GWT và README từ case study, phiếu phạm vi và tài liệu buổi 3–4 | Đối chiếu từng quy tắc QT-xx với case study; rà lại giả định A1–A6 và ví dụ API với dữ liệu mẫu thật; chạy checklist buổi 4; chạy test để xác nhận hành vi |
