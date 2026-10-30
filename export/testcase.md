# BÁO CÁO KẾT QUẢ KIỂM THỬ TỰ ĐỘNG

## 1. Thông tin lần chạy
- Thời điểm chạy: 2026-10-30T11:52:23+07:00
- Lệnh chạy: `python -m pytest -v`
- Commit hash: `1bf1fff`
- Nhánh Git: `main`
- Python: `3.14.2`
- pytest: `9.1.1`
- Playwright: `không xác định hoặc chưa cài playwright-python`
- Hệ điều hành: `Windows-11-10.0.26300-SP0`
- CSDL dùng: Chưa cấu hình
- Số dòng từng bảng: chưa truy vấn được (không cần PostgreSQL cho bộ test hiện tại)
- Seed dữ liệu đang dùng: không chạy seed trong lần kiểm thử hiện tại.

## 2. Tổng hợp
- Tổng số test: 25; PASS: 25; FAIL: 0; bỏ qua: 0; tổng thời gian: 0.070s.

| Mã | Tên | Loại | Nhóm | Kết quả | Thời gian (s) |
|---|---|---|---|---|---:|
| test_valid_future_half_hour_at_start_of_working_day | test_valid_future_half_hour_at_start_of_working_day | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_adjacent_half_hour_can_end_at_closing_time | test_adjacent_half_hour_can_end_at_closing_time | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_sunday_appointment_is_rejected | test_sunday_appointment_is_rejected | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_me_requires_a_bearer_token | test_me_requires_a_bearer_token | Chưa được khai báo trong test. | service | PASS | 0.010 |
| test_ticket_api_requires_a_bearer_token | test_ticket_api_requires_a_bearer_token | Chưa được khai báo trong test. | service | PASS | 0.010 |
| test_invalid_credentials_return_the_srs_error | test_invalid_credentials_return_the_srs_error | Chưa được khai báo trong test. | service | PASS | 0.004 |
| test_bad_request_body_uses_contract_validation_error | test_bad_request_body_uses_contract_validation_error | Chưa được khai báo trong test. | service | PASS | 0.003 |
| test_srs_endpoints_are_registered | test_srs_endpoints_are_registered | Chưa được khai báo trong test. | service | PASS | 0.018 |
| test_cors_allows_the_vite_origin | test_cors_allows_the_vite_origin | Chưa được khai báo trong test. | service | PASS | 0.005 |
| test_token_contains_the_required_user_claims | test_token_contains_the_required_user_claims | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_token_rejects_bad_signature | test_token_rejects_bad_signature | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_signing_requires_a_configured_secret | test_signing_requires_a_configured_secret | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_root_returns_greeting | The root endpoint returns the expected greeting. | Chưa được khai báo trong test. | service | PASS | 0.005 |
| test_database_check_returns_database_time | The database check route returns the time supplied by its service. | Chưa được khai báo trong test. | service | PASS | 0.004 |
| test_normalize_phone | test_normalize_phone[0909 123 456-0909123456] | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_normalize_phone | test_normalize_phone[+84 909.123.456-0909123456] | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_normalize_phone | test_normalize_phone[84909123456-0909123456] | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_normalize_phone | test_normalize_phone[-None] | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_normalize_phone | test_normalize_phone[123456789-None] | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_normalize_status_accepts_source_and_database_codes | test_normalize_status_accepts_source_and_database_codes[DA_PHAN_CONG-DA_PHAN_CONG] | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_normalize_status_accepts_source_and_database_codes | test_normalize_status_accepts_source_and_database_codes[\u0110\xc3_PH\xc2N_C\xd4NG-DA_PHAN_CONG] | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_normalize_status_accepts_source_and_database_codes | test_normalize_status_accepts_source_and_database_codes[CHO_LINH_KIEN-CHO_LINH_KIEN] | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_normalize_status_accepts_source_and_database_codes | test_normalize_status_accepts_source_and_database_codes[\u0110ANG_X\u1eec_L\xdd-DANG_XU_LY] | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_normalize_status_accepts_source_and_database_codes | test_normalize_status_accepts_source_and_database_codes[DA_DONG-DA_DONG] | Chưa được khai báo trong test. | service | PASS | 0.001 |
| test_normalize_status_rejects_unknown_code | test_normalize_status_rejects_unknown_code | Chưa được khai báo trong test. | service | PASS | 0.001 |

## 3. Chi tiết từng test case

### test_valid_future_half_hour_at_start_of_working_day - test_valid_future_half_hour_at_start_of_working_day
- Hàm test: `tests/test_appointment_validation.py::test_valid_future_half_hour_at_start_of_working_day`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_valid_future_half_hour_at_start_of_working_day_valid_future_half_hour_at_start_of_working_day.png` — tồn tại

### test_adjacent_half_hour_can_end_at_closing_time - test_adjacent_half_hour_can_end_at_closing_time
- Hàm test: `tests/test_appointment_validation.py::test_adjacent_half_hour_can_end_at_closing_time`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_adjacent_half_hour_can_end_at_closing_time_adjacent_half_hour_can_end_at_closing_time.png` — tồn tại

### test_sunday_appointment_is_rejected - test_sunday_appointment_is_rejected
- Hàm test: `tests/test_appointment_validation.py::test_sunday_appointment_is_rejected`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_sunday_appointment_is_rejected_sunday_appointment_is_rejected.png` — tồn tại

### test_me_requires_a_bearer_token - test_me_requires_a_bearer_token
- Hàm test: `tests/test_auth_routes.py::test_me_requires_a_bearer_token`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.010s
- Ảnh:
  - `export/test-evidence/test_me_requires_a_bearer_token_me_requires_a_bearer_token.png` — tồn tại

### test_ticket_api_requires_a_bearer_token - test_ticket_api_requires_a_bearer_token
- Hàm test: `tests/test_auth_routes.py::test_ticket_api_requires_a_bearer_token`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.010s
- Ảnh:
  - `export/test-evidence/test_ticket_api_requires_a_bearer_token_ticket_api_requires_a_bearer_token.png` — tồn tại

### test_invalid_credentials_return_the_srs_error - test_invalid_credentials_return_the_srs_error
- Hàm test: `tests/test_auth_routes.py::test_invalid_credentials_return_the_srs_error`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.004s
- Ảnh:
  - `export/test-evidence/test_invalid_credentials_return_the_srs_error_invalid_credentials_return_the_srs_error.png` — tồn tại

### test_bad_request_body_uses_contract_validation_error - test_bad_request_body_uses_contract_validation_error
- Hàm test: `tests/test_auth_routes.py::test_bad_request_body_uses_contract_validation_error`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.003s
- Ảnh:
  - `export/test-evidence/test_bad_request_body_uses_contract_validation_error_bad_request_body_uses_contract_validation_error.png` — tồn tại

### test_srs_endpoints_are_registered - test_srs_endpoints_are_registered
- Hàm test: `tests/test_auth_routes.py::test_srs_endpoints_are_registered`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.018s
- Ảnh:
  - `export/test-evidence/test_srs_endpoints_are_registered_srs_endpoints_are_registered.png` — tồn tại

### test_cors_allows_the_vite_origin - test_cors_allows_the_vite_origin
- Hàm test: `tests/test_auth_routes.py::test_cors_allows_the_vite_origin`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.005s
- Ảnh:
  - `export/test-evidence/test_cors_allows_the_vite_origin_cors_allows_the_vite_origin.png` — tồn tại

### test_token_contains_the_required_user_claims - test_token_contains_the_required_user_claims
- Hàm test: `tests/test_auth_tokens.py::test_token_contains_the_required_user_claims`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_token_contains_the_required_user_claims_token_contains_the_required_user_claims.png` — tồn tại

### test_token_rejects_bad_signature - test_token_rejects_bad_signature
- Hàm test: `tests/test_auth_tokens.py::test_token_rejects_bad_signature`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_token_rejects_bad_signature_token_rejects_bad_signature.png` — tồn tại

### test_signing_requires_a_configured_secret - test_signing_requires_a_configured_secret
- Hàm test: `tests/test_auth_tokens.py::test_signing_requires_a_configured_secret`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_signing_requires_a_configured_secret_signing_requires_a_configured_secret.png` — tồn tại

### test_root_returns_greeting - The root endpoint returns the expected greeting.
- Hàm test: `tests/test_main.py::test_root_returns_greeting`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.005s
- Ảnh:
  - `export/test-evidence/test_root_returns_greeting_the_root_endpoint_returns_the_expected_greeting.png` — tồn tại

### test_database_check_returns_database_time - The database check route returns the time supplied by its service.
- Hàm test: `tests/test_main.py::test_database_check_returns_database_time`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.004s
- Ảnh:
  - `export/test-evidence/test_database_check_returns_database_time_the_database_check_route_returns_the_time_supplied_by_its_service.png` — tồn tại

### test_normalize_phone - test_normalize_phone[0909 123 456-0909123456]
- Hàm test: `tests/test_seed_helpers.py::test_normalize_phone[0909 123 456-0909123456]`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_normalize_phone_normalize_phone_0909_123_456_0909123456.png` — tồn tại

### test_normalize_phone - test_normalize_phone[+84 909.123.456-0909123456]
- Hàm test: `tests/test_seed_helpers.py::test_normalize_phone[+84 909.123.456-0909123456]`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_normalize_phone_normalize_phone_84_909_123_456_0909123456.png` — tồn tại

### test_normalize_phone - test_normalize_phone[84909123456-0909123456]
- Hàm test: `tests/test_seed_helpers.py::test_normalize_phone[84909123456-0909123456]`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_normalize_phone_normalize_phone_84909123456_0909123456.png` — tồn tại

### test_normalize_phone - test_normalize_phone[-None]
- Hàm test: `tests/test_seed_helpers.py::test_normalize_phone[-None]`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_normalize_phone_normalize_phone_none.png` — tồn tại

### test_normalize_phone - test_normalize_phone[123456789-None]
- Hàm test: `tests/test_seed_helpers.py::test_normalize_phone[123456789-None]`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_normalize_phone_normalize_phone_123456789_none.png` — tồn tại

### test_normalize_status_accepts_source_and_database_codes - test_normalize_status_accepts_source_and_database_codes[DA_PHAN_CONG-DA_PHAN_CONG]
- Hàm test: `tests/test_seed_helpers.py::test_normalize_status_accepts_source_and_database_codes[DA_PHAN_CONG-DA_PHAN_CONG]`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_normalize_status_accepts_source_and_database_codes_normalize_status_accepts_source_and_database_codes_da_phan_cong_da_phan_cong.png` — tồn tại

### test_normalize_status_accepts_source_and_database_codes - test_normalize_status_accepts_source_and_database_codes[\u0110\xc3_PH\xc2N_C\xd4NG-DA_PHAN_CONG]
- Hàm test: `tests/test_seed_helpers.py::test_normalize_status_accepts_source_and_database_codes[\u0110\xc3_PH\xc2N_C\xd4NG-DA_PHAN_CONG]`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_normalize_status_accepts_source_and_database_codes_normalize_status_accepts_source_and_database_codes_u0110_xc3_ph_xc2n_c_xd4ng_da_.png` — tồn tại

### test_normalize_status_accepts_source_and_database_codes - test_normalize_status_accepts_source_and_database_codes[CHO_LINH_KIEN-CHO_LINH_KIEN]
- Hàm test: `tests/test_seed_helpers.py::test_normalize_status_accepts_source_and_database_codes[CHO_LINH_KIEN-CHO_LINH_KIEN]`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_normalize_status_accepts_source_and_database_codes_normalize_status_accepts_source_and_database_codes_cho_linh_kien_cho_linh_kien.png` — tồn tại

### test_normalize_status_accepts_source_and_database_codes - test_normalize_status_accepts_source_and_database_codes[\u0110ANG_X\u1eec_L\xdd-DANG_XU_LY]
- Hàm test: `tests/test_seed_helpers.py::test_normalize_status_accepts_source_and_database_codes[\u0110ANG_X\u1eec_L\xdd-DANG_XU_LY]`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_normalize_status_accepts_source_and_database_codes_normalize_status_accepts_source_and_database_codes_u0110ang_x_u1eec_l_xdd_dang_x.png` — tồn tại

### test_normalize_status_accepts_source_and_database_codes - test_normalize_status_accepts_source_and_database_codes[DA_DONG-DA_DONG]
- Hàm test: `tests/test_seed_helpers.py::test_normalize_status_accepts_source_and_database_codes[DA_DONG-DA_DONG]`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_normalize_status_accepts_source_and_database_codes_normalize_status_accepts_source_and_database_codes_da_dong_da_dong.png` — tồn tại

### test_normalize_status_rejects_unknown_code - test_normalize_status_rejects_unknown_code
- Hàm test: `tests/test_seed_helpers.py::test_normalize_status_rejects_unknown_code`
- Loại: Chưa được khai báo trong test.
- Truy vết: Chưa khai báo trong docstring hoặc marker.
- Given: Chưa được khai báo trong test.
- When: Chưa được khai báo trong test.
- Then (kỳ vọng): Chưa được khai báo trong test.
- Dữ liệu thật đã dùng: Chưa được khai báo trong test.
- Kết quả thực tế: Chưa được khai báo trong test.
- Kết quả: PASS; thời gian: 0.001s
- Ảnh:
  - `export/test-evidence/test_normalize_status_rejects_unknown_code_normalize_status_rejects_unknown_code.png` — tồn tại

## 4. Danh sách ảnh trong export/test-evidence/
- `_summary.png` (180741 bytes)
- `test_adjacent_half_hour_can_end_at_closing_time_adjacent_half_hour_can_end_at_closing_time.png` (38935 bytes)
- `test_bad_request_body_uses_contract_validation_error_bad_request_body_uses_contract_validation_error.png` (39227 bytes)
- `test_cors_allows_the_vite_origin_cors_allows_the_vite_origin.png` (38306 bytes)
- `test_database_check_returns_database_time_the_database_check_route_returns_the_time_supplied_by_its_service.png` (39834 bytes)
- `test_invalid_credentials_return_the_srs_error_invalid_credentials_return_the_srs_error.png` (38150 bytes)
- `test_me_requires_a_bearer_token_me_requires_a_bearer_token.png` (37674 bytes)
- `test_normalize_phone_normalize_phone_0909_123_456_0909123456.png` (39709 bytes)
- `test_normalize_phone_normalize_phone_123456789_none.png` (39967 bytes)
- `test_normalize_phone_normalize_phone_84909123456_0909123456.png` (40126 bytes)
- `test_normalize_phone_normalize_phone_84_909_123_456_0909123456.png` (40384 bytes)
- `test_normalize_phone_normalize_phone_none.png` (37381 bytes)
- `test_normalize_status_accepts_source_and_database_codes_normalize_status_accepts_source_and_database_codes_cho_linh_kien_cho_linh_kien.png` (38784 bytes)
- `test_normalize_status_accepts_source_and_database_codes_normalize_status_accepts_source_and_database_codes_da_dong_da_dong.png` (38784 bytes)
- `test_normalize_status_accepts_source_and_database_codes_normalize_status_accepts_source_and_database_codes_da_phan_cong_da_phan_cong.png` (38784 bytes)
- `test_normalize_status_accepts_source_and_database_codes_normalize_status_accepts_source_and_database_codes_u0110_xc3_ph_xc2n_c_xd4ng_da_.png` (38784 bytes)
- `test_normalize_status_accepts_source_and_database_codes_normalize_status_accepts_source_and_database_codes_u0110ang_x_u1eec_l_xdd_dang_x.png` (38784 bytes)
- `test_normalize_status_rejects_unknown_code_normalize_status_rejects_unknown_code.png` (38807 bytes)
- `test_root_returns_greeting_the_root_endpoint_returns_the_expected_greeting.png` (38850 bytes)
- `test_signing_requires_a_configured_secret_signing_requires_a_configured_secret.png` (38411 bytes)
- `test_srs_endpoints_are_registered_srs_endpoints_are_registered.png` (38217 bytes)
- `test_sunday_appointment_is_rejected_sunday_appointment_is_rejected.png` (38533 bytes)
- `test_ticket_api_requires_a_bearer_token_ticket_api_requires_a_bearer_token.png` (38110 bytes)
- `test_token_contains_the_required_user_claims_token_contains_the_required_user_claims.png` (38309 bytes)
- `test_token_rejects_bad_signature_token_rejects_bad_signature.png` (38704 bytes)
- `test_valid_future_half_hour_at_start_of_working_day_valid_future_half_hour_at_start_of_working_day.png` (39475 bytes)

## 5. Cảnh báo và điểm bất thường
- `test_valid_future_half_hour_at_start_of_working_day` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_valid_future_half_hour_at_start_of_working_day` không theo mẫu mã TCxx.
- `test_adjacent_half_hour_can_end_at_closing_time` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_adjacent_half_hour_can_end_at_closing_time` không theo mẫu mã TCxx.
- `test_sunday_appointment_is_rejected` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_sunday_appointment_is_rejected` không theo mẫu mã TCxx.
- `test_me_requires_a_bearer_token` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_me_requires_a_bearer_token` không theo mẫu mã TCxx.
- `test_ticket_api_requires_a_bearer_token` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_ticket_api_requires_a_bearer_token` không theo mẫu mã TCxx.
- `test_invalid_credentials_return_the_srs_error` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_invalid_credentials_return_the_srs_error` không theo mẫu mã TCxx.
- `test_bad_request_body_uses_contract_validation_error` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_bad_request_body_uses_contract_validation_error` không theo mẫu mã TCxx.
- `test_srs_endpoints_are_registered` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_srs_endpoints_are_registered` không theo mẫu mã TCxx.
- `test_cors_allows_the_vite_origin` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_cors_allows_the_vite_origin` không theo mẫu mã TCxx.
- `test_token_contains_the_required_user_claims` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_token_contains_the_required_user_claims` không theo mẫu mã TCxx.
- `test_token_rejects_bad_signature` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_token_rejects_bad_signature` không theo mẫu mã TCxx.
- `test_signing_requires_a_configured_secret` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_signing_requires_a_configured_secret` không theo mẫu mã TCxx.
- `test_root_returns_greeting` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_root_returns_greeting` không theo mẫu mã TCxx.
- `test_database_check_returns_database_time` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_database_check_returns_database_time` không theo mẫu mã TCxx.
- `test_normalize_phone` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_normalize_phone` không theo mẫu mã TCxx.
- `test_normalize_phone` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_normalize_phone` không theo mẫu mã TCxx.
- `test_normalize_phone` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_normalize_phone` không theo mẫu mã TCxx.
- `test_normalize_phone` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_normalize_phone` không theo mẫu mã TCxx.
- `test_normalize_phone` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_normalize_phone` không theo mẫu mã TCxx.
- `test_normalize_status_accepts_source_and_database_codes` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_normalize_status_accepts_source_and_database_codes` không theo mẫu mã TCxx.
- `test_normalize_status_accepts_source_and_database_codes` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_normalize_status_accepts_source_and_database_codes` không theo mẫu mã TCxx.
- `test_normalize_status_accepts_source_and_database_codes` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_normalize_status_accepts_source_and_database_codes` không theo mẫu mã TCxx.
- `test_normalize_status_accepts_source_and_database_codes` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_normalize_status_accepts_source_and_database_codes` không theo mẫu mã TCxx.
- `test_normalize_status_accepts_source_and_database_codes` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_normalize_status_accepts_source_and_database_codes` không theo mẫu mã TCxx.
- `test_normalize_status_rejects_unknown_code` không có marker `@pytest.mark.tc`; mã được lấy tạm từ tên hàm.
- `test_normalize_status_rejects_unknown_code` không theo mẫu mã TCxx.
- Mã TC trùng `test_normalize_phone` xuất hiện 5 lần.
- Mã TC trùng `test_normalize_status_accepts_source_and_database_codes` xuất hiện 5 lần.

## 6. Cách chạy lại
- Backend: `python -m pytest -v`
- Giao diện: `python -m pytest tests/ui -v -m ui --headed --slowmo 500`
- Tùy thư mục xuất: Windows PowerShell: `$env:EXPORT_DIR="export"` rồi chạy lại pytest.
