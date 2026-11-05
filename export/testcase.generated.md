# BÁO CÁO KẾT QUẢ KIỂM THỬ TỰ ĐỘNG

## 1. Thông tin lần chạy
- Thời điểm chạy: 2026-11-05T13:37:10+07:00
- Lệnh chạy: `python -m pytest -v`
- Commit hash: `ca0d51e`
- Nhánh Git: `main`
- Python: `3.14.2`
- pytest: `9.1.1`
- Playwright: `không xác định hoặc chưa cài playwright-python`
- Hệ điều hành: `Windows-11-10.0.26300-SP0`
- CSDL dùng: Chưa cấu hình
- Số dòng từng bảng: chưa truy vấn được (không cần PostgreSQL cho bộ test hiện tại)
- Seed dữ liệu đang dùng: không chạy seed trong lần kiểm thử hiện tại.

## 2. Tổng hợp
- Tổng số test: 4; PASS: 4; FAIL: 0; bỏ qua: 0; tổng thời gian: 2.182s.

| Mã | Tên | Loại | Nhóm | Kết quả | Thời gian (s) |
|---|---|---|---|---|---:|
| TC22 | TC22: gợi ý rỗng cho cặp trung tâm - nhóm sự cố. | Chưa được khai báo trong test. | service | PASS | 0.460 |
| TC23 | TC23: chỉ một KTV đủ điều kiện và thứ tự gợi ý đúng. | Chưa được khai báo trong test. | service | PASS | 0.510 |
| TC24 | TC24: phân công thành công, đúng log, và từ chối KTV không đủ điều kiện. | Chưa được khai báo trong test. | service | PASS | 0.629 |
| TC25 | TC25: lịch liền kề, trùng, DA_HUY và trạng thái phiếu bị chặn. | Chưa được khai báo trong test. | service | PASS | 0.582 |

## 3. Chi tiết từng test case

### TC22 - TC22: gợi ý rỗng cho cặp trung tâm - nhóm sự cố.
- Hàm test: `tests/integration/test_tc22_tc25.py::test_empty_suggestion`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.460s
- Ảnh:
  - `export/test-evidence/run-20261105-133708/TC22_tc22_g_i_r_ng_cho_c_p_trung_t_m_nh_m_s_c.png` — tồn tại

### TC23 - TC23: chỉ một KTV đủ điều kiện và thứ tự gợi ý đúng.
- Hàm test: `tests/integration/test_tc22_tc25.py::test_single_eligible_technician_order`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.510s
- Ảnh:
  - `export/test-evidence/run-20261105-133708/TC23_tc23_ch_m_t_ktv_i_u_ki_n_v_th_t_g_i_ng.png` — tồn tại

### TC24 - TC24: phân công thành công, đúng log, và từ chối KTV không đủ điều kiện.
- Hàm test: `tests/integration/test_tc22_tc25.py::test_assignment_success_and_conflicts`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.629s
- Ảnh:
  - `export/test-evidence/run-20261105-133708/TC24_tc24_ph_n_c_ng_th_nh_c_ng_ng_log_v_t_ch_i_ktv_kh_ng_i_u_ki_n.png` — tồn tại

### TC25 - TC25: lịch liền kề, trùng, DA_HUY và trạng thái phiếu bị chặn.
- Hàm test: `tests/integration/test_tc22_tc25.py::test_appointment_slots`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.582s
- Ảnh:
  - `export/test-evidence/run-20261105-133708/TC25_tc25_l_ch_li_n_k_tr_ng_da_huy_v_tr_ng_th_i_phi_u_b_ch_n.png` — tồn tại

## 4. Danh sách ảnh trong export/test-evidence/
- `_summary.png` (32640 bytes)
- `TC22_tc22_g_i_r_ng_cho_c_p_trung_t_m_nh_m_s_c.png` (40841 bytes)
- `TC23_tc23_ch_m_t_ktv_i_u_ki_n_v_th_t_g_i_ng.png` (41846 bytes)
- `TC24_tc24_ph_n_c_ng_th_nh_c_ng_ng_log_v_t_ch_i_ktv_kh_ng_i_u_ki_n.png` (42150 bytes)
- `TC25_tc25_l_ch_li_n_k_tr_ng_da_huy_v_tr_ng_th_i_phi_u_b_ch_n.png` (41480 bytes)

## 5. Cảnh báo và điểm bất thường
- Không có cảnh báo bất thường.

## 6. Cách chạy lại
- Backend: `python -m pytest -v`
- Giao diện: `python -m pytest tests/ui -v -m ui --headed --slowmo 500`
- Tùy thư mục xuất: Windows PowerShell: `$env:EXPORT_DIR="export"` rồi chạy lại pytest.
