# Test Report – BT3 (12 test case chạy thật)

Sinh viên: Nguyễn Quốc Việt – MSSV 2374802010556 · Track SE · L04 · Kế hoạch: [test-plan.md](test-plan.md)

- **Mã nguồn test:** [tests/bt3/test_bt3.py](../tests/bt3/test_bt3.py). Mỗi test dựng tiền điều kiện bằng SQL trên bản sao
  `smartcrm_work_test` (clone từ dữ liệu thật `smartcrm_test`), thực hiện bước bằng **Swagger của backend thật**,
  chụp ảnh bằng Playwright, ghi kết quả đọc được từ API/CSDL, rồi mới so với kết quả mong đợi.
- **Chạy cả bộ:** `python -m pytest -m bt3` · **chạy lại một case:** `python -m pytest -m bt3 -k tc05` (thay số).
- **Kết quả thực tế từng lần chạy** do test tự ghi: [docs/screenshots/bt3-ket-qua-chay.md](screenshots/bt3-ket-qua-chay.md).
- **Ảnh:** [docs/screenshots/](screenshots/) – mỗi ảnh là khối Swagger gồm lệnh `curl`, URL và phản hồi thật của server.

## Tổng kết

| Lần chạy | Commit | Số TC | PASS | FAIL | Ghi chú |
|---|---|---|---|---|---|
| Lần 1 (08/11/2026 16:35) | `9cccebd` | 12 | 11 | 1 | TC-07 FAIL → BUG-08 ([kết quả lần 1](screenshots/BUG-08_truoc-sua_ket-qua-chay.md)) |
| Lần 2 sau khi sửa BUG-08 (08/11/2026) | `224fd69` | 12 | 12 | 0 | TC-07 chạy lại PASS |
| Lần 3 (10/11/2026 14:29–14:34), lần chạy cho ảnh hiện tại | `4e16cf3` | 12 | 12 | 0 | Kết quả như lần 2; TC-03, TC-05 đặt lịch ngày 10/12/2026 vì test chọn ngày trống cách ngày chạy ~30 ngày ([ảnh terminal](screenshots/BT3-12-passed.png)) |

| Loại (5 loại BT3) | Test case |
|---|---|
| Luồng đúng | TC-01, TC-02, TC-03 |
| Giá trị biên (hai bên ranh giới) | TC-04 (tay nghề 3 \| 2), TC-05 (lịch liền kề \| chồng 1 phút) |
| Dữ liệu sai | TC-06, TC-07, TC-08 |
| Bảo mật / chất lượng dữ liệu | TC-09 (A01), TC-10 (A07), TC-11 (A05, A02) |
| Tái lập | TC-12 |

| Mã | Tên | Loại | Ưu tiên | Truy vết | Kết quả |
|---|---|---|---|---|---|
| TC-01 | Gợi ý KTV đúng thứ tự khối lượng | Luồng đúng | Cao | US2 · FR2 · QT-08 · (TC01 Buổi 10) | PASS |
| TC-02 | Phân công thành công và ghi lịch sử | Luồng đúng | Cao | US3 · FR3 · QT-07 · (TC04) | PASS |
| TC-03 | Đặt lịch hẹn hợp lệ | Luồng đúng | Cao | FR6 · A2 · (TC08) | PASS |
| TC-04 | Biên tay nghề 3 \| 2 | Biên | Cao | FR2, FR3 · QT-08 · (TC05, TC06) | PASS |
| TC-05 | Biên lịch liền kề \| chồng 1 phút | Biên | Cao | FR7 · A3 · (TC09, TC10) | PASS |
| TC-06 | Đổi KTV lý do chỉ khoảng trắng | Dữ liệu sai | Trung bình | FR4 · QT-07 · (TC12) | PASS |
| TC-07 | Tạo phiếu SĐT sai / trường chỉ khoảng trắng | Dữ liệu sai | Trung bình | QT-02 · TD-17 | **FAIL → sửa BUG-08 → PASS** |
| TC-08 | Mã phiếu không tồn tại / vượt BIGINT | Dữ liệu sai | Trung bình | Hợp đồng lỗi (README §4) | PASS |
| TC-09 | A01 sửa phiếu của người khác | Bảo mật | Cao | QT-14 · OWASP A01 · (TC13) | PASS |
| TC-10 | A07 token thiếu / hết hạn / bị sửa | Bảo mật | Cao | OWASP A07 | PASS |
| TC-11 | A05 injection, XSS · A02 CORS, lộ lỗi | Bảo mật | Cao | OWASP A05, A02 | PASS |
| TC-12 | Dựng CSDL hai lần không nhân đôi | Tái lập | Trung bình | C5 · TD-19 | PASS |

## Chi tiết tám cột

Mỗi khối ghi đủ tám cột: **Mã · Tiền điều kiện · Các bước · Dữ liệu thử · Kết quả mong đợi · Ưu tiên · Kết quả thực tế · PASS/FAIL**.

### TC-01 – Gợi ý kỹ thuật viên đúng thứ tự khối lượng công việc tăng dần

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Trên bản sao: chọn cặp (trung tâm, nhóm) có ≥ 3 KTV đang làm, tay nghề ≥ 3 → TT03, nhóm KHAC. Đóng phiếu đang giữ thật của 3 KTV đầu, tạo cho họ 5/2/8 phiếu `DA_PHAN_CONG`; tắt các KTV đủ điều kiện khác; tạo 1 phiếu MỚI TEST-7816. |
| Các bước | 1. Đăng nhập QL_TT03, lấy token. 2. Swagger Authorize bằng token. 3. Gọi `GET /api/tickets/7816/technician-suggestions`. |
| Dữ liệu thử | QL_TT03; phiếu 7816 (KHAC); khối lượng KT003 = 5, KT022 = 2, KT027 = 8 |
| Kết quả mong đợi | HTTP 200; đúng 3 KTV theo thứ tự KT022 (2) → KT003 (5) → KT027 (8) |
| Ưu tiên | Cao |
| Kết quả thực tế | HTTP 200; thứ tự KT022 (2) → KT003 (5) → KT027 (8) |
| PASS/FAIL | **PASS** · [TC-01.png](screenshots/TC-01.png) |

### TC-02 – Phân công kỹ thuật viên đủ điều kiện cho phiếu MỚI và ghi lịch sử

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Như TC-01 (phiếu MỚI TEST-7816, chưa có KTV, 1 dòng log). |
| Các bước | 1. Đăng nhập QL_TT03. 2. Gọi `POST /api/tickets/7816/assignment` body `{"technician_id": 22}`. 3. Đọc lại bảng `ticket` và đếm `ticket_status_log` của phiếu. |
| Dữ liệu thử | technician_id = 22 (KT022, tay nghề 3, khối lượng nhỏ nhất) |
| Kết quả mong đợi | HTTP 201; `ticket.status = DA_PHAN_CONG`, `technician_id = 22`; log của phiếu tăng đúng 1 dòng |
| Ưu tiên | Cao |
| Kết quả thực tế | HTTP 201; status = DA_PHAN_CONG, technician_id = 22; log 1 → 2 |
| PASS/FAIL | **PASS** · [TC-02.png](screenshots/TC-02.png) |

### TC-03 – Đặt lịch hẹn NHẬN hợp lệ 09:00–10:00

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Phiếu thật BH-000009/2026 ở `DA_PHAN_CONG`, KTV KT008 (id 8), trung tâm 1. Ngày thứ Hai–Bảy đầu tiên cách hôm nay ≥ 30 ngày mà KT008 trống 09:00–10:00 (10/12/2026 ở lần chạy 3; ngày thay đổi theo ngày chạy). |
| Các bước | 1. Đăng nhập QL_TT01. 2. Đếm bảng `appointment`. 3. Gọi `POST /api/appointments`. 4. Đếm lại. |
| Dữ liệu thử | `{"ticket_id": 9, "appointment_type": "NHAN", "start_at": "2026-12-10T09:00:00+07:00", "end_at": "2026-12-10T10:00:00+07:00", "note": "BT3 TC-03"}` |
| Kết quả mong đợi | HTTP 201; lịch `status = DA_HEN`, `technician_id = 8` (theo KTV của phiếu); bảng appointment +1 |
| Ưu tiên | Cao |
| Kết quả thực tế | HTTP 201; status = DA_HEN, technician_id = 8; appointment 300 → 301 |
| PASS/FAIL | **PASS** · [TC-03.png](screenshots/TC-03.png) |

### TC-04 – Biên tay nghề: = 3 được gợi ý, = 2 bị loại và bị từ chối phân công

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Trung tâm 1: đặt KT020 tay nghề MAN_HINH = 3, KT033 tay nghề MAN_HINH = 2 (cả hai đang làm). Tạo phiếu MỚI nhóm MAN_HINH ở trung tâm 1. |
| Các bước | 1. Đăng nhập QL_TT01. 2. `GET /api/tickets/{id}/technician-suggestions`. 3. `POST /api/tickets/{id}/assignment` với KT033. 4. Đọc lại phiếu. |
| Dữ liệu thử | Ranh giới QT-08 “tay nghề ≥ 3”: giá trị 3 (trong) và 2 (ngoài); technician_id của KT033 |
| Kết quả mong đợi | (a) 200, KT020 có trong gợi ý với proficiency 3, KT033 không có. (b) 400 `TECHNICIAN_NOT_ELIGIBLE`; phiếu vẫn MOI, chưa có KTV |
| Ưu tiên | Cao |
| Kết quả thực tế | (a) HTTP 200: KT020 có, KT033 không có; (b) HTTP 400 TECHNICIAN_NOT_ELIGIBLE; phiếu còn MOI, technician_id = None |
| PASS/FAIL | **PASS** · [TC-04.png](screenshots/TC-04.png), [TC-04_b.png](screenshots/TC-04_b.png) |

### TC-05 – Biên lịch hẹn: liền kề hợp lệ, chồng 1 phút bị 409

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Phiếu BH-000009/2026, KT008; ngày 10/12/2026 KT008 trống 08:00–11:00; tạo trước lịch A 09:00–10:00 qua API. |
| Các bước | 1. Đăng nhập QL_TT01. 2. Đếm lịch `DA_HEN` của KT008. 3. `POST /api/appointments` 10:00–11:00. 4. `POST /api/appointments` 08:00–09:01. 5. Đếm lại. |
| Dữ liệu thử | (a) start 10:00 = end của A (khoảng nửa mở `[)`); (b) 08:00–09:01, chồng A đúng 1 phút |
| Kết quả mong đợi | (a) 201. (b) 409 `APPOINTMENT_OVERLAP` kèm khung trống gợi ý. Lịch DA_HEN của KTV chỉ tăng 1 |
| Ưu tiên | Cao |
| Kết quả thực tế | (a) HTTP 201; (b) HTTP 409 APPOINTMENT_OVERLAP, gợi ý 2 khung trống; lịch DA_HEN của KT008 8 → 9 |
| PASS/FAIL | **PASS** · [TC-05.png](screenshots/TC-05.png), [TC-05_b.png](screenshots/TC-05_b.png) |

### TC-06 – Đổi kỹ thuật viên với lý do chỉ có khoảng trắng

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Phiếu BH-000009/2026 của KT008 (`DA_PHAN_CONG`); KT012 cùng trung tâm, đang làm, tay nghề ≥ 3 với nhóm của phiếu. |
| Các bước | 1. Đăng nhập QL_TT01. 2. `PUT /api/tickets/9/assignment`. 3. Đọc lại phiếu và đếm log. |
| Dữ liệu thử | `{"technician_id": 12, "reason": "   "}` (3 dấu cách) |
| Kết quả mong đợi | 400 `REASON_REQUIRED`; phiếu vẫn của KT008; log không thêm dòng |
| Ưu tiên | Trung bình |
| Kết quả thực tế | HTTP 400 REASON_REQUIRED “Lý do đổi kỹ thuật viên là bắt buộc.”; technician_id vẫn 8; log 2 → 2 |
| PASS/FAIL | **PASS** · [TC-06.png](screenshots/TC-06.png) |

### TC-07 – Tạo phiếu với SĐT sai và với trường bắt buộc chỉ có khoảng trắng

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Dữ liệu thật trên bản sao: 7.317 phiếu, không phiếu nào có tên/mô tả rỗng. |
| Các bước | 1. Đăng nhập QL_TT01. 2. Đếm bảng `ticket`. 3. `POST /api/tickets` với SĐT sai. 4. `POST /api/tickets` với ba trường chữ chỉ có khoảng trắng. 5. Đếm lại và đếm phiếu có tên/mô tả rỗng. |
| Dữ liệu thử | Phần còn lại hợp lệ (PIN, CAO, hạn +3 ngày). (a) `customer_phone = "09123"`; (b) `customer_name = serial_no = issue_desc = "   "`, `customer_phone = "0912345678"` |
| Kết quả mong đợi | (a) 400 `INVALID_PHONE`. (b) 400, phản hồi nêu tên trường `customer_name`. Bảng ticket không thêm bản ghi |
| Ưu tiên | Trung bình |
| Kết quả thực tế – lần 1 (commit `9cccebd`) | (a) HTTP 400 INVALID_PHONE; **(b) HTTP 201, tạo phiếu BH-007801/2026 với `customer_name = ""`, `serial_no = ""`, `issue_desc = ""`; bảng ticket 7317 → 7318** |
| PASS/FAIL – lần 1 | **FAIL** → [BUG-08](bug-log.md#bug-08) · [ảnh a](screenshots/BUG-08_truoc-sua_TC-07.png), [ảnh b](screenshots/BUG-08_truoc-sua_TC-07_b.png) |
| Kết quả thực tế – lần 2 (sau sửa, commit `224fd69`) | (a) HTTP 400 INVALID_PHONE; (b) HTTP 400 REQUIRED_FIELD_BLANK, `fields = [customer_name, serial_no, issue_desc]`; bảng ticket 7317 → 7317; phiếu có tên/mô tả rỗng: 0 |
| PASS/FAIL – lần 2 | **PASS** · [TC-07.png](screenshots/TC-07.png), [TC-07_b.png](screenshots/TC-07_b.png) |

### TC-08 – Mã phiếu không tồn tại và mã vượt giới hạn BIGINT

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Mã phiếu lớn nhất trong dữ liệu thật là 7800. |
| Các bước | 1. Đăng nhập QL_TT01. 2. `GET /api/tickets/99999999`. 3. `GET /api/tickets/99999999999999999999`. |
| Dữ liệu thử | (a) 99 999 999 (không tồn tại); (b) 99 999 999 999 999 999 999 (> 2^63 − 1, giới hạn BIGINT) |
| Kết quả mong đợi | Cả hai: 404 `TICKET_NOT_FOUND`, **không phải 500** |
| Ưu tiên | Trung bình |
| Kết quả thực tế | (a) HTTP 404 TICKET_NOT_FOUND; (b) HTTP 404 TICKET_NOT_FOUND |
| PASS/FAIL | **PASS** · [TC-08.png](screenshots/TC-08.png), [TC-08_b.png](screenshots/TC-08_b.png) · *Giả thuyết trước khi chạy là (b) sẽ ra 500; chạy thật cho thấy không – PostgreSQL so sánh như số và không tìm thấy dòng nào.* |

### TC-09 – A01: sửa phiếu không thuộc quyền mình

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Phiếu BH-000009/2026 của KT008 ở `DA_PHAN_CONG`; KT002 là KTV khác, đang làm. Phiếu MỚI BH-000001/2025 thuộc trung tâm 5, tên khách “Hoàng Anh Dung”. |
| Các bước | 1. Đăng nhập KT002, gọi `PATCH /api/tickets/9/status` `{"to_status": "DANG_XU_LY"}`. 2. Đăng nhập QL_TT01 (trung tâm 1), gọi `PUT /api/tickets/{id BH-000001/2025}` với `customer_name = "Đã bị sửa"`. 3. Đọc lại hai phiếu và log. |
| Dữ liệu thử | Token KT002; token QL_TT01; hai phiếu nêu trên |
| Kết quả mong đợi | (a) 403, phiếu 9 vẫn DA_PHAN_CONG, log không đổi. (b) 403, tên khách không đổi |
| Ưu tiên | Cao |
| Kết quả thực tế | (a) HTTP 403 FORBIDDEN, phiếu vẫn DA_PHAN_CONG, log 2 → 2; (b) HTTP 403 FORBIDDEN, tên khách vẫn “Hoàng Anh Dung” |
| PASS/FAIL | **PASS** · [TC-09.png](screenshots/TC-09.png), [TC-09_b.png](screenshots/TC-09_b.png) |

### TC-10 – A07: token thiếu, hết hạn, bị sửa một ký tự

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Backend chạy với `SECRET_KEY` của `.env`; tài khoản QL_TT01 đăng nhập được (đối chứng). |
| Các bước | 1. `GET /api/auth/me` không Authorize. 2. Authorize bằng token hết hạn, gọi lại. 3. Authorize bằng token bị sửa, gọi lại. 4. Đối chứng: gọi bằng token gốc. |
| Dữ liệu thử | (b) token QL_TT01 ký đúng khoá nhưng `exp = now − 60 s`; (c) token QL_TT01 hợp lệ, đổi ký tự đầu của phần chữ ký |
| Kết quả mong đợi | Cả ba: 401; token gốc vẫn 200 |
| Ưu tiên | Cao |
| Kết quả thực tế | (a) HTTP 401 UNAUTHORIZED; (b) HTTP 401 INVALID_TOKEN; (c) HTTP 401 INVALID_TOKEN; đối chứng: HTTP 200 |
| PASS/FAIL | **PASS** · [TC-10.png](screenshots/TC-10.png), [TC-10_b.png](screenshots/TC-10_b.png), [TC-10_c.png](screenshots/TC-10_c.png) |

### TC-11 – A05 injection và XSS, A02 CORS và lộ thông tin lỗi

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Frontend chạy ở `http://localhost:5173`; QL_TT01 có 5 phiếu MỚI. |
| Các bước | 1. `GET /api/tickets?status=' OR 1=1 --`. 2. `GET /api/tickets?status=MOI&category_code=' OR 1=1 --`. 3. Tạo phiếu có mô tả chứa thẻ script, mở M2 của phiếu đó trên giao diện, theo dõi hộp thoại `alert`. 4. Gửi preflight `OPTIONS /api/tickets` từ `http://evil.example` và từ frontend. |
| Dữ liệu thử | `' OR 1=1 --`; `issue_desc = <script>alert('XSS')</script><img src=x onerror=alert(1)>` |
| Kết quả mong đợi | (a) 400 `INVALID_STATUS`, phản hồi không có traceback/SQL. (b) 200, `total = 0` (không trả hết bản ghi). (c) Chuỗi hiện nguyên văn, không có hộp thoại nào. (d) Không có `Access-Control-Allow-Origin` cho evil.example; có cho frontend |
| Ưu tiên | Cao |
| Kết quả thực tế | (a) HTTP 400 INVALID_STATUS, không có traceback/SQL; (b) HTTP 200, total = 0; (c) chuỗi hiện nguyên văn, 0 hộp thoại; (d) Allow-Origin cho evil.example = không có, cho http://localhost:5173 = http://localhost:5173 |
| PASS/FAIL | **PASS** · [TC-11.png](screenshots/TC-11.png), [TC-11_b.png](screenshots/TC-11_b.png), [TC-11_c.png](screenshots/TC-11_c.png) |

### TC-12 – Dựng CSDL hai lần trên bộ mẫu không nhân đôi

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Database `smartcrm_load_test` không tồn tại (test xoá trước và sau). |
| Các bước | 1. `DATA_DIR=data/sample DB_NAME=smartcrm_load_test python scripts/setup_all.py`. 2. Đếm sáu bảng. 3. Chạy lại bước 1. 4. Đếm lại, đếm phiếu MOI. |
| Dữ liệu thử | Bộ mẫu `data/sample` trong repo |
| Kết quả mong đợi | Hai lần cùng số dòng: service_center 6, technician 38, technician_skill 159, ticket 939, ticket_status_log 3237, appointment 300; phiếu MOI = 30 |
| Ưu tiên | Trung bình |
| Kết quả thực tế | Lần 1 và lần 2 đều: service_center = 6, technician = 38, technician_skill = 159, ticket = 939, ticket_status_log = 3237, appointment = 300; phiếu MOI = 30 |
| PASS/FAIL | **PASS** · ảnh terminal [TC-12.png](screenshots/TC-12.png) |
