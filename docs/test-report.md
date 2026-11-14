# Test Report – BT3 (12 test case cốt lõi + 13 test case bổ sung, chạy thật)

Sinh viên: Nguyễn Quốc Việt – MSSV 2374802010556 · Track SE · L04 · Kế hoạch: [test-plan.md](test-plan.md)

- **Mã nguồn test:** [tests/bt3/test_bt3.py](../tests/bt3/test_bt3.py). Mỗi test dựng tiền điều kiện bằng SQL trên bản sao
  `smartcrm_work_test` (clone từ dữ liệu thật `smartcrm_test`), thực hiện bước bằng **Swagger của backend thật**,
  chụp ảnh bằng Playwright, ghi kết quả đọc được từ API/CSDL, rồi mới so với kết quả mong đợi.
- **Chạy cả bộ (25 case):** `python -m pytest -m bt3` · **chạy lại một case:** `python -m pytest -m bt3 -k tc05` (thay số). Lệnh cho từng case: README mục 5.3.
- **Mã nguồn test bổ sung (giao diện cải tiến, TD-26/TD-27):** [tests/bt3/test_bt3_v2.py](../tests/bt3/test_bt3_v2.py).
- **Kết quả thực tế từng lần chạy** do test tự ghi: [docs/screenshots/bt3-ket-qua-chay.md](screenshots/bt3-ket-qua-chay.md).
- **Ảnh:** [docs/screenshots/](screenshots/) – mỗi ảnh là khối Swagger gồm lệnh `curl`, URL và phản hồi thật của server.

## Tổng kết

| Lần chạy | Commit | Số TC | PASS | FAIL | Ghi chú |
|---|---|---|---|---|---|
| Lần 1 (08/11/2026 16:35) | `9cccebd` | 12 | 11 | 1 | TC-07 FAIL → BUG-08 ([kết quả lần 1](screenshots/BUG-08_truoc-sua_ket-qua-chay.md)) |
| Lần 2 sau khi sửa BUG-08 (08/11/2026) | `224fd69` | 12 | 12 | 0 | TC-07 chạy lại PASS |
| Lần 3 (10/11/2026 14:29–14:34) | `4e16cf3` | 12 | 12 | 0 | Kết quả như lần 2; TC-03, TC-05 đặt lịch ngày 10/12/2026 vì test chọn ngày trống cách ngày chạy ~30 ngày ([ảnh terminal](screenshots/BT3-12-passed.png)) |
| Lần 4 (15/11/2026 04:33–04:38), lần chạy cho kết quả và ảnh hiện tại | `4f901a4` | 25 | 25 | 0 | 12 case cốt lõi và 13 case bổ sung trên giao diện cải tiến; dữ liệu đầy đủ `smartcrm_test` ([kết quả tự ghi](screenshots/bt3-ket-qua-chay.md), [ảnh terminal](screenshots/run4-test-pass.png)) |

| Loại (5 loại BT3) | Test case cốt lõi | Test case bổ sung |
|---|---|---|
| Luồng đúng | TC-01, TC-02, TC-03 | TC-13, TC-14, TC-15, TC-16, TC-17 |
| Giá trị biên (hai bên ranh giới) | TC-04 (tay nghề 3 \| 2), TC-05 (lịch liền kề \| chồng 1 phút) | TC-18 (17:30–18:00 \| 17:31–18:01), TC-19 (20 \| 21 phiếu) |
| Dữ liệu sai | TC-06, TC-07, TC-08 | TC-20, TC-21, TC-22 |
| Bảo mật / chất lượng dữ liệu | TC-09 (A01), TC-10 (A07), TC-11 (A05, A02) | TC-23 (A01 API), TC-24 (A01 giao diện) |
| Tái lập | TC-12 | TC-25 |

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
| TC-13 | Quản lý tạo phiếu bằng "+ Tạo phiếu mới" | Luồng đúng | Cao | QT-02 · TD-17 · TD-26 | PASS |
| TC-14 | Quản lý sửa phiếu MỚI | Luồng đúng | Trung bình | QT-02 · TD-17 · TD-26 | PASS |
| TC-15 | Kỹ thuật viên đổi giờ lịch trên trang "Lịch hẹn của tôi" | Luồng đúng | Cao | FR6, FR7 · A2 · TD-26 | PASS |
| TC-16 | Quản lý hủy lịch hẹn (hủy mềm) | Luồng đúng | Cao | QT-13 · FR6 · TD-26 | PASS |
| TC-17 | Hoàn tất phiếu phải xác nhận | Luồng đúng | Cao | FR8 · QT-06 · TD-26 | PASS |
| TC-18 | Biên giờ làm việc khi đổi giờ lịch | Biên | Cao | FR7 · A2 (08:00–18:00) | PASS |
| TC-19 | Biên phân trang 20 \| 21 phiếu | Biên | Trung bình | FR1 · giao diện M1 (20 dòng/trang) | PASS |
| TC-20 | Tạo phiếu trên giao diện với dữ liệu sai | Dữ liệu sai | Trung bình | QT-02 · TD-17 | PASS |
| TC-21 | Đổi giờ lịch trùng lịch khác trên giao diện | Dữ liệu sai | Cao | FR7 · A3 · NFR2 | PASS |
| TC-22 | Hủy khi không còn hợp lệ | Dữ liệu sai | Trung bình | QT-13 · TD-17 | PASS |
| TC-23 | A01: phạm vi danh sách lịch hẹn | Bảo mật | Cao | QT-14 · OWASP A01 | PASS |
| TC-24 | A01: điều hướng giao diện theo vai trò | Bảo mật | Cao | QT-14 · OWASP A01 | PASS |
| TC-25 | Nạp lại dữ liệu không ghi đè thao tác của người dùng | Tái lập | Trung bình | C8 · TD-19 | PASS |

## Chi tiết tám cột

Mỗi khối ghi đủ tám cột: **Mã · Tiền điều kiện · Các bước · Dữ liệu thử · Kết quả mong đợi · Ưu tiên · Kết quả thực tế · PASS/FAIL**.

### TC-01 – Gợi ý kỹ thuật viên đúng thứ tự khối lượng công việc tăng dần

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Trên bản sao: chọn cặp (trung tâm, nhóm) có ≥ 3 KTV đang làm, tay nghề ≥ 3 → TT03, nhóm KHAC. Đóng phiếu đang giữ thật của 3 KTV đầu, tạo cho họ 5/2/8 phiếu `DA_PHAN_CONG`; tắt các KTV đủ điều kiện khác; tạo 1 phiếu MỚI TEST-7816. |
| Các bước | 1. Đăng nhập QL_TT03, lấy token. 2. Swagger Authorize bằng token. 3. Gọi `GET /api/tickets/7816/technician-suggestions`. |
| Dữ liệu thử | QL_TT03; phiếu 7816 (KHAC); khối lượng KT003 = 5, KT022 = 2, KT027 = 8 · *Lần 4 (15/11/2026 04:33–04:38):* QL_TT03, phiếu MỚI TEST-7816 nhóm KHAC; khối lượng KT003=5, KT022=2, KT027=8 |
| Kết quả mong đợi | HTTP 200; đúng 3 KTV theo thứ tự KT022 (2) → KT003 (5) → KT027 (8) |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): HTTP 200; thứ tự KT022 (2) → KT003 (5) → KT027 (8) |
| PASS/FAIL | **PASS** · [TC-01.png](screenshots/TC-01.png) |

### TC-02 – Phân công kỹ thuật viên đủ điều kiện cho phiếu MỚI và ghi lịch sử

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Như TC-01 (phiếu MỚI TEST-7816, chưa có KTV, 1 dòng log). |
| Các bước | 1. Đăng nhập QL_TT03. 2. Gọi `POST /api/tickets/7816/assignment` body `{"technician_id": 22}`. 3. Đọc lại bảng `ticket` và đếm `ticket_status_log` của phiếu. |
| Dữ liệu thử | technician_id = 22 (KT022, tay nghề 3, khối lượng nhỏ nhất) · *Lần 4 (15/11/2026 04:33–04:38):* QL_TT03, phiếu TEST-7816, technician_id=22 (KT022) |
| Kết quả mong đợi | HTTP 201; `ticket.status = DA_PHAN_CONG`, `technician_id = 22`; log của phiếu tăng đúng 1 dòng |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): HTTP 201; ticket.status=DA_PHAN_CONG, technician_id=22; ticket_status_log của phiếu 1 → 2 |
| PASS/FAIL | **PASS** · [TC-02.png](screenshots/TC-02.png) |

### TC-03 – Đặt lịch hẹn NHẬN hợp lệ 09:00–10:00

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Phiếu thật BH-000009/2026 ở `DA_PHAN_CONG`, KTV KT008 (id 8), trung tâm 1. Ngày thứ Hai–Bảy đầu tiên cách hôm nay ≥ 30 ngày mà KT008 trống 09:00–10:00 (10/12/2026 ở lần chạy 3; ngày thay đổi theo ngày chạy). |
| Các bước | 1. Đăng nhập QL_TT01. 2. Đếm bảng `appointment`. 3. Gọi `POST /api/appointments`. 4. Đếm lại. |
| Dữ liệu thử | `{"ticket_id": 9, "appointment_type": "NHAN", "start_at": "2026-12-10T09:00:00+07:00", "end_at": "2026-12-10T10:00:00+07:00", "note": "BT3 TC-03"}` · *Lần 4 (15/11/2026 04:33–04:38):* Phiếu BH-000009/2026 (KTV KT008), 15/12/2026 09:00–10:00 NHAN |
| Kết quả mong đợi | HTTP 201; lịch `status = DA_HEN`, `technician_id = 8` (theo KTV của phiếu); bảng appointment +1 |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): HTTP 201; status=DA_HEN, technician_id=8; bảng appointment 300 → 301 |
| PASS/FAIL | **PASS** · [TC-03.png](screenshots/TC-03.png) |

### TC-04 – Biên tay nghề: = 3 được gợi ý, = 2 bị loại và bị từ chối phân công

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Trung tâm 1: đặt KT020 tay nghề MAN_HINH = 3, KT033 tay nghề MAN_HINH = 2 (cả hai đang làm). Tạo phiếu MỚI nhóm MAN_HINH ở trung tâm 1. |
| Các bước | 1. Đăng nhập QL_TT01. 2. `GET /api/tickets/{id}/technician-suggestions`. 3. `POST /api/tickets/{id}/assignment` với KT033. 4. Đọc lại phiếu. |
| Dữ liệu thử | Ranh giới QT-08 “tay nghề ≥ 3”: giá trị 3 (trong) và 2 (ngoài); technician_id của KT033 · *Lần 4 (15/11/2026 04:33–04:38):* Phiếu MỚI MAN_HINH trung tâm 1; KT020 tay nghề 3, KT033 tay nghề 2 |
| Kết quả mong đợi | (a) 200, KT020 có trong gợi ý với proficiency 3, KT033 không có. (b) 400 `TECHNICIAN_NOT_ELIGIBLE`; phiếu vẫn MOI, chưa có KTV |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): (a) gợi ý HTTP 200: KT020 có, KT033 không có; (b) phân công KT033: HTTP 400 TECHNICIAN_NOT_ELIGIBLE; phiếu còn MOI, technician_id=None |
| PASS/FAIL | **PASS** · [TC-04.png](screenshots/TC-04.png), [TC-04_b.png](screenshots/TC-04_b.png) |

### TC-05 – Biên lịch hẹn: liền kề hợp lệ, chồng 1 phút bị 409

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Phiếu BH-000009/2026, KT008; ngày 10/12/2026 KT008 trống 08:00–11:00; tạo trước lịch A 09:00–10:00 qua API. |
| Các bước | 1. Đăng nhập QL_TT01. 2. Đếm lịch `DA_HEN` của KT008. 3. `POST /api/appointments` 10:00–11:00. 4. `POST /api/appointments` 08:00–09:01. 5. Đếm lại. |
| Dữ liệu thử | (a) start 10:00 = end của A (khoảng nửa mở `[)`); (b) 08:00–09:01, chồng A đúng 1 phút · *Lần 4 (15/11/2026 04:33–04:38):* Phiếu BH-000009/2026, KTV KT008, 15/12/2026; đã có lịch A 09:00–10:00; (a) 10:00–11:00, (b) 08:00–09:01 |
| Kết quả mong đợi | (a) 201. (b) 409 `APPOINTMENT_OVERLAP` kèm khung trống gợi ý. Lịch DA_HEN của KTV chỉ tăng 1 |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): (a) HTTP 201; (b) HTTP 409 APPOINTMENT_OVERLAP, gợi ý 2 khung trống; lịch DA_HEN của KTV 8 → 9 |
| PASS/FAIL | **PASS** · [TC-05.png](screenshots/TC-05.png), [TC-05_b.png](screenshots/TC-05_b.png) |

### TC-06 – Đổi kỹ thuật viên với lý do chỉ có khoảng trắng

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Phiếu BH-000009/2026 của KT008 (`DA_PHAN_CONG`); KT012 cùng trung tâm, đang làm, tay nghề ≥ 3 với nhóm của phiếu. |
| Các bước | 1. Đăng nhập QL_TT01. 2. `PUT /api/tickets/9/assignment`. 3. Đọc lại phiếu và đếm log. |
| Dữ liệu thử | `{"technician_id": 12, "reason": "   "}` (3 dấu cách) · *Lần 4 (15/11/2026 04:33–04:38):* Phiếu BH-000009/2026 của KT008 → KT012, reason="   " (3 dấu cách) |
| Kết quả mong đợi | 400 `REASON_REQUIRED`; phiếu vẫn của KT008; log không thêm dòng |
| Ưu tiên | Trung bình |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): HTTP 400 REASON_REQUIRED "Lý do đổi kỹ thuật viên là bắt buộc."; technician_id vẫn 8; log 2 → 2 |
| PASS/FAIL | **PASS** · [TC-06.png](screenshots/TC-06.png) |

### TC-07 – Tạo phiếu với SĐT sai và với trường bắt buộc chỉ có khoảng trắng

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Dữ liệu thật trên bản sao: 7.317 phiếu, không phiếu nào có tên/mô tả rỗng. |
| Các bước | 1. Đăng nhập QL_TT01. 2. Đếm bảng `ticket`. 3. `POST /api/tickets` với SĐT sai. 4. `POST /api/tickets` với ba trường chữ chỉ có khoảng trắng. 5. Đếm lại và đếm phiếu có tên/mô tả rỗng. |
| Dữ liệu thử | Phần còn lại hợp lệ (PIN, CAO, hạn +3 ngày). (a) `customer_phone = "09123"`; (b) `customer_name = serial_no = issue_desc = "   "`, `customer_phone = "0912345678"` · *Lần 4 (15/11/2026 04:33–04:38):* QL_TT01; (a) customer_phone="09123"; (b) customer_name, serial_no, issue_desc = "   " |
| Kết quả mong đợi | (a) 400 `INVALID_PHONE`. (b) 400, phản hồi nêu tên trường `customer_name`. Bảng ticket không thêm bản ghi |
| Ưu tiên | Trung bình |
| Kết quả thực tế – lần 1 (commit `9cccebd`) | (a) HTTP 400 INVALID_PHONE; **(b) HTTP 201, tạo phiếu BH-007801/2026 với `customer_name = ""`, `serial_no = ""`, `issue_desc = ""`; bảng ticket 7317 → 7318** |
| PASS/FAIL – lần 1 | **FAIL** → [BUG-08](bug-log.md#bug-08) · [ảnh a](screenshots/BUG-08_truoc-sua_TC-07.png), [ảnh b](screenshots/BUG-08_truoc-sua_TC-07_b.png) |
| Kết quả thực tế – lần 2 (sau sửa, commit `224fd69`) | (a) HTTP 400 INVALID_PHONE; (b) HTTP 400 REQUIRED_FIELD_BLANK, `fields = [customer_name, serial_no, issue_desc]`; bảng ticket 7317 → 7317; phiếu có tên/mô tả rỗng: 0 |
| PASS/FAIL – lần 2 | **PASS** · [TC-07.png](screenshots/TC-07.png), [TC-07_b.png](screenshots/TC-07_b.png) |
| Kết quả thực tế – lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`) | (a) HTTP 400 INVALID_PHONE; (b) HTTP 400 REQUIRED_FIELD_BLANK; bảng ticket 7317 → 7317; số phiếu có tên/mô tả rỗng: 0 |
| PASS/FAIL – lần 4 (15/11/2026 04:33–04:38) | **PASS** · [TC-07.png](screenshots/TC-07.png), [TC-07_b.png](screenshots/TC-07_b.png) |

### TC-08 – Mã phiếu không tồn tại và mã vượt giới hạn BIGINT

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Mã phiếu lớn nhất trong dữ liệu thật là 7800. |
| Các bước | 1. Đăng nhập QL_TT01. 2. `GET /api/tickets/99999999`. 3. `GET /api/tickets/99999999999999999999`. |
| Dữ liệu thử | (a) 99 999 999 (không tồn tại); (b) 99 999 999 999 999 999 999 (> 2^63 − 1, giới hạn BIGINT) · *Lần 4 (15/11/2026 04:33–04:38):* ticket_id=99999999 (max thật 7800); ticket_id=99999999999999999999 (> 2^63−1) |
| Kết quả mong đợi | Cả hai: 404 `TICKET_NOT_FOUND`, **không phải 500** |
| Ưu tiên | Trung bình |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): (a) HTTP 404 TICKET_NOT_FOUND; (b) HTTP 404 TICKET_NOT_FOUND |
| PASS/FAIL | **PASS** · [TC-08.png](screenshots/TC-08.png), [TC-08_b.png](screenshots/TC-08_b.png) |

### TC-09 – A01: sửa phiếu không thuộc quyền mình

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Phiếu BH-000009/2026 của KT008 ở `DA_PHAN_CONG`; KT002 là KTV khác, đang làm. Phiếu MỚI BH-000001/2025 thuộc trung tâm 5, tên khách “Hoàng Anh Dung”. |
| Các bước | 1. Đăng nhập KT002, gọi `PATCH /api/tickets/9/status` `{"to_status": "DANG_XU_LY"}`. 2. Đăng nhập QL_TT01 (trung tâm 1), gọi `PUT /api/tickets/{id BH-000001/2025}` với `customer_name = "Đã bị sửa"`. 3. Đọc lại hai phiếu và log. |
| Dữ liệu thử | Token KT002; token QL_TT01; hai phiếu nêu trên · *Lần 4 (15/11/2026 04:33–04:38):* (a) token KT002, phiếu BH-000009/2026 của KT008; (b) token QL_TT01, phiếu BH-000001/2025 (trung tâm 5) |
| Kết quả mong đợi | (a) 403, phiếu 9 vẫn DA_PHAN_CONG, log không đổi. (b) 403, tên khách không đổi |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): (a) HTTP 403 FORBIDDEN, phiếu vẫn DA_PHAN_CONG, log 2 → 2; (b) HTTP 403 FORBIDDEN, tên khách vẫn "Hoàng Anh Dung" |
| PASS/FAIL | **PASS** · [TC-09.png](screenshots/TC-09.png), [TC-09_b.png](screenshots/TC-09_b.png) |

### TC-10 – A07: token thiếu, hết hạn, bị sửa một ký tự

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Backend chạy với `SECRET_KEY` của `.env`; tài khoản QL_TT01 đăng nhập được (đối chứng). |
| Các bước | 1. `GET /api/auth/me` không Authorize. 2. Authorize bằng token hết hạn, gọi lại. 3. Authorize bằng token bị sửa, gọi lại. 4. Đối chứng: gọi bằng token gốc. |
| Dữ liệu thử | (b) token QL_TT01 ký đúng khoá nhưng `exp = now − 60 s`; (c) token QL_TT01 hợp lệ, đổi ký tự đầu của phần chữ ký · *Lần 4 (15/11/2026 04:33–04:38):* GET /api/auth/me: (a) không header Authorization; (b) token QL_TT01 ký đúng nhưng exp = now − 60 s; (c) token QL_TT01 hợp lệ đổi ký tự đầu của chữ ký |
| Kết quả mong đợi | Cả ba: 401; token gốc vẫn 200 |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): (a) HTTP 401 UNAUTHORIZED; (b) HTTP 401 INVALID_TOKEN; (c) HTTP 401 INVALID_TOKEN; đối chứng token gốc: HTTP 200 |
| PASS/FAIL | **PASS** · [TC-10.png](screenshots/TC-10.png), [TC-10_b.png](screenshots/TC-10_b.png), [TC-10_c.png](screenshots/TC-10_c.png) |

### TC-11 – A05 injection và XSS, A02 CORS và lộ thông tin lỗi

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Frontend chạy ở `http://localhost:5173`; QL_TT01 có 5 phiếu MỚI. |
| Các bước | 1. `GET /api/tickets?status=' OR 1=1 --`. 2. `GET /api/tickets?status=MOI&category_code=' OR 1=1 --`. 3. Tạo phiếu có mô tả chứa thẻ script, mở M2 của phiếu đó trên giao diện, theo dõi hộp thoại `alert`. 4. Gửi preflight `OPTIONS /api/tickets` từ `http://evil.example` và từ frontend. |
| Dữ liệu thử | `' OR 1=1 --`; `issue_desc = <script>alert('XSS')</script><img src=x onerror=alert(1)>` · *Lần 4 (15/11/2026 04:33–04:38):* QL_TT01; (a) status="' OR 1=1 --"; (b) status=MOI&category_code="' OR 1=1 --"; (c) issue_desc="<script>alert('XSS')</script><img src=x onerror=alert(1)>" mở ở M2; (d) preflight OPTIONS từ http://evil.example và http://localhost:5173 |
| Kết quả mong đợi | (a) 400 `INVALID_STATUS`, phản hồi không có traceback/SQL. (b) 200, `total = 0` (không trả hết bản ghi). (c) Chuỗi hiện nguyên văn, không có hộp thoại nào. (d) Không có `Access-Control-Allow-Origin` cho evil.example; có cho frontend |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): (a) HTTP 400 INVALID_STATUS; (b) HTTP 200, total=0; (c) chuỗi hiện nguyên văn, hộp thoại alert bật: 0; (d) Allow-Origin cho evil.example = None, cho http://localhost:5173 = http://localhost:5173; phản hồi lỗi không chứa traceback/SQL: True |
| PASS/FAIL | **PASS** · [TC-11.png](screenshots/TC-11.png), [TC-11_b.png](screenshots/TC-11_b.png), [TC-11_c.png](screenshots/TC-11_c.png) |

### TC-12 – Dựng CSDL hai lần trên bộ mẫu không nhân đôi

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Database `smartcrm_load_test` không tồn tại (test xoá trước và sau). |
| Các bước | 1. `DATA_DIR=data/sample DB_NAME=smartcrm_load_test python scripts/setup_all.py`. 2. Đếm sáu bảng. 3. Chạy lại bước 1. 4. Đếm lại, đếm phiếu MOI. |
| Dữ liệu thử | Bộ mẫu `data/sample` trong repo · *Lần 4 (15/11/2026 04:33–04:38):* DATA_DIR=data/sample, database smartcrm_load_test (xoá trước khi chạy), chạy `python scripts/setup_all.py` hai lần |
| Kết quả mong đợi | Hai lần cùng số dòng: service_center 6, technician 38, technician_skill 159, ticket 939, ticket_status_log 3237, appointment 300; phiếu MOI = 30 |
| Ưu tiên | Trung bình |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): lần 1: service_center=6, technician=38, technician_skill=159, ticket=939, ticket_status_log=3237, appointment=300; lần 2: service_center=6, technician=38, technician_skill=159, ticket=939, ticket_status_log=3237, appointment=300; phiếu MOI = 30 |
| PASS/FAIL | **PASS** · ảnh terminal [TC-12.png](screenshots/TC-12.png) |

## Test case bổ sung (TC-13…TC-25) – giao diện cải tiến

Mười hai test case trên là phần cốt lõi theo yêu cầu 10–12 của BT3. Mười ba test case dưới đây kiểm các chức năng thêm ở giao diện cải tiến (TD-26) và chỗ còn thiếu test (`GET /api/appointments`); chúng chạy cùng lệnh `python -m pytest -m bt3`, cùng cách cô lập dữ liệu và cùng tám cột.

### TC-13 – Quản lý tạo phiếu bằng nút "+ Tạo phiếu mới": phiếu MỚI được lưu, số trên tab tăng 1

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Bản sao dữ liệu thật; trung tâm 1 có các phiếu MỚI thật; frontend chạy. |
| Các bước | 1. Đăng nhập QL_TT01 trên giao diện. 2. Ghi số trên tab "Chờ phân công". 3. Bấm "+ Tạo phiếu mới", nhập đủ trường, bấm "Tạo phiếu". 4. Đọc lại bảng `ticket`, log và số trên tab. |
| Dữ liệu thử | QL_TT01; khách "Nguyễn Thị Thu (TC-13)", SĐT "0912 345 613", serial SN-TC13-0001, SAC, CAO, hạn mặc định +3 ngày 17:00 |
| Kết quả mong đợi | HTTP 201; phiếu mới trạng thái MOI, đúng trung tâm 1; SĐT chuẩn hoá 10 số; bảng ticket +1; log của phiếu 1 dòng; số trên tab +1 và bằng SQL |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): HTTP 201, phiếu BH-007801/2026: status MOI, center 1, SĐT lưu 0912345613; ticket 7317 → 7318; MOI trung tâm 1 5 → 6 (tab hiển thị 6); log của phiếu 1 |
| PASS/FAIL | **PASS** · [TC-13.png](screenshots/TC-13.png), [TC-13_b.png](screenshots/TC-13_b.png) |

### TC-14 – Quản lý sửa phiếu MỚI (mô tả, mức ưu tiên): chỉ hai trường đó đổi, hạn cam kết giữ nguyên

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Phiếu MỚI thật đầu tiên của trung tâm 1 (đã quá hạn cam kết). |
| Các bước | 1. Đăng nhập QL_TT01. 2. Ở dòng phiếu bấm "Sửa". 3. Đổi mô tả lỗi và mức ưu tiên, bấm "Lưu thay đổi". 4. Đọc lại phiếu. |
| Dữ liệu thử | QL_TT01; phiếu BH-000153/2026 (MỚI, hạn 29/07/2026 17:30); mô tả mới "Cập nhật TC-14: màn hình chớp khi mở camera", ưu tiên TRUNG_BINH → THAP |
| Kết quả mong đợi | HTTP 200; chỉ `issue_desc` và `priority` đổi; 7 trường còn lại (khách, SĐT, serial, nhóm, hạn cam kết, trạng thái, trung tâm) giữ nguyên – sửa được cả phiếu đã quá hạn vì hạn không đổi |
| Ưu tiên | Trung bình |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): HTTP 200; issue_desc = "Cập nhật TC-14: màn hình chớp khi mở camera", priority = THAP; giữ nguyên 7/7 trường khác (customer_name, customer_phone, serial_no, category_code, due_date, status, center_id) |
| PASS/FAIL | **PASS** · [TC-14.png](screenshots/TC-14.png), [TC-14_b.png](screenshots/TC-14_b.png) |

### TC-15 – Kỹ thuật viên đổi giờ lịch trên trang "Lịch hẹn của tôi" sang 10:00, thời lượng 60 phút

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Phiếu ĐÃ PHÂN CÔNG có KTV đang làm cùng trung tâm; ngày D (≥ 30 ngày tới, Thứ Hai–Thứ Bảy) KTV trống 09:00–12:00; đặt trước lịch 09:00–09:30 qua API. |
| Các bước | 1. Đăng nhập bằng KTV. 2. Menu "Lịch hẹn của tôi". 3. Ở dòng lịch bấm "Đổi giờ", chọn 10:00 và thời lượng 60 phút. 4. Bấm "Lưu lịch hẹn". 5. Đọc lại lịch. |
| Dữ liệu thử | KT008, phiếu BH-000009/2026; lịch #301 ngày 15/12/2026 09:00–09:30 → 10:00, 60 phút |
| Kết quả mong đợi | HTTP 200; lịch thành 10:00–11:00 ngày D, vẫn ĐÃ HẸN, vẫn của KTV đó |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): HTTP 200; lịch #301: 10:00–11:00, status DA_HEN, KTV KT008 |
| PASS/FAIL | **PASS** · [TC-15.png](screenshots/TC-15.png), [TC-15_b.png](screenshots/TC-15_b.png) |

### TC-16 – Quản lý hủy lịch ở trang chi tiết phiếu: lịch thành ĐÃ HỦY, bản ghi còn, khung giờ được giải phóng

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Như TC-15, lịch 09:00–09:30 ngày D; ghi số dòng bảng `appointment`. |
| Các bước | 1. Đăng nhập Quản lý trung tâm của phiếu. 2. Mở trang chi tiết phiếu. 3. Ở dòng lịch bấm "Hủy lịch", rồi "Xác nhận hủy lịch". 4. Đếm bảng; đặt lại đúng khung giờ đó qua API. |
| Dữ liệu thử | QL_TT02, phiếu BH-000009/2026; lịch #301 15/12/2026 09:00–09:30 (ĐÃ HẸN) |
| Kết quả mong đợi | Lịch thành ĐÃ HỦY; bảng `appointment` không mất dòng nào; đặt lại cùng khung giờ được (201) |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): lịch #301 status DA_HUY; bảng appointment 301 → 301 (không xoá dòng); đặt lại đúng khung đó: HTTP 201 |
| PASS/FAIL | **PASS** · [TC-16.png](screenshots/TC-16.png), [TC-16_b.png](screenshots/TC-16_b.png) |

### TC-17 – Kỹ thuật viên bấm Hoàn tất: "Quay lại" không đổi gì, "Xác nhận" mới chuyển HOÀN TẤT

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Phiếu ĐÃ PHÂN CÔNG được KTV chuyển sang ĐANG XỬ LÝ qua API. |
| Các bước | 1. Đăng nhập KTV, mở phiếu bằng liên kết `/my-tickets?ticket=<id>`. 2. Bấm "Hoàn tất", ở hộp xác nhận bấm "Quay lại". 3. Bấm "Hoàn tất" lần nữa, bấm "Xác nhận". 4. Sau mỗi lần đọc trạng thái và log. |
| Dữ liệu thử | KT008, phiếu BH-000009/2026 đang DANG_XU_LY (log 3); mở bằng liên kết /my-tickets?ticket=9 |
| Kết quả mong đợi | Sau "Quay lại": vẫn ĐANG XỬ LÝ, log không thêm; sau "Xác nhận": HOÀN TẤT, log +1 |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): sau "Quay lại": DANG_XU_LY, log 3; sau "Xác nhận": HOAN_TAT, log 4 |
| PASS/FAIL | **PASS** · [TC-17.png](screenshots/TC-17.png), [TC-17_b.png](screenshots/TC-17_b.png) |

### TC-18 – Biên giờ làm việc khi đổi giờ lịch: 17:30–18:00 được, 17:31–18:01 bị 400

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Lịch 17:00–17:30 ngày D (KTV trống 17:00–18:00). |
| Các bước | 1. Swagger, Authorize bằng Quản lý. 2. `PUT /api/appointments/{id}` 17:30–18:00. 3. `PUT` 17:31–18:01. 4. Đọc lại lịch sau mỗi bước. |
| Dữ liệu thử | lịch #301 (phiếu BH-000009/2026) ngày 15/12/2026; ranh giới 18:00: (a) 17:30–18:00, (b) 17:31–18:01 |
| Kết quả mong đợi | (a) 200, lịch kết thúc đúng 18:00 (trong biên); (b) 400 `OUTSIDE_WORKING_HOURS` (vượt biên 1 phút), lịch giữ nguyên 17:30–18:00 |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): (a) HTTP 200, lịch 17:30–18:00; (b) HTTP 400 OUTSIDE_WORKING_HOURS, lịch vẫn 17:30–18:00 |
| PASS/FAIL | **PASS** · [TC-18.png](screenshots/TC-18.png), [TC-18_b.png](screenshots/TC-18_b.png) |

### TC-19 – Biên phân trang danh sách phiếu: 20 phiếu MỚI là 1 trang, 21 phiếu là 2 trang (trang 2 có 1 dòng)

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Trên bản sao đặt đúng 20 phiếu MỚI cho trung tâm 1 (tạo thêm từ bản ghi thật). |
| Các bước | 1. Đăng nhập QL_TT01, xem tab Chờ phân công. 2. Thêm 1 phiếu MỚI (ưu tiên THẤP), tải lại trang. 3. Bấm "Sau". |
| Dữ liệu thử | QL_TT01; trên bản sao đặt đúng 20 phiếu MỚI ở trung tâm 1, sau đó thêm 1 phiếu (ưu tiên THẤP, xếp cuối) |
| Kết quả mong đợi | 20 phiếu: 20 dòng, "Trang 1 / 1"; 21 phiếu: trang 1 có 20 dòng, "Trang 1 / 2"; trang 2 có đúng 1 dòng |
| Ưu tiên | Trung bình |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): 20 phiếu: 20 dòng, "Trang 1 / 1"; 21 phiếu: trang 1 có 20 dòng, "Trang 1 / 2", trang 2 có 1 dòng |
| PASS/FAIL | **PASS** · [TC-19.png](screenshots/TC-19.png), [TC-19_b.png](screenshots/TC-19_b.png) |

### TC-20 – Tạo phiếu trên giao diện với SĐT sai và hạn cam kết đã qua: báo lỗi đúng ô, không lưu phiếu

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Đếm bảng `ticket` trên bản sao. |
| Các bước | 1. Đăng nhập QL_TT01, bấm "+ Tạo phiếu mới". 2. Nhập SĐT "09123", bấm "Tạo phiếu". 3. Sửa SĐT đúng, đặt hạn cam kết là hôm qua, bấm lại. 4. Đếm bảng. |
| Dữ liệu thử | QL_TT01; (a) SĐT "09123"; (b) SĐT đúng, hạn cam kết 14/11/2026 17:00 (hôm qua) |
| Kết quả mong đợi | (a) 400 `INVALID_PHONE`, ô SĐT đánh dấu đỏ; (b) 400 `INVALID_DUE_DATE`, ô hạn cam kết đánh dấu đỏ; bảng ticket không thêm dòng |
| Ưu tiên | Trung bình |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): (a) HTTP 400 INVALID_PHONE, ô SĐT đánh dấu đỏ; (b) HTTP 400 INVALID_DUE_DATE, ô hạn cam kết đánh dấu đỏ; bảng ticket 7317 → 7317 |
| PASS/FAIL | **PASS** · [TC-20.png](screenshots/TC-20.png), [TC-20_b.png](screenshots/TC-20_b.png) |

### TC-21 – Đổi giờ lịch B trùng lịch A trên giao diện: 409, hiện khung trống gợi ý, lịch B giữ nguyên

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Cùng KTV, ngày D: lịch A 09:00–09:30 và lịch B 10:00–10:30 (đặt qua API). |
| Các bước | 1. Quản lý mở trang chi tiết phiếu. 2. Ở lịch B bấm "Đổi giờ", chọn 09:00, bấm "Lưu lịch hẹn". 3. Đọc lại lịch B. |
| Dữ liệu thử | QL_TT02, phiếu BH-000009/2026, ngày 15/12/2026: lịch A #301 09:00–09:30, lịch B #302 10:00–10:30; đổi B sang 09:00–09:30 |
| Kết quả mong đợi | 409 `APPOINTMENT_OVERLAP`, nêu lịch A là xung đột, giao diện hiện các khung trống gợi ý; lịch B giữ nguyên 10:00–10:30 |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): HTTP 409 APPOINTMENT_OVERLAP; xung đột [301], gợi ý 2 khung trống; lịch B vẫn 10:00–10:30 |
| PASS/FAIL | **PASS** · [TC-21.png](screenshots/TC-21.png) |

### TC-22 – Hủy phiếu đã phân công và hủy lịch đã hủy đều bị 409; giao diện không hiện nút Hủy phiếu

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Phiếu ĐÃ PHÂN CÔNG; một lịch của phiếu đã được hủy qua API. |
| Các bước | 1. Swagger `DELETE /api/tickets/{id}`. 2. Swagger `DELETE /api/appointments/{id}` (lịch đã hủy). 3. Mở trang chi tiết phiếu trên giao diện. |
| Dữ liệu thử | QL_TT02; (a) phiếu BH-000009/2026 đang DA_PHAN_CONG; (b) lịch #301 đã DA_HUY; (c) mở trang chi tiết phiếu |
| Kết quả mong đợi | (a) 409 `TICKET_NOT_CANCELLABLE`, phiếu vẫn ĐÃ PHÂN CÔNG, log không đổi; (b) 409 `APPOINTMENT_NOT_CANCELLABLE`; (c) không có nút "Hủy phiếu" |
| Ưu tiên | Trung bình |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): (a) HTTP 409 TICKET_NOT_CANCELLABLE, phiếu vẫn DA_PHAN_CONG, log 2 → 2; (b) HTTP 409 APPOINTMENT_NOT_CANCELLABLE; (c) số nút "Hủy phiếu": 0 |
| PASS/FAIL | **PASS** · [TC-22.png](screenshots/TC-22.png), [TC-22_b.png](screenshots/TC-22_b.png), [TC-22_c.png](screenshots/TC-22_c.png) |

### TC-23 – A01: danh sách lịch hẹn chỉ trả lịch trong phạm vi; KTV khác sửa/hủy lịch bị 403

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Đặt 1 lịch cho phiếu của KTV K; chọn KTV khác K2 đang làm. |
| Các bước | 1. Gọi `GET /api/appointments` (mọi trang) bằng token Quản lý và token K; đối chiếu từng dòng với SQL. 2. Swagger bằng token K: danh sách của mình. 3. Swagger bằng token K2: `PUT` rồi `DELETE` lịch của K. |
| Dữ liệu thử | QL_TT02 (trung tâm 2), KT008 (chủ lịch #301), KT002 (KTV khác) |
| Kết quả mong đợi | Quản lý chỉ nhận lịch của trung tâm mình, đủ số lượng như SQL; K chỉ nhận lịch của mình; K2 nhận 403 cho cả PUT và DELETE, lịch không đổi |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): QL_TT02: 65 lịch, trung tâm [2] (SQL 65); KT008: 9 lịch, mọi dòng technician_id=8: True (SQL 9); KT002: PUT HTTP 403 FORBIDDEN, DELETE HTTP 403 FORBIDDEN; lịch vẫn DA_HEN 09:00 |
| PASS/FAIL | **PASS** · [TC-23.png](screenshots/TC-23.png), [TC-23_b.png](screenshots/TC-23_b.png), [TC-23_c.png](screenshots/TC-23_c.png) |

### TC-24 – A01 trên giao diện: KTV không vào được trang của Quản lý, không mở được phiếu người khác bằng liên kết

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | KTV K; một phiếu không thuộc K. |
| Các bước | 1. Đăng nhập K, mở `/tickets`, `/tickets/{id}`, `/tickets/{id}/assign`. 2. Mở `/my-tickets?ticket=<phiếu không thuộc K>`. 3. Gọi API đọc phiếu đó bằng token K. 4. Đăng nhập Quản lý, mở `/my-tickets`. |
| Dữ liệu thử | KT008 mở /tickets, /tickets/1, /tickets/1/assign và /my-tickets?ticket=1 (phiếu BH-000001/2025 không phải của mình); QL_TT02 mở /my-tickets |
| Kết quả mong đợi | K luôn bị đưa về `/my-tickets`; phiếu không thuộc K không hiện; API trả 403; Quản lý bị đưa về `/tickets` |
| Ưu tiên | Cao |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): KTV bị đưa về {'/my-tickets'}; phiếu BH-000001/2025 hiện: 0 lần; API GET phiếu đó: HTTP 403; Quản lý bị đưa về /tickets |
| PASS/FAIL | **PASS** · [TC-24.png](screenshots/TC-24.png), [TC-24_b.png](screenshots/TC-24_b.png) |

### TC-25 – Chạy lại bước nạp dữ liệu sau khi người dùng đã thao tác: không nhân đôi, không ghi đè thay đổi

| Cột | Nội dung |
|---|---|
| Tiền điều kiện | Trên bản sao: Quản lý tạo 1 phiếu và hủy 1 phiếu MỚI qua API; đếm sáu bảng. |
| Các bước | 1. Chạy lại `scripts/setup_all.py` vào chính bản sao. 2. Đếm lại sáu bảng, đọc hai phiếu. 3. Mở tab "Đã hủy" trên giao diện. |
| Dữ liệu thử | Trên bản sao: QL_TT01 tạo phiếu BH-007801/2026 và hủy phiếu BH-000153/2026 qua API, rồi chạy lại scripts/setup_all.py vào smartcrm_work_test |
| Kết quả mong đợi | setup_all thoát 0; số dòng sáu bảng không đổi (không nhân đôi, không xoá); phiếu vừa tạo vẫn còn; phiếu đã hủy vẫn ĐÃ HỦY và hiện ở tab "Đã hủy" |
| Ưu tiên | Trung bình |
| Kết quả thực tế | Lần 4 (15/11/2026 04:33–04:38) (commit `4f901a4`): setup_all mã thoát 0; số dòng trước {'service_center': 6, 'technician': 38, 'technician_skill': 159, 'ticket': 7318, 'ticket_status_log': 35721, 'appointment': 300} – sau {'service_center': 6, 'technician': 38, 'technician_skill': 159, 'ticket': 7318, 'ticket_status_log': 35721, 'appointment': 300}; phiếu BH-000153/2026 vẫn DA_HUY; phiếu BH-007801/2026 còn: True; tab "Đã hủy" vẫn có BH-000153/2026 |
| PASS/FAIL | **PASS** · [TC-25.png](screenshots/TC-25.png) |
