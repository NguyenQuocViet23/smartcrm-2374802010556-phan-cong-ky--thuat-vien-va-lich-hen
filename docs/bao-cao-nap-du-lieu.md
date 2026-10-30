# Báo cáo khảo sát/nạp dữ liệu thật

## Kết quả

**Trạng thái: CHƯA NẠP VÀO CSDL.** PostgreSQL không khả dụng trong phiên kiểm tra; lệnh seed mặc định được kiểm tra ở bước preflight và dừng vì thiếu nguồn bắt buộc. Không chạy `--allow-incomplete`, không ghi dữ liệu vào database và không tạo tài khoản demo.

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

## Điều kiện để hoàn tất

1. Cung cấp `ticket_status_log.csv` và bộ tạo lịch hẹn đã được xác minh hoặc `appointments.csv` sinh với seed `20261023`.
2. Khởi động PostgreSQL, tạo `smartcrm` và `smartcrm_test`, áp dụng migration.
3. Hoàn thiện/kiểm chứng mapping log và lịch hẹn trên header thật, chạy seed hai lần và đối chiếu số dòng.
4. Tạo MOI, tài khoản demo, reject files và báo cáo sau lần nạp thành công; sau đó mới chạy các test phụ thuộc DB.
