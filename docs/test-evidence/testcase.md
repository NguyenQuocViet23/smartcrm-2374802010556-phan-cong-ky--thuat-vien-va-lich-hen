# BÁO CÁO KẾT QUẢ KIỂM THỬ TỰ ĐỘNG

## 1. Thông tin lần chạy
- Thời điểm: 2026-11-06T11:03:04+07:00
- Lệnh chạy: `python -m pytest -m system`
- Commit hash: `e355ff2` (nhánh `main`)
- Hệ điều hành: Windows-11-10.0.26300-SP0
- Python 3.14.2 · pytest 9.1.1 · Playwright 1.64.1
- Trình duyệt: chromium 156.0.8078.4
- UI_BASE_URL: http://localhost:5173 · API_BASE_URL: http://localhost:8000
- CSDL: mỗi test chạy trên `smartcrm_work_test`, tạo lại từ `smartcrm_test` (dữ liệu thật) trước test; backend được khởi động lại trên bản sao đó.
- Số dòng 6 bảng của `smartcrm_test` lúc chạy: service_center 6, technician 38, technician_skill 159, ticket 7.317, ticket_status_log 35.719, appointment 300
- Seed dữ liệu: phiếu MOI seed 20260901; lịch hẹn seed 20261102.

## 2. Tổng hợp
- Tổng số test: 18; PASS: 18; FAIL: 0; bỏ qua: 0; tổng thời gian: 262.0s
- Dòng cuối của pytest: `18 passed in 262.01s`

| Mã | Tên | Loại | Truy vết | Kênh | Kết quả | Thời gian (s) |
|---|---|---|---|---|---|---:|
| TC01 | Gợi ý kỹ thuật viên đúng thứ tự khối lượng công việc | Luồng đúng | US2 · FR2 · AC2.1 · QT-08, A1, A4, A6 | UI React | PASS | 15.77 |
| TC02 | Gợi ý loại bỏ kỹ thuật viên không đủ điều kiện | Ngoại lệ | US2 · FR2 · AC2.2 · QT-08, A6 | UI React | PASS | 16.57 |
| TC03 | Gợi ý trả danh sách rỗng kèm lý do khi không có kỹ thuật viên phù hợp | Ngoại lệ | US2 · FR2 · AC2.3 · QT-08 | UI React | PASS | 14.29 |
| TC04 | Phân công kỹ thuật viên thành công và ghi lịch sử trạng thái | Luồng đúng | US3 · FR3, FR8 · AC3.1 · QT-06, QT-07, QT-08 | UI React | PASS | 14.61 |
| TC05 | Biên: kỹ thuật viên có tay nghề đúng bằng 3 được phân công | Biên | US3 · FR3 · QT-08 | UI React | PASS | 10.23 |
| TC06 | Biên: kỹ thuật viên có tay nghề bằng 2 bị từ chối | Biên | US3 · FR3 · AC3.2 · QT-08 | Swagger | PASS | 14.21 |
| TC07 | Từ chối phân công khi phiếu đã được phân công | Ngoại lệ | US3 · FR3 · AC3.3 · QT-06, QT-07, NFR2 | UI React | PASS | 10.31 |
| TC08 | Đặt lịch hẹn giao/nhận thiết bị hợp lệ | Luồng đúng | US6 · FR6 · AC6.1 · A2, QT-13 | UI React | PASS | 13.65 |
| TC09 | Từ chối đặt lịch hẹn trùng khung giờ | Ngoại lệ | US6 · FR7 · AC6.2 · A3, NFR2 | Swagger | PASS | 16.21 |
| TC10 | Biên: lịch hẹn liền kề (kết thúc = bắt đầu) không bị coi là trùng | Biên | US6 · FR7 · A3 | UI React | PASS | 14.49 |
| TC11 | Từ chối chuyển trạng thái lùi, nhảy bước hoặc giá trị không hợp lệ | Ngoại lệ | US7 · FR8 · QT-06 | Swagger | PASS | 14.98 |
| TC12 | Đổi kỹ thuật viên: bắt buộc có lý do, lý do rỗng bị từ chối | Dữ liệu sai | US4 · FR4 · QT-07 · EX-5.1 | Swagger + UI React | PASS | 15.23 |
| TC13 | Che số điện thoại và phân quyền theo vai trò | Ngoại lệ | US5 · FR5 · QT-14, QT-15 · NFR3 | Swagger + UI React | PASS | 24.87 |
| TC14 | Giao diện M1: trạng thái đang tải | Luồng đúng | US1 · FR1 · yêu cầu 3 trạng thái (Buổi 10) | UI React | PASS | 16.58 |
| TC15 | Giao diện M1: trạng thái rỗng (không có phiếu chờ phân công) | Ngoại lệ | US1 · FR1 · EX-1.1 | UI React | PASS | 10.78 |
| TC16 | Giao diện M1: trạng thái lỗi và nút Thử lại | Ngoại lệ | US1 · FR1 · NFR2 · EX-7b | UI React | PASS | 10.57 |
| TC17 | Giao diện: xử lý 401 (hết phiên) và đăng nhập sai | Ngoại lệ | NFR3 · yêu cầu đăng nhập và 401 (Buổi 10) | UI React | PASS | 12.34 |
| TC18 | End-to-end luồng chính: phân công → đặt lịch hẹn → cập nhật trạng thái đến HOÀN TẤT | Luồng đúng | US1–US7 · FR1–FR8 · UC1–UC7 · NFR4 | UI React | PASS | 16.32 |

## 3. Chi tiết từng test case

### TC01 – Gợi ý kỹ thuật viên đúng thứ tự khối lượng công việc
- Loại: Luồng đúng | Truy vết: US2 · FR2 · AC2.1 · QT-08, A1, A4, A6 | Hàm test: `tests/service/test_suggestion.py::test_tc01_goi_y_dung_thu_tu[chromium]`
- Given: Dữ liệu thật đã nạp. Tự tìm trong dữ liệu một cặp (trung tâm A, nhóm sự cố X) có ≥ 3 kỹ thuật viên đang làm việc với tay nghề ≥ 3. / Tạo 1 phiếu MỚI thuộc trung tâm A, nhóm X (trong giao dịch thử, sẽ rollback). / Trong giao dịch thử: vô hiệu hóa các phiếu đang giữ thật của 3 kỹ thuật viên đó rồi tạo phiếu để khối lượng lần lượt là 5, 2, 8; tắt (is_active = false) các kỹ thuật viên đủ điều kiện còn lại.
- When: Quản lý trung tâm A gọi GET /api/tickets/{ticket_id}/technician-suggestions.
- Then (kỳ vọng): HTTP 200; danh sách đúng 3 kỹ thuật viên theo thứ tự khối lượng 2 → 5 → 8. / Mỗi dòng có technician_code, full_name, proficiency (≥ 3) và workload.
- Dữ liệu thật dùng: Trung tâm TT03, nhóm KHAC, phiếu MỚI TEST-7816 (tạo trên bản sao); KTV KT003, KT022, KT027; 3 KTV đủ điều kiện khác được tắt
- Kết quả thực tế: HTTP 200; gợi ý theo thứ tự KT022 (khối lượng 2) → KT003 (khối lượng 5) → KT027 (khối lượng 8); SQL đếm khối lượng khớp (thời gian chạy 15.77s)
- Trạng thái: PASS
- Ảnh:
  - TC01_goi_y_dung_thu_tu.png | http://localhost:5173/tickets/7816/assign | Smart CRM - Mekong Mobile | 2026-11-06T11:01:26+07:00 | 1280×1090 | tồn tại

### TC02 – Gợi ý loại bỏ kỹ thuật viên không đủ điều kiện
- Loại: Ngoại lệ | Truy vết: US2 · FR2 · AC2.2 · QT-08, A6 | Hàm test: `tests/service/test_suggestion.py::test_tc02_goi_y_loai_ktv_khong_du_dieu_kien[chromium]`
- Given: Cùng kịch bản TC01 (trung tâm A, nhóm X, phiếu MỚI). / Thêm trong giao dịch thử: 1 kỹ thuật viên trung tâm A có tay nghề nhóm X = 2; 1 kỹ thuật viên trung tâm B có tay nghề nhóm X = 5; 1 kỹ thuật viên trung tâm A đủ tay nghề nhưng is_active = false.
- When: Quản lý trung tâm A mở gợi ý cho phiếu.
- Then (kỳ vọng): HTTP 200; cả 3 kỹ thuật viên nói trên KHÔNG xuất hiện trong danh sách. / Danh sách chỉ gồm người cùng trung tâm A, đang làm việc, tay nghề ≥ 3.
- Dữ liệu thật dùng: Trung tâm TT03, nhóm KHAC, phiếu TEST-7816; KTV bị loại: KT019 (tay nghề 2); KT002 (trung tâm khác, tay nghề 5); KT032 (đã nghỉ, tay nghề 4)
- Kết quả thực tế: HTTP 200; danh sách gợi ý KT022, KT003, KT027; không có KT019, KT002, KT032 (thời gian chạy 16.57s)
- Trạng thái: PASS
- Ảnh:
  - TC02_goi_y_loai_ktv_khong_du_dieu_kien.png | http://localhost:5173/tickets/7816/assign | Smart CRM - Mekong Mobile | 2026-11-06T11:01:43+07:00 | 1280×1090 | tồn tại

### TC03 – Gợi ý trả danh sách rỗng kèm lý do khi không có kỹ thuật viên phù hợp
- Loại: Ngoại lệ | Truy vết: US2 · FR2 · AC2.3 · QT-08 | Hàm test: `tests/service/test_suggestion.py::test_tc03_goi_y_rong_khong_co_ktv[chromium]`
- Given: Phiếu MỚI thuộc trung tâm A, nhóm sự cố Y. / Trong giao dịch thử: hạ tay nghề nhóm Y của mọi kỹ thuật viên trung tâm A xuống < 3.
- When: Quản lý trung tâm A mở gợi ý cho phiếu.
- Then (kỳ vọng): HTTP 200 (không phải lỗi); suggestions là danh sách rỗng. / Có trường message nêu rõ lý do (không có người cùng trung tâm đủ tay nghề ≥ 3). / Phiếu vẫn ở trạng thái MOI, không có kỹ thuật viên.
- Dữ liệu thật dùng: Phiếu MỚI thật BH-000001/2025 (trung tâm TT05, nhóm SAC); hạ tay nghề SAC của 4 KTV trung tâm này xuống 2 trên bản sao
- Kết quả thực tế: HTTP 200; suggestions = []; message: "Không có kỹ thuật viên cùng trung tâm đủ tay nghề từ 3 trở lên."; phiếu vẫn MOI, chưa có KTV (thời gian chạy 14.29s)
- Trạng thái: PASS
- Ảnh:
  - TC03_goi_y_rong_khong_co_ktv.png | http://localhost:5173/tickets/1/assign | Smart CRM - Mekong Mobile | 2026-11-06T11:01:57+07:00 | 1280×893 | tồn tại

### TC04 – Phân công kỹ thuật viên thành công và ghi lịch sử trạng thái
- Loại: Luồng đúng | Truy vết: US3 · FR3, FR8 · AC3.1 · QT-06, QT-07, QT-08 | Hàm test: `tests/service/test_assignment.py::test_tc04_phan_cong_thanh_cong[chromium]`
- Given: Phiếu MỚI thuộc trung tâm A, nhóm X, chưa có kỹ thuật viên. / Kỹ thuật viên P đứng đầu danh sách gợi ý (cùng trung tâm, tay nghề ≥ 3, đang làm việc). / Ghi nhận trước số dòng ticket_status_log của phiếu.
- When: Quản lý trung tâm A gọi POST /api/tickets/{ticket_id}/assignment với {"technician_id": P}.
- Then (kỳ vọng): HTTP 201; phản hồi có status = DA_PHAN_CONG, technician_id = P, assigned_by, assigned_at. / Trong CSDL: ticket.status = DA_PHAN_CONG và ticket.technician_id = P. / ticket_status_log tăng đúng 1 dòng: event_type = TRANG_THAI, from_status = MOI, to_status = DA_PHAN_CONG, to_technician_id = P, có changed_by và changed_at.
- Dữ liệu thật dùng: Phiếu MỚI thật BH-000001/2025 (trung tâm TT05, nhóm SAC); KTV đầu danh sách KT026 (khối lượng 20)
- Kết quả thực tế: HTTP 201, status DA_PHAN_CONG, technician_id 26, assigned_by 5; log 1 → 2 dòng (TRANG_THAI, MOI → DA_PHAN_CONG) (thời gian chạy 14.61s)
- Trạng thái: PASS
- Ảnh:
  - TC04_phan_cong_thanh_cong.png | http://localhost:5173/tickets/1/assign | Smart CRM - Mekong Mobile | 2026-11-06T11:00:06+07:00 | 1280×1411 | tồn tại

### TC05 – Biên: kỹ thuật viên có tay nghề đúng bằng 3 được phân công
- Loại: Biên | Truy vết: US3 · FR3 · QT-08 | Hàm test: `tests/service/test_assignment.py::test_tc05_bien_tay_nghe_bang_3[chromium]`
- Given: Phiếu MỚI thuộc trung tâm A, nhóm X. / Kỹ thuật viên Q cùng trung tâm A, đang làm việc, tay nghề nhóm X đặt đúng = 3 (trong giao dịch thử).
- When: Quản lý trung tâm A phân công Q cho phiếu.
- Then (kỳ vọng): HTTP 201; phiếu chuyển sang DA_PHAN_CONG với technician_id = Q (ngưỡng ≥ 3 là ngưỡng đóng, giá trị 3 hợp lệ).
- Dữ liệu thật dùng: Phiếu MỚI thật BH-000001/2025 (trung tâm TT05, nhóm SAC); KTV KT024 cùng trung tâm, đặt proficiency SAC = 3 trên bản sao
- Kết quả thực tế: HTTP 201; phiếu DA_PHAN_CONG, technician_id = 24 (KT024) (thời gian chạy 10.23s)
- Trạng thái: PASS
- Ảnh:
  - TC05_bien_tay_nghe_bang_3.png | http://localhost:5173/tickets/1/assign | Smart CRM - Mekong Mobile | 2026-11-06T11:00:16+07:00 | 1280×1481 | tồn tại

### TC06 – Biên: kỹ thuật viên có tay nghề bằng 2 bị từ chối
- Loại: Biên | Truy vết: US3 · FR3 · AC3.2 · QT-08 | Hàm test: `tests/service/test_assignment.py::test_tc06_bien_tay_nghe_bang_2[chromium]`
- Given: Phiếu MỚI thuộc trung tâm A, nhóm X. / Kỹ thuật viên R cùng trung tâm A, đang làm việc, tay nghề nhóm X = 2. / Ghi nhận trước số dòng ticket_status_log.
- When: Quản lý trung tâm A gửi yêu cầu phân công R cho phiếu.
- Then (kỳ vọng): HTTP 400, mã lỗi TECHNICIAN_NOT_ELIGIBLE, message nêu rõ tay nghề < 3. / Phiếu vẫn status = MOI, technician_id = NULL; ticket_status_log không tăng dòng nào.
- Dữ liệu thật dùng: Phiếu MỚI thật BH-000001/2025 (trung tâm TT05, nhóm SAC); KTV KT007 (id 7) đặt proficiency SAC = 2 trên bản sao
- Kết quả thực tế: HTTP 400 TECHNICIAN_NOT_ELIGIBLE: "Kỹ thuật viên không đủ điều kiện: tay nghề SAC = 2 (< 3) hoặc khác trung tâm/đã nghỉ việc."; phiếu vẫn MOI, technician_id NULL; log giữ 1 dòng (thời gian chạy 14.21s)
- Trạng thái: PASS
- Ảnh:
  - TC06_bien_tay_nghe_bang_2.png | http://localhost:8000/docs#/tickets/assign_ticket_api_tickets__ticket_id__assignment_post | Smart CRM - Swagger UI | 2026-11-06T11:00:30+07:00 | 1224×1378 (khối thao tác Swagger) | tồn tại

### TC07 – Từ chối phân công khi phiếu đã được phân công
- Loại: Ngoại lệ | Truy vết: US3 · FR3 · AC3.3 · QT-06, QT-07, NFR2 | Hàm test: `tests/service/test_assignment.py::test_tc07_phan_cong_phieu_da_co_ktv[chromium]`
- Given: Phiếu đã được phân công cho kỹ thuật viên P (status DA_PHAN_CONG) qua đúng nghiệp vụ. / Kỹ thuật viên Q khác, đủ điều kiện, cùng trung tâm.
- When: Một quản lý khác của cùng trung tâm gọi POST /assignment với technician_id = Q cho cùng phiếu.
- Then (kỳ vọng): HTTP 409, mã lỗi TICKET_ALREADY_ASSIGNED, message có mã kỹ thuật viên hiện tại (P). / Phiếu vẫn technician_id = P; ticket_status_log không tăng thêm dòng.
- Dữ liệu thật dùng: Phiếu MỚI thật BH-000001/2025 (trung tâm TT05, nhóm SAC); phiên 2 phân công KT026, phiên 1 thử phân công KT017
- Kết quả thực tế: Phiên 2: HTTP 201. Phiên 1: HTTP 409 TICKET_ALREADY_ASSIGNED: "Phiếu đã được phân công cho kỹ thuật viên KT026."; phiếu vẫn thuộc KT026; log không tăng thêm (thời gian chạy 10.31s)
- Trạng thái: PASS
- Ảnh:
  - TC07_phan_cong_phieu_da_co_ktv.png | http://localhost:5173/tickets/1/assign | Smart CRM - Mekong Mobile | 2026-11-06T11:00:40+07:00 | 1280×1294 | tồn tại

### TC08 – Đặt lịch hẹn giao/nhận thiết bị hợp lệ
- Loại: Luồng đúng | Truy vết: US6 · FR6 · AC6.1 · A2, QT-13 | Hàm test: `tests/service/test_appointment.py::test_tc08_dat_lich_hop_le[chromium]`
- Given: Phiếu đã gán kỹ thuật viên K (DA_PHAN_CONG); K chưa có lịch nào vào ngày làm việc D (Thứ Hai–Thứ Bảy, cách hôm nay ≥ 30 ngày để không đụng lịch hẹn mẫu).
- When: Kỹ thuật viên K (hoặc Quản lý) gọi POST /api/appointments với appointment_type = NHAN, 09:00–09:30 ngày D.
- Then (kỳ vọng): HTTP 201; phản hồi có status = DA_HEN, technician_id = K, appointment_type = NHAN, start_at/end_at đúng khung 09:00–09:30. / Lịch hẹn xuất hiện trong danh sách lịch hẹn của phiếu và của K.
- Dữ liệu thật dùng: KTV KT008, phiếu thật BH-000009/2026 (DA_PHAN_CONG); ngày D = 07/12/2026, K chưa có lịch ngày D
- Kết quả thực tế: HTTP 201, appointment_id 301, status DA_HEN, NHAN, 09:00–09:30 ngày 07/12/2026; có trong lịch hẹn của phiếu và của KT008 (thời gian chạy 13.65s)
- Trạng thái: PASS
- Ảnh:
  - TC08_dat_lich_hop_le.png | http://localhost:5173/my-tickets | Smart CRM - Mekong Mobile | 2026-11-06T10:59:20+07:00 | 1280×2357 | tồn tại

### TC09 – Từ chối đặt lịch hẹn trùng khung giờ
- Loại: Ngoại lệ | Truy vết: US6 · FR7 · AC6.2 · A3, NFR2 | Hàm test: `tests/service/test_appointment.py::test_tc09_dat_lich_trung[chromium]`
- Given: Kỹ thuật viên K đã có lịch hẹn DA_HEN 09:00–09:30 vào ngày làm việc D (Thứ Hai–Thứ Bảy, cách hôm nay ≥ 30 ngày để không đụng lịch hẹn mẫu). / Ghi nhận trước số dòng bảng appointment.
- When: Đặt thêm lịch hẹn cho K khung 09:15–09:45 cùng ngày.
- Then (kỳ vọng): HTTP 409, mã lỗi APPOINTMENT_OVERLAP. / Trường conflicts liệt kê lịch bị trùng (appointment_id, ticket_code, start_at, end_at). / Số dòng bảng appointment không đổi (không lưu lịch mới).
- Dữ liệu thật dùng: KTV KT008, phiếu thật BH-000009/2026; ngày D = 07/12/2026; lịch có sẵn #301 09:00–09:30
- Kết quả thực tế: HTTP 409 APPOINTMENT_OVERLAP; conflicts: #301 BH-000009/2026 09:00–09:30; bảng appointment giữ 301 dòng (thời gian chạy 16.21s)
- Trạng thái: PASS
- Ảnh:
  - TC09_dat_lich_trung.png | http://localhost:8000/docs#/appointments/create_appointment_api_appointments_post | Smart CRM - Swagger UI | 2026-11-06T10:59:37+07:00 | 1224×1564 (khối thao tác Swagger) | tồn tại

### TC10 – Biên: lịch hẹn liền kề (kết thúc = bắt đầu) không bị coi là trùng
- Loại: Biên | Truy vết: US6 · FR7 · A3 | Hàm test: `tests/service/test_appointment.py::test_tc10_bien_lich_lien_ke[chromium]`
- Given: Kỹ thuật viên K đã có lịch DA_HEN 09:00–09:30 vào ngày làm việc D (Thứ Hai–Thứ Bảy, cách hôm nay ≥ 30 ngày để không đụng lịch hẹn mẫu).
- When: Đặt thêm lịch hẹn cho K khung 09:30–10:00 cùng ngày.
- Then (kỳ vọng): HTTP 201; lịch mới được lưu (khoảng nửa mở [start, end) nên không giao nhau). / K có đúng 2 lịch DA_HEN trong ngày D; ràng buộc EXCLUDE của CSDL không báo lỗi.
- Dữ liệu thật dùng: KTV KT008, phiếu thật BH-000009/2026; ngày D = 07/12/2026; lịch có sẵn #301 09:00–09:30
- Kết quả thực tế: HTTP 201 cho lịch 09:30–10:00; K có đúng 2 lịch DA_HEN ngày D (09:00–09:30, 09:30–10:00); ràng buộc EXCLUDE không báo lỗi (thời gian chạy 14.49s)
- Trạng thái: PASS
- Ảnh:
  - TC10_bien_lich_lien_ke.png | http://localhost:5173/my-tickets | Smart CRM - Mekong Mobile | 2026-11-06T10:59:51+07:00 | 1280×2403 | tồn tại

### TC11 – Từ chối chuyển trạng thái lùi, nhảy bước hoặc giá trị không hợp lệ
- Loại: Ngoại lệ | Truy vết: US7 · FR8 · QT-06 | Hàm test: `tests/service/test_status.py::test_tc11_chuyen_trang_thai_lui[chromium]`
- Given: Kỹ thuật viên K có phiếu T1 ở trạng thái HOAN_TAT và phiếu T2 ở trạng thái DA_PHAN_CONG. / Ghi nhận trước số dòng ticket_status_log của T1, T2.
- When: (a) K gọi PATCH /api/tickets/{T1}/status với to_status = DANG_XU_LY (lùi). / (b) K gọi PATCH /api/tickets/{T2}/status với to_status = HOAN_TAT (nhảy bước). / (c) K gọi PATCH /api/tickets/{T2}/status với to_status = "ABC".
- Then (kỳ vọng): (a) và (b): HTTP 409; trạng thái phiếu giữ nguyên; log không tăng. / (c): HTTP 400 (giá trị trạng thái không hợp lệ); T2 vẫn DA_PHAN_CONG.
- Dữ liệu thật dùng: KTV KT002; T1 = BH-000788/2024 (HOAN_TAT), T2 = BH-000622/2025 (DA_PHAN_CONG)
- Kết quả thực tế: (a) HTTP 409 "Không thể chuyển từ HOAN_TAT sang DANG_XU_LY."; (b) HTTP 409 "Không thể chuyển từ DA_PHAN_CONG sang HOAN_TAT."; (c) HTTP 400 INVALID_STATUS; T1 vẫn HOAN_TAT, T2 vẫn DA_PHAN_CONG; log không đổi (thời gian chạy 14.98s)
- Trạng thái: PASS
- Ảnh:
  - TC11_chuyen_trang_thai_lui.png | http://localhost:8000/docs#/tickets/update_ticket_status_api_tickets__ticket_id__status_patch | Smart CRM - Swagger UI | 2026-11-06T11:01:10+07:00 | 1224×1378 (khối thao tác Swagger) | tồn tại
  - TC11_chuyen_trang_thai_lui_b.png | http://localhost:8000/docs#/tickets/update_ticket_status_api_tickets__ticket_id__status_patch | Smart CRM - Swagger UI | 2026-11-06T11:01:10+07:00 | 1224×1386 (khối thao tác Swagger) | tồn tại
  - TC11_chuyen_trang_thai_lui_c.png | http://localhost:8000/docs#/tickets/update_ticket_status_api_tickets__ticket_id__status_patch | Smart CRM - Swagger UI | 2026-11-06T11:01:11+07:00 | 1224×1386 (khối thao tác Swagger) | tồn tại

### TC12 – Đổi kỹ thuật viên: bắt buộc có lý do, lý do rỗng bị từ chối
- Loại: Dữ liệu sai | Truy vết: US4 · FR4 · QT-07 · EX-5.1 | Hàm test: `tests/service/test_assignment.py::test_tc12_doi_ktv_thieu_ly_do[chromium]`
- Given: Phiếu DA_PHAN_CONG đang gán cho kỹ thuật viên K1; kỹ thuật viên K2 đủ điều kiện cùng trung tâm. / Ghi nhận trước số dòng ticket_status_log.
- When: (a) Quản lý gọi PUT /api/tickets/{id}/assignment với technician_id = K2, reason = "". / (b) Như (a) nhưng reason = "   " (chỉ khoảng trắng). / (c) Như (a) nhưng reason = "Kỹ thuật viên cũ nghỉ phép".
- Then (kỳ vọng): (a) và (b): HTTP 400; phiếu vẫn thuộc K1; log không tăng. / (c): HTTP 200; phiếu chuyển sang K2, trạng thái phiếu không lùi; log tăng đúng 1 dòng event_type = DOI_KTV, from_technician_id = K1, to_technician_id = K2, note = lý do.
- Dữ liệu thật dùng: Phiếu thật BH-000009/2026 (trung tâm TT02, nhóm SAC) đang thuộc KT008; K2 = KT012
- Kết quả thực tế: (a) reason "": HTTP 400 REASON_REQUIRED; (b) reason "   ": HTTP 400 REASON_REQUIRED; (c) lý do hợp lệ: HTTP 200, phiếu chuyển sang KT012, vẫn DA_PHAN_CONG; log thêm 1 dòng DOI_KTV KT008 → KT012 (thời gian chạy 15.23s)
- Trạng thái: PASS
- Ảnh:
  - TC12_doi_ktv_thieu_ly_do_a.png | http://localhost:8000/docs#/tickets/change_assignment_api_tickets__ticket_id__assignment_put | Smart CRM - Swagger UI | 2026-11-06T11:00:54+07:00 | 1224×1392 (khối thao tác Swagger) | tồn tại
  - TC12_doi_ktv_thieu_ly_do.png | http://localhost:5173/tickets/9/assign | Smart CRM - Mekong Mobile | 2026-11-06T11:00:56+07:00 | 1280×1653 | tồn tại

### TC13 – Che số điện thoại và phân quyền theo vai trò
- Loại: Ngoại lệ | Truy vết: US5 · FR5 · QT-14, QT-15 · NFR3 | Hàm test: `tests/service/test_access.py::test_tc13_che_so_dien_thoai_va_phan_quyen[chromium]`
- Given: Phiếu T1 gán cho kỹ thuật viên K, khách có số điện thoại 10 chữ số; phiếu T2 gán cho kỹ thuật viên K' khác. / Có Quản lý trung tâm của trung tâm chứa T1.
- When: (a) K gọi GET /api/technicians/me/tickets. / (b) Quản lý gọi GET /api/tickets/{T1} (hoặc danh sách phiếu). / (c) K gọi GET /api/tickets/{T2}.
- Then (kỳ vọng): (a) Số điện thoại dạng che 3 số đầu + **** + 3 số cuối (ví dụ 090****456); 0 phiếu của người khác trong phản hồi. / (b) Số điện thoại hiển thị đầy đủ cho Quản lý. / (c) HTTP 403.
- Dữ liệu thật dùng: T1 = BH-000002/2025 của KTV KT005 (SĐT khách 0334058225); T2 = BH-000003/2026 của KT013; Quản lý QL_TT02
- Kết quả thực tế: (a) 211 phiếu, tất cả của KT005, SĐT dạng che (T1: 033****225); (b) Quản lý thấy 0334058225; (c) HTTP 403 "Bạn không phải kỹ thuật viên phụ trách phiếu này" (thời gian chạy 24.87s)
- Trạng thái: PASS
- Ảnh:
  - TC13_che_so_dien_thoai_va_phan_quyen.png | http://localhost:5173/my-tickets | Smart CRM - Mekong Mobile | 2026-11-06T10:58:56+07:00 | 1280×1995 | tồn tại
  - TC13_che_so_dien_thoai_va_phan_quyen_c.png | http://localhost:8000/docs#/tickets/get_ticket_api_tickets__ticket_id__get | Smart CRM - Swagger UI | 2026-11-06T10:59:02+07:00 | 1224×895 (khối thao tác Swagger) | tồn tại
  - TC13_che_so_dien_thoai_va_phan_quyen_b.png | http://localhost:5173/tickets/2/assign | Smart CRM - Mekong Mobile | 2026-11-06T10:59:07+07:00 | 1280×1364 | tồn tại

### TC14 – Giao diện M1: trạng thái đang tải
- Loại: Luồng đúng | Truy vết: US1 · FR1 · yêu cầu 3 trạng thái (Buổi 10) | Hàm test: `tests/ui/test_states.py::test_tc14_ui_trang_thai_dang_tai[chromium]`
- Given: Đăng nhập bằng Quản lý của trung tâm có phiếu MỚI (dữ liệu thật). / Playwright làm chậm phản hồi GET /api/tickets 3 giây.
- When: Mở màn hình M1 – Phiếu chờ phân công.
- Then (kỳ vọng): Trong lúc chờ thấy vùng [data-testid=state-loading] với chữ "Đang tải dữ liệu…"; chụp ảnh đúng lúc này. / Sau khi dữ liệu về: vùng đang tải biến mất, bảng hiển thị ≥ 1 dòng phiếu thật.
- Dữ liệu thật dùng: Quản lý QL_TT01 (5 phiếu MOI thật); GET /api/tickets bị giữ 3.0s
- Kết quả thực tế: Trong lúc chờ: "Đang tải dữ liệu…", chưa có bảng; sau 3.0s bảng hiện 5 phiếu, dòng đầu BH-005310/2025 (thời gian chạy 16.58s)
- Trạng thái: PASS
- Ảnh:
  - TC14_ui_trang_thai_dang_tai.png | http://localhost:5173/tickets | Smart CRM - Mekong Mobile | 2026-11-06T11:02:23+07:00 | 1280×720 | tồn tại

### TC15 – Giao diện M1: trạng thái rỗng (không có phiếu chờ phân công)
- Loại: Ngoại lệ | Truy vết: US1 · FR1 · EX-1.1 | Hàm test: `tests/ui/test_states.py::test_tc15_ui_trang_thai_rong[chromium]`
- Given: Đăng nhập bằng Quản lý của trung tâm không có phiếu MỚI nào (script nạp dữ liệu cố ý chừa 1 trung tâm).
- When: Mở màn hình M1.
- Then (kỳ vọng): Hiển thị vùng [data-testid=state-empty] với chữ "Không có phiếu chờ phân công". / Không có vùng lỗi [data-testid=state-error]; không hiển thị thông báo đỏ.
- Dữ liệu thật dùng: Quản lý QL_TT06; trên bản sao đã xoá 5 phiếu MOI của trung tâm này (BH-004381/2024, BH-004873/2024, BH-005905/2025, BH-006447/2026, BH-007629/2025); SQL đếm MOI = 0
- Kết quả thực tế: M1 hiện "Không có phiếu chờ phân công"; không có vùng lỗi, không có dải đỏ (thời gian chạy 10.78s)
- Trạng thái: PASS
- Ảnh:
  - TC15_ui_trang_thai_rong.png | http://localhost:5173/tickets | Smart CRM - Mekong Mobile | 2026-11-06T11:02:41+07:00 | 1280×720 | tồn tại

### TC16 – Giao diện M1: trạng thái lỗi và nút Thử lại
- Loại: Ngoại lệ | Truy vết: US1 · FR1 · NFR2 · EX-7b | Hàm test: `tests/ui/test_states.py::test_tc16_ui_trang_thai_loi[chromium]`
- Given: Đăng nhập Quản lý của trung tâm có phiếu MỚI. / Playwright chặn (abort) GET /api/tickets để mô phỏng backend không phản hồi.
- When: Mở M1; sau đó bỏ chặn và bấm nút "Thử lại".
- Then (kỳ vọng): Hiển thị vùng [data-testid=state-error] có thông báo lỗi dễ hiểu và nút "Thử lại" ([data-testid=retry-button]); chụp ảnh 1. / Sau khi bỏ chặn và bấm Thử lại: bảng phiếu thật hiển thị; chụp ảnh 2.
- Dữ liệu thật dùng: Quản lý QL_TT01 (5 phiếu MOI thật); GET /api/tickets bị chặn (abort) rồi bỏ chặn
- Kết quả thực tế: Lần 1: "Không thể kết nối máy chủ. Vui lòng thử lại." + nút Thử lại; sau khi bấm Thử lại: bảng hiện 5 phiếu thật, dải lỗi biến mất (thời gian chạy 10.57s)
- Trạng thái: PASS
- Ảnh:
  - TC16_ui_trang_thai_loi_1_loi.png | http://localhost:5173/tickets | Smart CRM - Mekong Mobile | 2026-11-06T11:02:51+07:00 | 1280×720 | tồn tại
  - TC16_ui_trang_thai_loi_2_thu_lai.png | http://localhost:5173/tickets | Smart CRM - Mekong Mobile | 2026-11-06T11:02:52+07:00 | 1280×720 | tồn tại

### TC17 – Giao diện: xử lý 401 (hết phiên) và đăng nhập sai
- Loại: Ngoại lệ | Truy vết: NFR3 · yêu cầu đăng nhập và 401 (Buổi 10) | Hàm test: `tests/ui/test_states.py::test_tc17_ui_het_phien_dang_nhap_401[chromium]`
- Given: Đang đăng nhập (có token trong trình duyệt). / Playwright cho GET /api/tickets trả HTTP 401.
- When: (a) Mở M1 khi API trả 401. / (b) Tại trang đăng nhập, nhập sai mật khẩu.
- Then (kỳ vọng): (a) Token bị xóa khỏi bộ nhớ trình duyệt và giao diện chuyển về trang đăng nhập; chụp ảnh 1. / (b) Trang đăng nhập hiển thị thông báo lỗi "Sai tên đăng nhập hoặc mật khẩu", không bị lặp chuyển trang; chụp ảnh 2.
- Dữ liệu thật dùng: Quản lý QL_TT01; GET /api/tickets trả 401 (page.route); mật khẩu sai "mat-khau-sai"
- Kết quả thực tế: (a) về /login, access_token = null; (b) thông báo "Sai tên đăng nhập hoặc mật khẩu", không có điều hướng nào trong 1,5 giây (thời gian chạy 12.34s)
- Trạng thái: PASS
- Ảnh:
  - TC17_ui_het_phien_dang_nhap_401_1_ve_dang_nhap.png | http://localhost:5173/login | Smart CRM - Mekong Mobile | 2026-11-06T11:03:02+07:00 | 1280×720 | tồn tại
  - TC17_ui_het_phien_dang_nhap_401_2_sai_mat_khau.png | http://localhost:5173/login | Smart CRM - Mekong Mobile | 2026-11-06T11:03:04+07:00 | 1280×720 | tồn tại

### TC18 – End-to-end luồng chính: phân công → đặt lịch hẹn → cập nhật trạng thái đến HOÀN TẤT
- Loại: Luồng đúng | Truy vết: US1–US7 · FR1–FR8 · UC1–UC7 · NFR4 | Hàm test: `tests/ui/test_e2e_main_flow.py::test_tc18_ui_e2e_luong_chinh[chromium]`
- Given: Dữ liệu thật đã nạp; đã chạy bước tạo phiếu MỚI; có Quản lý và kỹ thuật viên phù hợp (tài khoản trong data/processed/demo_accounts.json).
- When: b1: Quản lý đăng nhập, mở M1. / b2: Bấm "Phân công" ở dòng phiếu đầu tiên, mở M2 và xem danh sách gợi ý. / b3: Chọn kỹ thuật viên đầu danh sách, bấm "Xác nhận phân công". / b4: Bấm "Đặt lịch hẹn", chọn loại, ngày D, 09:00–09:30, bấm "Lưu lịch hẹn". / b5: Đăng xuất, đăng nhập bằng kỹ thuật viên vừa được phân công, mở M3. / b6: Chọn phiếu, bấm "Bắt đầu sửa". / b7: Bấm "Hoàn tất".
- Then (kỳ vọng): b1: M1 chỉ có phiếu MỚI của trung tâm, sắp CAO → TRUNG_BINH → THAP. / b2: M2 hiển thị thông tin phiếu và bảng gợi ý (tay nghề ≥ 3, khối lượng tăng dần). / b3: Thông báo thành công; trạng thái phiếu ĐÃ PHÂN CÔNG; bảng lịch sử thêm 1 dòng. / b4: Lịch hẹn lưu thành công, hiển thị với trạng thái ĐÃ HẸN. / b5: M3 của kỹ thuật viên có phiếu vừa nhận, số điện thoại dạng che. / b6: Trạng thái ĐANG XỬ LÝ. b7: Trạng thái HOÀN TẤT. / Kiểm CSDL cuối luồng: ticket.status = HOAN_TAT; ticket_status_log có đủ MOI → DA_PHAN_CONG → DANG_XU_LY → HOAN_TAT; có 1 lịch hẹn DA_HEN.
- Dữ liệu thật dùng: Quản lý QL_TT01; phiếu MỚI thật BH-005310/2025; KTV đầu danh sách KT033 (khối lượng 60); lịch GIAO 09:00–09:30 ngày 07/12/2026
- Kết quả thực tế: b1 5 phiếu MOI đúng thứ tự; b2 2 gợi ý, khối lượng [60, 76]; b3 HTTP 201, lịch sử +1 dòng; b4 HTTP 201, ĐÃ HẸN; b5 SĐT dạng che; b6 ĐANG XỬ LÝ; b7 HOÀN TẤT; CSDL: HOAN_TAT, log MOI → DA_PHAN_CONG → DANG_XU_LY → HOAN_TAT, 1 lịch DA_HEN (thời gian chạy 16.32s)
- Trạng thái: PASS
- Ảnh:
  - TC18_ui_e2e_luong_chinh_b1_danh_sach_M1.png | http://localhost:5173/tickets | Smart CRM - Mekong Mobile | 2026-11-06T11:02:11+07:00 | 1280×720 | tồn tại
  - TC18_ui_e2e_luong_chinh_b2_goi_y_M2.png | http://localhost:5173/tickets/5310/assign | Smart CRM - Mekong Mobile | 2026-11-06T11:02:11+07:00 | 1280×1020 | tồn tại
  - TC18_ui_e2e_luong_chinh_b3_phan_cong_xong.png | http://localhost:5173/tickets/5310/assign | Smart CRM - Mekong Mobile | 2026-11-06T11:02:11+07:00 | 1280×1271 | tồn tại
  - TC18_ui_e2e_luong_chinh_b4_dat_lich_xong.png | http://localhost:5173/tickets/5310/assign | Smart CRM - Mekong Mobile | 2026-11-06T11:02:12+07:00 | 1280×1467 | tồn tại
  - TC18_ui_e2e_luong_chinh_b5_phieu_cua_toi_M3.png | http://localhost:5173/my-tickets | Smart CRM - Mekong Mobile | 2026-11-06T11:02:13+07:00 | 1280×3145 | tồn tại
  - TC18_ui_e2e_luong_chinh_b6_dang_xu_ly.png | http://localhost:5173/my-tickets | Smart CRM - Mekong Mobile | 2026-11-06T11:02:13+07:00 | 1280×3706 | tồn tại
  - TC18_ui_e2e_luong_chinh_b7_hoan_tat.png | http://localhost:5173/my-tickets | Smart CRM - Mekong Mobile | 2026-11-06T11:02:13+07:00 | 1280×1687 | tồn tại

## 4. Danh sách ảnh trong docs/test-evidence/
- TC01_goi_y_dung_thu_tu.png (55.842 bytes)
- TC02_goi_y_loai_ktv_khong_du_dieu_kien.png (56.058 bytes)
- TC03_goi_y_rong_khong_co_ktv.png (49.904 bytes)
- TC04_phan_cong_thanh_cong.png (75.171 bytes)
- TC05_bien_tay_nghe_bang_3.png (78.468 bytes)
- TC06_bien_tay_nghe_bang_2.png (63.205 bytes)
- TC07_phan_cong_phieu_da_co_ktv.png (68.352 bytes)
- TC08_dat_lich_hop_le.png (231.738 bytes)
- TC09_dat_lich_trung.png (81.995 bytes)
- TC10_bien_lich_lien_ke.png (234.493 bytes)
- TC11_chuyen_trang_thai_lui.png (62.750 bytes)
- TC11_chuyen_trang_thai_lui_b.png (62.356 bytes)
- TC11_chuyen_trang_thai_lui_c.png (61.098 bytes)
- TC12_doi_ktv_thieu_ly_do.png (88.879 bytes)
- TC12_doi_ktv_thieu_ly_do_a.png (62.462 bytes)
- TC13_che_so_dien_thoai_va_phan_quyen.png (221.672 bytes)
- TC13_che_so_dien_thoai_va_phan_quyen_b.png (75.366 bytes)
- TC13_che_so_dien_thoai_va_phan_quyen_c.png (46.338 bytes)
- TC14_ui_trang_thai_dang_tai.png (16.648 bytes)
- TC15_ui_trang_thai_rong.png (17.497 bytes)
- TC16_ui_trang_thai_loi_1_loi.png (18.565 bytes)
- TC16_ui_trang_thai_loi_2_thu_lai.png (51.613 bytes)
- TC17_ui_het_phien_dang_nhap_401_1_ve_dang_nhap.png (14.469 bytes)
- TC17_ui_het_phien_dang_nhap_401_2_sai_mat_khau.png (17.874 bytes)
- TC18_ui_e2e_luong_chinh_b1_danh_sach_M1.png (51.613 bytes)
- TC18_ui_e2e_luong_chinh_b2_goi_y_M2.png (53.793 bytes)
- TC18_ui_e2e_luong_chinh_b3_phan_cong_xong.png (68.199 bytes)
- TC18_ui_e2e_luong_chinh_b4_dat_lich_xong.png (75.985 bytes)
- TC18_ui_e2e_luong_chinh_b5_phieu_cua_toi_M3.png (366.060 bytes)
- TC18_ui_e2e_luong_chinh_b6_dang_xu_ly.png (396.850 bytes)
- TC18_ui_e2e_luong_chinh_b7_hoan_tat.png (128.216 bytes)

## 5. Cảnh báo và điểm bất thường
- Không có.

## 6. Cách chạy lại
1. PostgreSQL có `smartcrm_test` đã nạp dữ liệu thật (README mục 3).
2. Chạy frontend: `cd src/frontend` rồi `npm run dev`; để trống cổng 8000 (test tự chạy backend).
3. Windows PowerShell: `$env:TEST_DB_NAME = "smartcrm_test"` rồi `python -m pytest -m system`.
4. Thêm `--headed --slowmo 300` để xem trình duyệt chạy.
