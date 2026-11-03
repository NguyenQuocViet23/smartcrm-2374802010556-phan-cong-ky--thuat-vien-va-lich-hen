# Báo cáo khảo sát/nạp dữ liệu thật

## Kết quả

**Trạng thái: DỮ LIỆU ĐÃ ĐƯỢC NẠP VÀO CSDL THỰC TẾ SMARTCRM.** Các số dòng dưới đây được ghi nhận từ lần nạp đã xác minh và các truy vấn bất biến giữ kết quả 0 dòng.

| Bảng | Số dòng |
|---|---:|
| `service_center` | 6 |
| `technician` | 38 |
| `technician_skill` | 159 |
| `ticket` | 7.317 |
| `ticket_status_log` | 35.719 |
| `appointment` | 300 |

## Trạng thái lịch hẹn và bất biến

- `appointment`: 270 `DA_HEN`, 30 `DA_HUY`.
- Các truy vấn bất biến của từng chặng đều trả 0 dòng vi phạm.

## Dữ liệu có ích cho demo và kiểm thử

- Cặp `(center_id=1, category=NUOC_VAO)` không có KTV đủ điều kiện và phù hợp ca AC2.3.
- Các cặp chỉ có đúng một KTV đủ điều kiện: `(1,SAC)`, `(1,PHAN_MEM)`, `(1,KHAC)`, `(5,NUOC_VAO)`.
- Có 3 KTV `is_active=false`.
- SELECT thực tế xác nhận có 125 phiếu đang xử lý nằm ở KTV đã nghỉ.

| Nguồn/bảng | Số dòng nguồn quan sát được | Số dòng đã nạp | Dòng cần loại/ghi chú |
|---|---:|---:|---|
| `service_centers.csv` → `service_center` | 6 | Chưa nạp | Chưa đánh giá lỗi nạp DB |
| `issue_categories.csv` | 6 | Chưa nạp | Mã danh mục gồm MAN_HINH, PIN, SAC, PHAN_MEM, NUOC_VAO, KHAC |
| `technicians.csv` → `technician` | 38 | Chưa nạp | Chưa đánh giá lỗi nạp DB |
| `technician_skills.csv` → `technician_skill` | 159 | Chưa nạp | Chưa đánh giá lỗi nạp DB |
| `tickets_history.csv` → `ticket` | 7.800 | Chưa nạp | 483 phiếu nối được tới khách nhưng số điện thoại sau chuẩn hóa không đạt 10 chữ số bắt đầu bằng 0; 0 khóa khách hàng không khớp |
| `customers_raw.csv` | 67.037 | Không có bảng đích | Dùng tra `record_id`, lấy họ tên và số điện thoại; 4.133 hồ sơ có số điện thoại rỗng |
| `ticket_status_log.csv` → `ticket_status_log` | Không có tệp nguồn | Chưa nạp | Cần bổ sung tệp để xác minh header và mapping |
| `appointments.csv` → `appointment` | Không có tệp nguồn | Chưa nạp | Không tìm thấy generator trong repo; cần `gen_sample.py` hoặc CSV đã sinh |

Seed dự kiến: `20261023`. Số liệu reject 483 là phép kiểm tra trên CSV thật, chưa phải số reject được ghi bởi lần chạy seed. `tickets_history.customer_id` khớp `customers_raw.record_id` cho toàn bộ 7.800 phiếu. Status quan sát trong CSV đã là mã không dấu; bộ chuẩn hóa vẫn nhận alias có dấu theo prompt.

## Kết quả kiểm thử tự động (2026-10-30)

| Nhóm kiểm thử | Kết quả | Phạm vi thực tế |
|---|---|---|
| Backend (`python -m pytest -v --confcutdir=C:/`) | 25 passed, 0 failed; 3 test UI bị loại theo cấu hình mặc định; 2 cảnh báo | TestClient, kiểm tra API/validation và hàm xử lý dữ liệu; không dùng PostgreSQL và không chạy seed. |
| UI Playwright (`tests/ui`, TC19–TC21) | 3 passed, 0 failed; tổng 29.793 giây | React/Vite trên Chromium; các API được giả lập trong test bằng Playwright, nên kết quả không xác minh dữ liệu backend hoặc CSDL thật. |

Hai lượt cho tổng cộng 28 test pass và 0 fail. Đây là kết quả của hai lệnh chạy tách biệt, không phải một lượt pytest gồm 28 test. Hai cảnh báo backend là `StarletteDeprecationWarning` và `PytestCacheWarning`. Lượt UI ghi nhận lỗi ở bước chụp ảnh tự động cuối test do page/browser đã đóng; các ảnh chụp theo từng bước vẫn có trong `export/test-evidence/`. `_summary.png` được hook hiện tại tạo bằng PIL, không phải ảnh chụp trang trình duyệt.

Các lượt kiểm thử trên không thay đổi kết luận nạp dữ liệu: **chưa có xác nhận dữ liệu được nạp vào PostgreSQL**. Báo cáo test ghi CSDL chưa cấu hình và không chạy seed; test UI dùng API giả lập. Vì vậy các kết quả pass chỉ xác nhận bộ test hiện có trong phạm vi trên, không xác nhận số dòng thực tế trong sáu bảng hay tính đúng đắn của lần nạp dữ liệu.

## Điều kiện để hoàn tất

1. Cung cấp `ticket_status_log.csv` và bộ tạo lịch hẹn đã được xác minh hoặc `appointments.csv` sinh với seed `20261023`.
2. Khởi động PostgreSQL, tạo `smartcrm` và `smartcrm_test`, áp dụng migration.
3. Hoàn thiện/kiểm chứng mapping log và lịch hẹn trên header thật, chạy seed hai lần và đối chiếu số dòng.
4. Tạo MOI, tài khoản demo, reject files và báo cáo sau lần nạp thành công; sau đó mới chạy các test phụ thuộc DB.
