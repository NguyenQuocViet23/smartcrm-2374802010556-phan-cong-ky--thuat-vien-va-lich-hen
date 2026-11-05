# Báo cáo nạp dữ liệu thật

## 1. Kết quả

**Trạng thái: đã nạp đủ sáu bảng** vào `smartcrm` (dùng cho demo) và `smartcrm_test` (dùng cho integration/e2e) bằng cùng một pipeline. Số dòng được kiểm lại bằng `SELECT count(*)` ngày 06/11/2026, hai database cho kết quả giống nhau:

| Bảng | Số dòng |
|---|---:|
| `service_center` | 6 |
| `technician` | 38 |
| `technician_skill` | 159 |
| `ticket` | 7.317 |
| `ticket_status_log` | 35.719 |
| `appointment` | 300 (270 `DA_HEN`, 30 `DA_HUY`) |

Mỗi trung tâm có đúng 5 phiếu `MOI` (30 phiếu, seed `20260901`). Fixture integration (`tests/integration/conftest.py`) dừng nếu số dòng của `smartcrm` hoặc `smartcrm_test` khác bảng trên.

## 2. Pipeline

Thứ tự chạy và lệnh: README mục 3. Các script dùng `ON CONFLICT DO NOTHING`, nên chạy lại không nhân đôi dòng.

| Script | Nguồn | Đích |
|---|---|---|
| `scripts/migrate.py` | `db/migrations/*.sql` | Sáu bảng, chỉ mục, ràng buộc |
| `scripts/load_catalog.py` | `service_centers.csv`, `technicians.csv`, `technician_skills.csv`, `issue_categories.csv` | `service_center`, `technician`, `technician_skill` |
| `scripts/load_tickets.py` | `tickets_history.csv`, `customers_raw.csv`, `ticket_status_log.csv` | `ticket`, `ticket_status_log`; chọn 30 phiếu MOI |
| `scripts/gen_appointments.py` (tùy chọn) | Database đã nạp phiếu | `data/sample/appointments.csv` (seed `20261102`) |
| `scripts/load_appointments.py` | `data/sample/appointments.csv` | `appointment` |
| `scripts/generate_demo_accounts.py` | `service_center`, `technician`, `DEMO_PASSWORD` | `data/processed/demo_accounts.json` (không commit) |

## 3. Đối chiếu nguồn → đích

| Nguồn | Dòng nguồn | Dòng đã nạp | Chênh lệch và lý do |
|---|---:|---:|---|
| `service_centers.csv` | 6 | 6 | — |
| `technicians.csv` | 38 | 38 | — |
| `technician_skills.csv` | 159 | 159 | — |
| `issue_categories.csv` | 6 | không có bảng đích | Ánh xạ `category_id` → `category_code` (TD-11) |
| `tickets_history.csv` | 7.800 | 7.317 | 483 phiếu bị loại vì không có số điện thoại hợp lệ sau chuẩn hoá (QT-02, TD-07) |
| `ticket_status_log.csv` | 38.112 | 35.719 | 2.363 dòng thuộc 483 phiếu bị loại; 30 dòng `MOI → DA_PHAN_CONG` bị cắt để 30 phiếu chọn làm MOI kết thúc ở `MOI` (TD-08) |
| `customers_raw.csv` | 67.037 | không có bảng đích | Chỉ dùng tra `record_id` lấy họ tên, số điện thoại; khớp 7.800/7.800 phiếu |
| `data/sample/appointments.csv` | 300 | 300 | — |

Tệp ghi lý do loại (thư mục `reports/`, không commit các CSV này): `load_tickets_rejects.csv` (2.846 dòng = 483 "thiếu SĐT" + 2.363 "phiếu cha bị loại"), `load_catalog_rejects.csv` (0 dòng), `moi_tickets_seed20260901.csv` (30 phiếu MOI), `appointment_edge_cases.csv` (các lịch liền kề, lịch hủy trùng lịch hoạt động, phiếu có cả GIAO và NHAN).

## 4. Dữ liệu có ích cho demo và kiểm thử

- Cặp `(center_id=1, NUOC_VAO)` không có kỹ thuật viên đủ điều kiện → gợi ý rỗng (TC22).
- Các cặp chỉ có đúng một kỹ thuật viên đủ điều kiện: `(1, SAC)`, `(1, PHAN_MEM)`, `(1, KHAC)`, `(5, NUOC_VAO)` (TC23).
- 3 kỹ thuật viên `is_active = false`; 125 phiếu đang xử lý nằm ở kỹ thuật viên đã nghỉ.
- Mỗi kỹ thuật viên giữ trung bình 192 phiếu (tối đa 443), phần lớn `DA_DONG` – lý do thêm bộ lọc trạng thái ở M3 (TD-13).

## 5. Kiểm thử trên dữ liệu này

Kết quả các bộ test: README mục 5. Luồng chính chạy end-to-end trên bản sao `smartcrm_work_test` của `smartcrm_test`, đầu vào/đầu ra và ảnh: [tich-hop-end-to-end.md](tich-hop-end-to-end.md).
