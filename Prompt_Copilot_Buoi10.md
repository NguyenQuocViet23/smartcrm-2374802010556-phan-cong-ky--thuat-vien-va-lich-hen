# PROMPT CHO COPILOT – BUỔI 10: MODULE MỞ RỘNG, GIAO DIỆN, TÍCH HỢP VÀ KIỂM THỬ (SPRINT 2)

Bạn là kỹ sư phần mềm đang giúp tôi hoàn thành **Bài thực hành Buổi 10** của học phần Chuyên đề Tốt nghiệp 1 (ĐH Văn Lang), dự án **Smart CRM – Mekong Mobile, luồng L04: Phân công kỹ thuật viên và lịch hẹn** (track SE). Repo hiện tại đã có kết quả Buổi 8 (cấu trúc 4 lớp, CRUD, migration). Hãy làm việc trực tiếp trong repo này.

## 0. NGUYÊN TẮC LÀM VIỆC (BẮT BUỘC)

1. **Đọc trước, làm sau.** Không đoán. Mọi nội dung nghiệp vụ lấy từ tài liệu trong repo (xem mục 1). Chỗ nào tài liệu mâu thuẫn hoặc thiếu, ghi lại và hỏi tôi, đừng tự bịa.
2. **Hỏi tôi trước khi thay đổi cấu trúc**: đổi tên/di chuyển thư mục đã nộp, sửa `db/schema.sql` (thêm/bớt bảng hoặc cột), đổi hợp đồng API đã có trong SRS Phụ lục A. Riêng các mục tôi liệt kê rõ là *được phép bổ sung* ở mục 4 thì làm luôn và ghi vào `docs/thay-doi-thiet-ke.md`.
3. **Không dùng dữ liệu tự gõ vài dòng.** Hệ thống và test phải chạy trên dữ liệu mẫu THẬT (16 tệp CSV của case study, xem mục 3).
4. **Tất cả test phải PASS thật.** Cấm: `skip`, `xfail`, nới lỏng assert cho dễ qua, hard-code kết quả. Nếu test fail: tìm nguyên nhân gốc, sửa mã nguồn (lỗi logic) hoặc báo tôi (nếu kỳ vọng trong tài liệu sai/mơ hồ). Báo cáo rõ phần đã sửa.
5. **Bảo mật & Git:** không commit `.env`, mật khẩu, tệp CSV lớn (`customers_raw.csv`, `orders_2024_2026.csv`, `ticket_status_log.csv`, `tickets_history.csv`); không force push. Commit theo Conventional Commits (`feat:`, `fix:`, `test:`, `docs:`, `chore:`, `refactor:`), mỗi commit một việc, hệ thống vẫn chạy được sau mỗi commit.
6. **Thuật ngữ nhất quán:** dùng đúng tên trong SRS (phiếu bảo hành = `ticket`, kỹ thuật viên = `technician`, lịch hẹn = `appointment`, hạn cam kết = `due_date`).
7. Cuối mỗi giai đoạn, báo cáo ngắn (≤ 10 dòng): đã làm gì, chạy lệnh nào, kết quả quan sát được.

## 1. TÀI LIỆU PHẢI ĐỌC TRƯỚC (GIAI ĐOẠN 0 – KHẢO SÁT, CHƯA SỬA GÌ)

- `docs/srs.md` (đặc biệt: Mục 3.2 tiêu chí chấp nhận, Mục 4 use case UC3/UC6, Mục 5 NFR + giả định A1–A6, **Phụ lục A – API contract**, Phụ lục B – dữ liệu).
- `docs/diagrams/wireframe.drawio` (3 trang M1, M2, M3 – **nguồn sự thật cho giao diện**), `architecture.drawio`, `erd.drawio`, `usecase.drawio`.
- `db/schema.sql` (6 bảng: service_center, technician, technician_skill, ticket, appointment, ticket_status_log) và toàn bộ `src/`, `tests/`, `docker-compose.yml`, `README.md`, `.gitignore`, `.env.example`.
- Báo cáo BT1 (nếu có trong `docs/`): mục 5 – bảng "Đối chiếu trường dữ liệu" của M1, M2, M3 và bảng "Chỗ hiển thị luồng ngoại lệ".

Sau khi đọc, trả lời tôi bằng bản tóm tắt: (1) phần nào đã có / chưa có so với yêu cầu Buổi 10, (2) điểm mâu thuẫn giữa tài liệu và mã nguồn, (3) kế hoạch ngắn cho các giai đoạn tiếp theo. Nếu không có mâu thuẫn cần tôi quyết, **tiếp tục** sang giai đoạn 1 mà không cần chờ.

## 2. YÊU CẦU CỦA BUỔI 10 (TÓM TẮT ĐỀ)

- Frontend ≥ 3 màn hình kết nối **API thật**; có `src/api/client.js` và các tệp `*.api.js`; mỗi màn hình bọc bằng thành phần **DataState** (đang tải · rỗng · lỗi); đăng nhập; nhận 401 thì xóa token và về trang đăng nhập. Xong khi: tắt backend → thấy thông báo lỗi có nút thử lại; tìm `fetch(` trong `pages/` ra rỗng.
- Luồng chính chạy end-to-end trên dữ liệu thật, không can thiệp tay giữa chừng.
- ≥ 5 unit test PASS (BT2 yêu cầu ba loại: luồng đúng · giá trị biên · dữ liệu sai). **Yêu cầu của tôi cao hơn: 18 test case ở mục 6, tất cả PASS.**
- README mục các bước dựng hệ thống: mỗi bước một lệnh, đã thử clone vào thư mục mới và chạy đúng theo README.
- Ghi nhận phần đã cắt/đổi và lý do vào `docs/thay-doi-thiet-ke.md`; tổng số commit của repo ≥ 8.

## 3. GIAI ĐOẠN 1 – NẠP DỮ LIỆU THẬT

Tạo `scripts/seed_real_data.py` (chạy bằng một lệnh, nhận `--csv-dir data/raw`, `--seed 20261023`, `--db-url` hoặc đọc `DATABASE_URL`; chạy lại lần hai KHÔNG nhân đôi dòng). Nguồn: bộ 16 tệp CSV của case study (đặt trong `data/raw/`, đã .gitignore). Chỉ dùng các tệp: `service_centers.csv`, `issue_categories.csv`, `technicians.csv`, `technician_skills.csv`, `tickets_history.csv`, `ticket_status_log.csv`, `customers_raw.csv` (để lấy tên/SĐT khách), và `appointments.csv` (sinh bằng `gen_sample.py`).

Quy tắc nạp (kiểm tra thực tế trên tệp trước khi giả định; báo tôi nếu khác):

1. **Ánh xạ trạng thái có dấu → mã không dấu:** ĐÃ_ĐÓNG→DA_DONG, ĐANG_XỬ_LÝ→DANG_XU_LY, CHỜ_LINH_KIỆN→CHO_LINH_KIEN, HOÀN_TẤT→HOAN_TAT, ĐÃ_PHÂN_CÔNG→DA_PHAN_CONG; ưu tiên TRUNG_BÌNH→TRUNG_BINH; `category_id` (1–6) → `category_code` qua `issue_categories.csv` (MAN_HINH, PIN, SAC, PHAN_MEM, NUOC_VAO, KHAC).
2. **Khách hàng:** nối `tickets_history.customer_id` với `customers_raw.csv` (xác minh khóa nối), chuẩn hóa SĐT về 10 chữ số bắt đầu bằng 0 (QT-02). Phiếu không có SĐT hợp lệ (khoảng 6% hồ sơ thiếu SĐT) vi phạm `customer_phone NOT NULL CHECK` → **không sửa schema**; ghi dòng đó vào `data/rejects/tickets_rejected.csv` kèm lý do và in tổng số bị loại.
3. **Lịch sử trạng thái:** nạp `ticket_status_log.csv` vào `ticket_status_log` với `event_type = 'TRANG_THAI'`, ánh xạ trạng thái như trên; dòng không khớp phiếu đã nạp thì loại và ghi lý do.
4. **Lịch hẹn:** chạy `python gen_sample.py --entity appointment --rows 300 --seed 20261023 --link tickets_history.csv --out appointments.csv`, rồi nạp. Dòng vi phạm ràng buộc EXCLUDE (trùng lịch cùng kỹ thuật viên), kỹ thuật viên khác phiếu, hoặc phiếu chưa có kỹ thuật viên → ghi vào `data/rejects/appointments_rejected.csv` kèm lý do.
5. **Phiếu MỚI:** dữ liệu mẫu không có phiếu MOI. Bằng `--seed`, với mỗi trung tâm chọn ngẫu nhiên tối đa 10 phiếu đang DA_PHAN_CONG, đặt lại về MOI, `technician_id = NULL`, giữ lại chỉ dòng log đầu tiên của phiếu. **Cố ý chừa 1 trung tâm (tham số `--empty-center`, mặc định trung tâm cuối cùng) không có phiếu MOI nào** để minh họa trạng thái rỗng.
6. **Tài khoản đăng nhập demo** (không thêm bảng mới – ERD giữ 6 bảng): sinh `data/processed/demo_accounts.json` gồm mỗi trung tâm 1 Quản lý (`QL_<center_code>`) và mỗi kỹ thuật viên (username = `technician_code`); mật khẩu lấy từ biến `DEMO_PASSWORD` trong `.env` (ghi tên biến vào `.env.example`, không ghi giá trị). File này liệt kê cả: trung tâm có dữ liệu, trung tâm bị chừa trống, một kỹ thuật viên phù hợp dùng cho TC18.
7. In báo cáo sau khi nạp: số dòng nguồn → số dòng nạp → số dòng bị loại (theo từng bảng) và lưu `docs/bao-cao-nap-du-lieu.md`.
8. Thêm mẫu nhỏ (vài trăm dòng cho tệp lớn) vào `data/sample/` để người khác chạy nhanh; các tệp danh mục nhỏ (service_centers, technicians, technician_skills, issue_categories) có thể commit đủ. Ghi seed vào README.
9. Tạo thêm CSDL thử nghiệm `smartcrm_test` (biến `TEST_DATABASE_URL`) và nạp bằng cùng script (`--db-url $TEST_DATABASE_URL`).

## 4. GIAI ĐOẠN 2 – BACKEND BỔ SUNG (ĐƯỢC PHÉP LÀM, GHI VÀO thay-doi-thiet-ke.md)

Chỉ được bổ sung các mục sau (mọi thay đổi khác → hỏi tôi):

- `POST /api/auth/login` và `GET /api/auth/me`: JWT (khóa trong `.env` là `SECRET_KEY`), trả `role` (QUAN_LY | KY_THUAT_VIEN), `center_id`, `technician_id` (nếu có), `full_name`, `employee_id`. Sai thông tin → 401. Tài khoản đọc từ `demo_accounts.json`.
- `GET /api/tickets/{ticket_id}`: chi tiết phiếu + lịch sử trạng thái (kể cả DOI_KTV) + kỹ thuật viên hiện tại; áp dụng QT-14 (403) và QT-15 (che SĐT trừ Quản lý trung tâm).
- `GET /api/tickets/{ticket_id}/appointments`: danh sách lịch hẹn của phiếu.
- `GET /api/tickets`: bổ sung lọc `category_code`, `priority`, phân trang `page`, `page_size` (mặc định 20), trả thêm `total`.
- Phản hồi 409 `APPOINTMENT_OVERLAP`: thêm trường `free_slots` (các khung 30 phút trống gần nhất trong ngày) theo UC6 luồng 4a.
- Hoàn thiện các endpoint #1–#7 trong SRS Phụ lục A nếu còn thiếu: đúng mã trạng thái 200/201/400/401/403/404/409, mã lỗi (`TICKET_ALREADY_ASSIGNED`, `TECHNICIAN_NOT_ELIGIBLE`, `APPOINTMENT_OVERLAP`…), phân công/đổi/ghi log **trong một giao dịch** có khóa dòng `SELECT … FOR UPDATE` (NFR2).
- Bật CORS cho `http://localhost:5173`.

## 5. GIAI ĐOẠN 3 – FRONTEND (React + Vite) THEO ĐÚNG 3 WIREFRAME

Mở `docs/diagrams/wireframe.drawio` (3 trang) và dựng **đúng bố cục, tên cột, nút, thông báo** của từng màn hình. Các số đỏ trên wireframe chỉ là chú giải, không hiển thị trên giao diện. Văn bản thông báo ngoại lệ (EX-…) lấy nguyên văn từ wireframe.

**Cấu trúc:** `src/frontend/src/api/client.js` (một chỗ duy nhất gọi `fetch`, tự gắn token, nhận 401 → xóa token và chuyển về `/login`), `api/tickets.api.js`, `api/technicians.api.js`, `api/appointments.api.js`, `api/auth.api.js`; `components/DataState.jsx`; `components/AppointmentForm.jsx` (dùng chung M2 và M3); `pages/LoginPage.jsx`, `pages/PendingTicketsPage.jsx` (M1), `pages/AssignTechnicianPage.jsx` (M2), `pages/MyTicketsPage.jsx` (M3). **Trong `pages/` và `components/` tuyệt đối không có `fetch(`.** Hợp đồng dữ liệu (tên trường snake_case của backend) ghi bằng comment ở đầu mỗi `*.api.js`; chuyển đổi dữ liệu tại một hàm duy nhất.

**DataState** bọc mọi màn hình, có đúng 3 trạng thái với `data-testid` cố định:
- Đang tải: `state-loading`, chữ "Đang tải dữ liệu…".
- Rỗng: `state-empty`, chữ theo ngữ cảnh (M1: "Không có phiếu chờ phân công"; M3: "Chưa có phiếu được giao").
- Lỗi: `state-error`, thông báo dễ hiểu + nút "Thử lại" (`retry-button`) gọi lại API; lỗi 403 hiển thị dải đỏ theo wireframe (M1: "Bạn không có quyền xem phiếu của trung tâm này"; M3: "Bạn không phải kỹ thuật viên phụ trách phiếu này").

**M1 – Phiếu chờ phân công (Quản lý, UC1):** thanh tiêu đề (tên hệ thống, tên trung tâm); bộ lọc Nhóm sự cố, Mức ưu tiên; bảng Mã phiếu · Khách hàng · Số điện thoại (đầy đủ) · Nhóm sự cố · Mức ưu tiên · Hạn cam kết (+ nhãn "QUÁ HẠN" tính từ `due_date`, không lưu) · nút "Phân công"; phân trang 20 dòng/trang và tổng số phiếu; sắp CAO → TRUNG_BINH → THAP rồi hạn gần hơn trước (A4).
**M2 – Phân công / đổi kỹ thuật viên (Quản lý, UC2–UC4, mở UC6):** khối thông tin phiếu (mã, khách, SĐT, serial, mô tả lỗi, nhóm sự cố, ưu tiên, hạn, trạng thái, kỹ thuật viên đang phụ trách khi đổi); bảng gợi ý (Chọn · Mã · Họ tên · Bậc · Tay nghề nhóm sự cố · Khối lượng) luôn hiển thị trước khi phân công/đổi; ô "Lý do đổi" bắt buộc khi đổi; nút "Xác nhận phân công / Lưu đổi kỹ thuật viên", "Đặt lịch hẹn" (mở `AppointmentForm`), "Hủy"; bảng Lịch sử trạng thái (Thời điểm · Sự kiện · Từ → Đến · Kỹ thuật viên cũ → mới · Ghi chú); các dải EX-2a, EX-3a, EX-4a, EX-5.1, EX-5.3, EX-6a, EX-7b. Sau khi phân công thành công, trang chuyển sang chế độ "Đổi kỹ thuật viên" (đây là cách vào UC4). Cho phép truy cập trực tiếp `/tickets/:id/assign`.
**M3 – Phiếu của tôi (Kỹ thuật viên, UC5–UC7):** bảng Mã phiếu · Nhóm sự cố · Ưu tiên · Hạn cam kết (+ QUÁ HẠN) · Trạng thái · SĐT khách **dạng che**; chi tiết phiếu (khách, serial, mô tả lỗi); nút "Bắt đầu sửa" / "Thiếu linh kiện" / "Hoàn tất" + ô ghi chú ≤ 255 ký tự; biểu mẫu đặt lịch hẹn (Loại GIAO/NHẬN, Ngày, Giờ bắt đầu, Giờ kết thúc mặc định +30 phút, Ghi chú) và bảng "Lịch hẹn của phiếu" (Giờ · Loại · Trạng thái); các dải EX-6.1, EX-6.2, EX-8.1, EX-6.3, EX-6.4 (kèm các khung giờ trống bấm chọn được), EX-6.5, EX-6.6.
**Khác:** trang đăng nhập tối giản, nút đăng xuất, điều hướng theo vai trò (Quản lý → M1/M2; Kỹ thuật viên → M3; vào sai vai trò thì chuyển hướng). Hiển thị trạng thái bằng tiếng Việt có dấu, nhưng gửi/nhận mã không dấu với API. **Không thêm màn hình hay chức năng ngoài wireframe** (trừ đăng nhập/đăng xuất/điều hướng); phần cắt ghi vào thay-doi-thiet-ke.md.

## 6. GIAI ĐOẠN 4 – 18 TEST CASE + TỰ ĐỘNG CHỤP HÌNH

### 6.1 Hạ tầng kiểm thử

- Công cụ: `pytest` (+ `pytest-playwright` cho nhóm B), `Pillow` để vẽ ảnh kết quả. Thêm vào `requirements.txt`/`requirements-dev.txt`; hướng dẫn `playwright install chromium` trong README.
- **Nhóm A (TC01–TC13)** gọi trực tiếp lớp Service/Router (hoặc HTTP client của FastAPI) trên CSDL `smartcrm_test` đã nạp dữ liệu thật. Mỗi test chạy trong một giao dịch rồi **rollback** (hoặc SAVEPOINT) để độc lập và chạy lại được. Fixture tự dựng kịch bản kiểm soát được **từ bản ghi thật** (tự tìm trung tâm/nhóm sự cố phù hợp trong dữ liệu; nếu không tìm được, dừng và báo tôi chứ không bịa dữ liệu). Lưu ý: khối lượng thật của kỹ thuật viên khoảng 30 phiếu, nên fixture phải vô hiệu hóa phiếu đang giữ trong giao dịch thử khi cần khối lượng 5/2/8.
- **Nhóm B (TC14–TC18)** chạy Playwright (Chromium) vào giao diện thật (`UI_BASE_URL`, mặc định http://localhost:5173) và API thật (`API_BASE_URL`, mặc định http://localhost:8000) trên CSDL đã nạp dữ liệu thật. Mô phỏng chậm/lỗi/401 bằng `page.route`. Đọc tài khoản từ `data/processed/demo_accounts.json`. Có script `scripts/reset_demo_data.py` (hoặc cờ của seed) đưa dữ liệu về trạng thái ban đầu để chạy lại TC18 nhiều lần.
- Mỗi test gắn marker `@pytest.mark.tc("TCxx")`, hàm tên `test_tcxx_<slug>` đúng như bảng bên dưới.
- Ngày giờ trong test tính động (không hard-code): "ngày D" = ngày làm việc Thứ Hai–Thứ Bảy cách hôm nay ≥ 30 ngày, múi giờ +07:00, giờ làm việc 08:00–18:00 (A2).

### 6.2 Tự động chụp hình sau mỗi test case

- Thư mục lưu ảnh: **`docs/test-evidence/`** (tạo sẵn, commit vào Git).
- **Nhóm A:** viết `tests/evidence.py` + hook `pytest_runtest_makereport` trong `tests/conftest.py`. Mỗi test ghi lại (Given / When / Expected / Actual – lấy từ giá trị THỰC TẾ khi chạy). Ngay sau khi test kết thúc, hook vẽ một ảnh PNG (rộng ≥ 1280 px, chữ monospace, có mã TCxx, tên test, thời điểm chạy, nhãn **PASS** xanh / **FAIL** đỏ kèm traceback nếu lỗi) và lưu `docs/test-evidence/<TCxx>_<slug>.png`.
- **Nhóm B:** ngay sau khi hoàn thành test (và ở các mốc trung gian nêu ở bảng), gọi `page.screenshot(path=..., full_page=True)` lưu vào cùng thư mục. Test fail cũng phải chụp (hậu tố `_FAIL`).
- Cuối phiên chạy: sinh `docs/test-evidence/_summary.png` (bảng 18 test: mã, tên, PASS/FAIL, thời gian) và `docs/test-evidence/results.json` (mảng {id, title, type, status, duration, images[]}).
- Xóa ảnh cũ của test sắp chạy trước khi chụp lại để không lẫn ảnh cũ.

### 6.3 Danh sách 18 test case (BẮT BUỘC đúng mã, tên tệp ảnh và kỳ vọng như sau)

Có **13 test thuộc loại biên / ngoại lệ / dữ liệu sai** (TC02, TC03, TC05, TC06, TC07, TC09, TC10, TC11, TC12, TC13, TC15, TC16, TC17), trong đó 3 test biên thuần (TC05, TC06, TC10) – vượt yêu cầu tối thiểu 3.

#### Nhóm A – Kiểm thử nghiệp vụ (pytest, PostgreSQL thử nghiệm nạp dữ liệu thật)

**TC01 – Gợi ý kỹ thuật viên đúng thứ tự khối lượng công việc**  _(Loại: Luồng đúng · Truy vết: US2 · FR2 · AC2.1 · QT-08, A1, A4, A6)_
- Hàm test: `tests/service/test_suggestion.py::test_tc01_goi_y_dung_thu_tu`
- **Given:**
  - Dữ liệu thật đã nạp. Tự tìm trong dữ liệu một cặp (trung tâm A, nhóm sự cố X) có ≥ 3 kỹ thuật viên đang làm việc với tay nghề ≥ 3.
  - Tạo 1 phiếu MỚI thuộc trung tâm A, nhóm X (trong giao dịch thử, sẽ rollback).
  - Trong giao dịch thử: vô hiệu hóa các phiếu đang giữ thật của 3 kỹ thuật viên đó rồi tạo phiếu để khối lượng lần lượt là 5, 2, 8; tắt (is_active = false) các kỹ thuật viên đủ điều kiện còn lại.
- **When:**
  - Quản lý trung tâm A gọi GET /api/tickets/{ticket_id}/technician-suggestions.
- **Then (assert):**
  - HTTP 200; danh sách đúng 3 kỹ thuật viên theo thứ tự khối lượng 2 → 5 → 8.
  - Mỗi dòng có technician_code, full_name, proficiency (≥ 3) và workload.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC01_goi_y_dung_thu_tu.png`

**TC02 – Gợi ý loại bỏ kỹ thuật viên không đủ điều kiện**  _(Loại: Ngoại lệ · Truy vết: US2 · FR2 · AC2.2 · QT-08, A6)_
- Hàm test: `tests/service/test_suggestion.py::test_tc02_goi_y_loai_ktv_khong_du_dieu_kien`
- **Given:**
  - Cùng kịch bản TC01 (trung tâm A, nhóm X, phiếu MỚI).
  - Thêm trong giao dịch thử: 1 kỹ thuật viên trung tâm A có tay nghề nhóm X = 2; 1 kỹ thuật viên trung tâm B có tay nghề nhóm X = 5; 1 kỹ thuật viên trung tâm A đủ tay nghề nhưng is_active = false.
- **When:**
  - Quản lý trung tâm A mở gợi ý cho phiếu.
- **Then (assert):**
  - HTTP 200; cả 3 kỹ thuật viên nói trên KHÔNG xuất hiện trong danh sách.
  - Danh sách chỉ gồm người cùng trung tâm A, đang làm việc, tay nghề ≥ 3.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC02_goi_y_loai_ktv_khong_du_dieu_kien.png`

**TC03 – Gợi ý trả danh sách rỗng kèm lý do khi không có kỹ thuật viên phù hợp**  _(Loại: Ngoại lệ · Truy vết: US2 · FR2 · AC2.3 · QT-08)_
- Hàm test: `tests/service/test_suggestion.py::test_tc03_goi_y_rong_khong_co_ktv`
- **Given:**
  - Phiếu MỚI thuộc trung tâm A, nhóm sự cố Y.
  - Trong giao dịch thử: hạ tay nghề nhóm Y của mọi kỹ thuật viên trung tâm A xuống < 3.
- **When:**
  - Quản lý trung tâm A mở gợi ý cho phiếu.
- **Then (assert):**
  - HTTP 200 (không phải lỗi); suggestions là danh sách rỗng.
  - Có trường message nêu rõ lý do (không có người cùng trung tâm đủ tay nghề ≥ 3).
  - Phiếu vẫn ở trạng thái MOI, không có kỹ thuật viên.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC03_goi_y_rong_khong_co_ktv.png`

**TC04 – Phân công kỹ thuật viên thành công và ghi lịch sử trạng thái**  _(Loại: Luồng đúng · Truy vết: US3 · FR3, FR8 · AC3.1 · QT-06, QT-07, QT-08)_
- Hàm test: `tests/service/test_assignment.py::test_tc04_phan_cong_thanh_cong`
- **Given:**
  - Phiếu MỚI thuộc trung tâm A, nhóm X, chưa có kỹ thuật viên.
  - Kỹ thuật viên P đứng đầu danh sách gợi ý (cùng trung tâm, tay nghề ≥ 3, đang làm việc).
  - Ghi nhận trước số dòng ticket_status_log của phiếu.
- **When:**
  - Quản lý trung tâm A gọi POST /api/tickets/{ticket_id}/assignment với {"technician_id": P}.
- **Then (assert):**
  - HTTP 201; phản hồi có status = DA_PHAN_CONG, technician_id = P, assigned_by, assigned_at.
  - Trong CSDL: ticket.status = DA_PHAN_CONG và ticket.technician_id = P.
  - ticket_status_log tăng đúng 1 dòng: event_type = TRANG_THAI, from_status = MOI, to_status = DA_PHAN_CONG, to_technician_id = P, có changed_by và changed_at.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC04_phan_cong_thanh_cong.png`

**TC05 – Biên: kỹ thuật viên có tay nghề đúng bằng 3 được phân công**  _(Loại: Biên · Truy vết: US3 · FR3 · QT-08)_
- Hàm test: `tests/service/test_assignment.py::test_tc05_bien_tay_nghe_bang_3`
- **Given:**
  - Phiếu MỚI thuộc trung tâm A, nhóm X.
  - Kỹ thuật viên Q cùng trung tâm A, đang làm việc, tay nghề nhóm X đặt đúng = 3 (trong giao dịch thử).
- **When:**
  - Quản lý trung tâm A phân công Q cho phiếu.
- **Then (assert):**
  - HTTP 201; phiếu chuyển sang DA_PHAN_CONG với technician_id = Q (ngưỡng ≥ 3 là ngưỡng đóng, giá trị 3 hợp lệ).
- **Ảnh lưu vào `docs/test-evidence/`:** `TC05_bien_tay_nghe_bang_3.png`

**TC06 – Biên: kỹ thuật viên có tay nghề bằng 2 bị từ chối**  _(Loại: Biên · Truy vết: US3 · FR3 · AC3.2 · QT-08)_
- Hàm test: `tests/service/test_assignment.py::test_tc06_bien_tay_nghe_bang_2`
- **Given:**
  - Phiếu MỚI thuộc trung tâm A, nhóm X.
  - Kỹ thuật viên R cùng trung tâm A, đang làm việc, tay nghề nhóm X = 2.
  - Ghi nhận trước số dòng ticket_status_log.
- **When:**
  - Quản lý trung tâm A gửi yêu cầu phân công R cho phiếu.
- **Then (assert):**
  - HTTP 400, mã lỗi TECHNICIAN_NOT_ELIGIBLE, message nêu rõ tay nghề < 3.
  - Phiếu vẫn status = MOI, technician_id = NULL; ticket_status_log không tăng dòng nào.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC06_bien_tay_nghe_bang_2.png`

**TC07 – Từ chối phân công khi phiếu đã được phân công**  _(Loại: Ngoại lệ · Truy vết: US3 · FR3 · AC3.3 · QT-06, QT-07, NFR2)_
- Hàm test: `tests/service/test_assignment.py::test_tc07_phan_cong_phieu_da_co_ktv`
- **Given:**
  - Phiếu đã được phân công cho kỹ thuật viên P (status DA_PHAN_CONG) qua đúng nghiệp vụ.
  - Kỹ thuật viên Q khác, đủ điều kiện, cùng trung tâm.
- **When:**
  - Một quản lý khác của cùng trung tâm gọi POST /assignment với technician_id = Q cho cùng phiếu.
- **Then (assert):**
  - HTTP 409, mã lỗi TICKET_ALREADY_ASSIGNED, message có mã kỹ thuật viên hiện tại (P).
  - Phiếu vẫn technician_id = P; ticket_status_log không tăng thêm dòng.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC07_phan_cong_phieu_da_co_ktv.png`

**TC08 – Đặt lịch hẹn giao/nhận thiết bị hợp lệ**  _(Loại: Luồng đúng · Truy vết: US6 · FR6 · AC6.1 · A2, QT-13)_
- Hàm test: `tests/service/test_appointment.py::test_tc08_dat_lich_hop_le`
- **Given:**
  - Phiếu đã gán kỹ thuật viên K (DA_PHAN_CONG); K chưa có lịch nào vào ngày làm việc D (Thứ Hai–Thứ Bảy, cách hôm nay ≥ 30 ngày để không đụng lịch hẹn mẫu).
- **When:**
  - Kỹ thuật viên K (hoặc Quản lý) gọi POST /api/appointments với appointment_type = NHAN, 09:00–09:30 ngày D.
- **Then (assert):**
  - HTTP 201; phản hồi có status = DA_HEN, technician_id = K, appointment_type = NHAN, start_at/end_at đúng khung 09:00–09:30.
  - Lịch hẹn xuất hiện trong danh sách lịch hẹn của phiếu và của K.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC08_dat_lich_hop_le.png`

**TC09 – Từ chối đặt lịch hẹn trùng khung giờ**  _(Loại: Ngoại lệ · Truy vết: US6 · FR7 · AC6.2 · A3, NFR2)_
- Hàm test: `tests/service/test_appointment.py::test_tc09_dat_lich_trung`
- **Given:**
  - Kỹ thuật viên K đã có lịch hẹn DA_HEN 09:00–09:30 vào ngày làm việc D (Thứ Hai–Thứ Bảy, cách hôm nay ≥ 30 ngày để không đụng lịch hẹn mẫu).
  - Ghi nhận trước số dòng bảng appointment.
- **When:**
  - Đặt thêm lịch hẹn cho K khung 09:15–09:45 cùng ngày.
- **Then (assert):**
  - HTTP 409, mã lỗi APPOINTMENT_OVERLAP.
  - Trường conflicts liệt kê lịch bị trùng (appointment_id, ticket_code, start_at, end_at).
  - Số dòng bảng appointment không đổi (không lưu lịch mới).
- **Ảnh lưu vào `docs/test-evidence/`:** `TC09_dat_lich_trung.png`

**TC10 – Biên: lịch hẹn liền kề (kết thúc = bắt đầu) không bị coi là trùng**  _(Loại: Biên · Truy vết: US6 · FR7 · A3)_
- Hàm test: `tests/service/test_appointment.py::test_tc10_bien_lich_lien_ke`
- **Given:**
  - Kỹ thuật viên K đã có lịch DA_HEN 09:00–09:30 vào ngày làm việc D (Thứ Hai–Thứ Bảy, cách hôm nay ≥ 30 ngày để không đụng lịch hẹn mẫu).
- **When:**
  - Đặt thêm lịch hẹn cho K khung 09:30–10:00 cùng ngày.
- **Then (assert):**
  - HTTP 201; lịch mới được lưu (khoảng nửa mở [start, end) nên không giao nhau).
  - K có đúng 2 lịch DA_HEN trong ngày D; ràng buộc EXCLUDE của CSDL không báo lỗi.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC10_bien_lich_lien_ke.png`

**TC11 – Từ chối chuyển trạng thái lùi, nhảy bước hoặc giá trị không hợp lệ**  _(Loại: Ngoại lệ · Truy vết: US7 · FR8 · QT-06)_
- Hàm test: `tests/service/test_status.py::test_tc11_chuyen_trang_thai_lui`
- **Given:**
  - Kỹ thuật viên K có phiếu T1 ở trạng thái HOAN_TAT và phiếu T2 ở trạng thái DA_PHAN_CONG.
  - Ghi nhận trước số dòng ticket_status_log của T1, T2.
- **When:**
  - (a) K gọi PATCH /api/tickets/{T1}/status với to_status = DANG_XU_LY (lùi).
  - (b) K gọi PATCH /api/tickets/{T2}/status với to_status = HOAN_TAT (nhảy bước).
  - (c) K gọi PATCH /api/tickets/{T2}/status với to_status = "ABC".
- **Then (assert):**
  - (a) và (b): HTTP 409; trạng thái phiếu giữ nguyên; log không tăng.
  - (c): HTTP 400 (giá trị trạng thái không hợp lệ); T2 vẫn DA_PHAN_CONG.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC11_chuyen_trang_thai_lui.png`

**TC12 – Đổi kỹ thuật viên: bắt buộc có lý do, lý do rỗng bị từ chối**  _(Loại: Dữ liệu sai · Truy vết: US4 · FR4 · QT-07 · EX-5.1)_
- Hàm test: `tests/service/test_assignment.py::test_tc12_doi_ktv_thieu_ly_do`
- **Given:**
  - Phiếu DA_PHAN_CONG đang gán cho kỹ thuật viên K1; kỹ thuật viên K2 đủ điều kiện cùng trung tâm.
  - Ghi nhận trước số dòng ticket_status_log.
- **When:**
  - (a) Quản lý gọi PUT /api/tickets/{id}/assignment với technician_id = K2, reason = "".
  - (b) Như (a) nhưng reason = "   " (chỉ khoảng trắng).
  - (c) Như (a) nhưng reason = "Kỹ thuật viên cũ nghỉ phép".
- **Then (assert):**
  - (a) và (b): HTTP 400; phiếu vẫn thuộc K1; log không tăng.
  - (c): HTTP 200; phiếu chuyển sang K2, trạng thái phiếu không lùi; log tăng đúng 1 dòng event_type = DOI_KTV, from_technician_id = K1, to_technician_id = K2, note = lý do.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC12_doi_ktv_thieu_ly_do.png`

**TC13 – Che số điện thoại và phân quyền theo vai trò**  _(Loại: Ngoại lệ · Truy vết: US5 · FR5 · QT-14, QT-15 · NFR3)_
- Hàm test: `tests/service/test_access.py::test_tc13_che_so_dien_thoai_va_phan_quyen`
- **Given:**
  - Phiếu T1 gán cho kỹ thuật viên K, khách có số điện thoại 10 chữ số; phiếu T2 gán cho kỹ thuật viên K' khác.
  - Có Quản lý trung tâm của trung tâm chứa T1.
- **When:**
  - (a) K gọi GET /api/technicians/me/tickets.
  - (b) Quản lý gọi GET /api/tickets/{T1} (hoặc danh sách phiếu).
  - (c) K gọi GET /api/tickets/{T2}.
- **Then (assert):**
  - (a) Số điện thoại dạng che 3 số đầu + **** + 3 số cuối (ví dụ 090****456); 0 phiếu của người khác trong phản hồi.
  - (b) Số điện thoại hiển thị đầy đủ cho Quản lý.
  - (c) HTTP 403.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC13_che_so_dien_thoai_va_phan_quyen.png`

#### Nhóm B – Kiểm thử giao diện và end-to-end (pytest + Playwright, dữ liệu thật)

**TC14 – Giao diện M1: trạng thái đang tải**  _(Loại: Luồng đúng · Truy vết: US1 · FR1 · yêu cầu 3 trạng thái (Buổi 10))_
- Hàm test: `tests/ui/test_states.py::test_tc14_ui_trang_thai_dang_tai`
- **Given:**
  - Đăng nhập bằng Quản lý của trung tâm có phiếu MỚI (dữ liệu thật).
  - Playwright làm chậm phản hồi GET /api/tickets 3 giây.
- **When:**
  - Mở màn hình M1 – Phiếu chờ phân công.
- **Then (assert):**
  - Trong lúc chờ thấy vùng [data-testid=state-loading] với chữ "Đang tải dữ liệu…"; chụp ảnh đúng lúc này.
  - Sau khi dữ liệu về: vùng đang tải biến mất, bảng hiển thị ≥ 1 dòng phiếu thật.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC14_ui_trang_thai_dang_tai.png`

**TC15 – Giao diện M1: trạng thái rỗng (không có phiếu chờ phân công)**  _(Loại: Ngoại lệ · Truy vết: US1 · FR1 · EX-1.1)_
- Hàm test: `tests/ui/test_states.py::test_tc15_ui_trang_thai_rong`
- **Given:**
  - Đăng nhập bằng Quản lý của trung tâm không có phiếu MỚI nào (script nạp dữ liệu cố ý chừa 1 trung tâm).
- **When:**
  - Mở màn hình M1.
- **Then (assert):**
  - Hiển thị vùng [data-testid=state-empty] với chữ "Không có phiếu chờ phân công".
  - Không có vùng lỗi [data-testid=state-error]; không hiển thị thông báo đỏ.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC15_ui_trang_thai_rong.png`

**TC16 – Giao diện M1: trạng thái lỗi và nút Thử lại**  _(Loại: Ngoại lệ · Truy vết: US1 · FR1 · NFR2 · EX-7b)_
- Hàm test: `tests/ui/test_states.py::test_tc16_ui_trang_thai_loi`
- **Given:**
  - Đăng nhập Quản lý của trung tâm có phiếu MỚI.
  - Playwright chặn (abort) GET /api/tickets để mô phỏng backend không phản hồi.
- **When:**
  - Mở M1; sau đó bỏ chặn và bấm nút "Thử lại".
- **Then (assert):**
  - Hiển thị vùng [data-testid=state-error] có thông báo lỗi dễ hiểu và nút "Thử lại" ([data-testid=retry-button]); chụp ảnh 1.
  - Sau khi bỏ chặn và bấm Thử lại: bảng phiếu thật hiển thị; chụp ảnh 2.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC16_ui_trang_thai_loi_1_loi.png`, `TC16_ui_trang_thai_loi_2_thu_lai.png`

**TC17 – Giao diện: xử lý 401 (hết phiên) và đăng nhập sai**  _(Loại: Ngoại lệ · Truy vết: NFR3 · yêu cầu đăng nhập và 401 (Buổi 10))_
- Hàm test: `tests/ui/test_states.py::test_tc17_ui_het_phien_dang_nhap_401`
- **Given:**
  - Đang đăng nhập (có token trong trình duyệt).
  - Playwright cho GET /api/tickets trả HTTP 401.
- **When:**
  - (a) Mở M1 khi API trả 401.
  - (b) Tại trang đăng nhập, nhập sai mật khẩu.
- **Then (assert):**
  - (a) Token bị xóa khỏi bộ nhớ trình duyệt và giao diện chuyển về trang đăng nhập; chụp ảnh 1.
  - (b) Trang đăng nhập hiển thị thông báo lỗi "Sai tên đăng nhập hoặc mật khẩu", không bị lặp chuyển trang; chụp ảnh 2.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC17_ui_het_phien_dang_nhap_401_1_ve_dang_nhap.png`, `TC17_ui_het_phien_dang_nhap_401_2_sai_mat_khau.png`

**TC18 – End-to-end luồng chính: phân công → đặt lịch hẹn → cập nhật trạng thái đến HOÀN TẤT**  _(Loại: Luồng đúng · Truy vết: US1–US7 · FR1–FR8 · UC1–UC7 · NFR4)_
- Hàm test: `tests/ui/test_e2e_main_flow.py::test_tc18_ui_e2e_luong_chinh`
- **Given:**
  - Dữ liệu thật đã nạp; đã chạy bước tạo phiếu MỚI; có Quản lý và kỹ thuật viên phù hợp (tài khoản trong data/processed/demo_accounts.json).
- **When:**
  - b1: Quản lý đăng nhập, mở M1.
  - b2: Bấm "Phân công" ở dòng phiếu đầu tiên, mở M2 và xem danh sách gợi ý.
  - b3: Chọn kỹ thuật viên đầu danh sách, bấm "Xác nhận phân công".
  - b4: Bấm "Đặt lịch hẹn", chọn loại, ngày D, 09:00–09:30, bấm "Lưu lịch hẹn".
  - b5: Đăng xuất, đăng nhập bằng kỹ thuật viên vừa được phân công, mở M3.
  - b6: Chọn phiếu, bấm "Bắt đầu sửa".
  - b7: Bấm "Hoàn tất".
- **Then (assert):**
  - b1: M1 chỉ có phiếu MỚI của trung tâm, sắp CAO → TRUNG_BINH → THAP.
  - b2: M2 hiển thị thông tin phiếu và bảng gợi ý (tay nghề ≥ 3, khối lượng tăng dần).
  - b3: Thông báo thành công; trạng thái phiếu ĐÃ PHÂN CÔNG; bảng lịch sử thêm 1 dòng.
  - b4: Lịch hẹn lưu thành công, hiển thị với trạng thái ĐÃ HẸN.
  - b5: M3 của kỹ thuật viên có phiếu vừa nhận, số điện thoại dạng che.
  - b6: Trạng thái ĐANG XỬ LÝ. b7: Trạng thái HOÀN TẤT.
  - Kiểm CSDL cuối luồng: ticket.status = HOAN_TAT; ticket_status_log có đủ MOI → DA_PHAN_CONG → DANG_XU_LY → HOAN_TAT; có 1 lịch hẹn DA_HEN.
- **Ảnh lưu vào `docs/test-evidence/`:** `TC18_ui_e2e_luong_chinh_b1_danh_sach_M1.png`, `TC18_ui_e2e_luong_chinh_b2_goi_y_M2.png`, `TC18_ui_e2e_luong_chinh_b3_phan_cong_xong.png`, `TC18_ui_e2e_luong_chinh_b4_dat_lich_xong.png`, `TC18_ui_e2e_luong_chinh_b5_phieu_cua_toi_M3.png`, `TC18_ui_e2e_luong_chinh_b6_dang_xu_ly.png`, `TC18_ui_e2e_luong_chinh_b7_hoan_tat.png`

### 6.4 Lệnh chạy kiểm thử (phải có trong README)

```
pytest tests/service -v          # Nhóm A (TC01–TC13)
pytest tests/ui -v               # Nhóm B (TC14–TC18) – cần backend + frontend đang chạy
pytest -v                        # toàn bộ 18 test, kết thúc in "18 passed"
```

## 7. GIAI ĐOẠN 5 – TÍCH HỢP VÀ TỰ KIỂM

Làm theo 6 bước của Buổi 10: viết luồng chính bằng lời → chạy thử từng bước riêng → ghép tăng dần → phân loại lỗi (hợp đồng dữ liệu hay logic) → chạy toàn luồng trên dữ liệu thật → chụp ảnh. Sau đó tự kiểm và báo cáo từng mục:

1. Module mở rộng (frontend) chạy được. 2. Luồng chính end-to-end không treo (TC18). 3. Đã chạy trên dữ liệu thật (nêu số dòng đã nạp). 4. Có ảnh trong `docs/test-evidence/`. 5. `pytest -v` báo **18 passed**. 6. Có test biên/ngoại lệ. 7. Ba trạng thái đang tải/rỗng/lỗi hoạt động (TC14–TC16). 8. README đủ bước chạy. 9. **Đã thử clone vào thư mục mới** (ví dụ `git clone <repo> /tmp/clean-check`) và chạy đúng theo README từ đầu đến khi `pytest -v` xanh; ghi lại bước nào thiếu rồi sửa README. 10. Số commit ≥ 8 và đúng quy ước.
Chạy thêm: `grep -rn "fetch(" src/frontend/src/pages src/frontend/src/components` phải rỗng; tắt backend → M1 hiện lỗi + nút Thử lại.

## 8. GIAI ĐOẠN 6 – TÀI LIỆU, README, COMMIT, GITHUB

**`docs/thay-doi-thiet-ke.md`:** nối tiếp vào cuối file theo mẫu TD-xx (Phản hồi – Quyết định SỬA/GIỮ – Lý do – Ảnh hưởng): ghi các endpoint bổ sung ở mục 4, cơ chế tài khoản demo không thêm bảng, quy tắc ánh xạ/loại dòng khi nạp dữ liệu, và mọi phần đã cắt khỏi giao diện (ví dụ UC8, hủy lịch hẹn trên UI) kèm lý do.

**`README.md` – cập nhật sau Buổi 10, giữ đánh số mục hiện có của repo, viết bằng tiếng Việt, cụ thể từng lệnh (mỗi bước một lệnh, ghi rõ chạy ở thư mục nào, hệ điều hành Windows/macOS/Linux), gồm tối thiểu:**
1. Mô tả bài toán, phạm vi (làm / không làm), công nghệ, cấu trúc thư mục.
2. Yêu cầu môi trường: Python 3.11+, Node.js LTS, PostgreSQL 16 hoặc Docker Desktop, Git, trình duyệt Chromium (Playwright); biến môi trường (xem `.env.example`).
3. **Các bước dựng hệ thống – cách 1: Docker Compose (2 lệnh)**; **cách 2: chạy thủ công** (tạo venv và cài thư viện, tạo CSDL `smartcrm` và `smartcrm_test`, áp dụng `db/schema.sql`, đặt dữ liệu CSV vào `data/raw/`, chạy `scripts/seed_real_data.py`, chạy backend uvicorn, chạy frontend `npm install` + `npm run dev`).
4. Cách đăng nhập demo (tài khoản lấy ở đâu, biến `DEMO_PASSWORD`), địa chỉ Swagger `/docs` và giao diện.
5. Cách chạy kiểm thử (3 lệnh ở 6.4), vị trí ảnh `docs/test-evidence/`, cách chạy lại khi dữ liệu đã bị thay đổi (reset).
6. Cách chạy lại trên dữ liệu mẫu nhỏ `data/sample/`, ghi seed đã dùng (`20261023`) và nơi tải bộ CSV đầy đủ.
7. Trạng thái hiện tại (tick từng hạng mục: 18/18 test, 3 màn hình, 3 trạng thái, hạng mục chưa làm), lỗi thường gặp và cách xử lý, khai báo sử dụng công cụ AI (có Copilot).

**Commit & đẩy lên GitHub** (theo quy ước nhánh của repo: `main` ổn định, `dev` làm việc, `feature/<tên>`):
- Làm trên các nhánh `feature/seed-data`, `feature/auth-api`, `feature/frontend`, `feature/tests-evidence`, gộp vào `dev`.
- Gợi ý chuỗi commit: `chore: add real data seed script` → `feat: add auth endpoints and ticket detail api` → `feat: add api client and DataState component` → `feat: build M1 pending tickets page` → `feat: build M2 assignment page` → `feat: build M3 my tickets and appointment form` → `test: add service tests with evidence capture` → `test: add ui and e2e tests with screenshots` → `docs: update README and design change log for lab 10`.
- Kiểm tra `git status` không chứa `.env` hay CSV lớn; ảnh trong `docs/test-evidence/` được commit.
- `git push origin dev`. Chỉ khi **cả 18 test PASS và đã kiểm clone sạch**, gộp `dev` vào `main` và `git push origin main`.

## 9. BÁO CÁO CUỐI CÙNG (trả lời cho tôi theo đúng khuôn)

1. Bảng 18 test: Mã · Tên · PASS/FAIL · Thời gian chạy · Tên tệp ảnh. Kèm dòng cuối của `pytest -v` (ví dụ "18 passed in …s").
2. Số liệu nạp dữ liệu thật: từng bảng (nguồn → nạp → bị loại), seed đã dùng, trung tâm bị chừa trống, tài khoản dùng cho TC18.
3. Danh sách commit (mã băm, thông điệp), tên nhánh, đường dẫn repo.
4. Mọi chỗ đã sửa mã vì test fail, mọi quyết định cần tôi xác nhận, mọi mâu thuẫn tài liệu (ví dụ thông báo EX-8.1 trong wireframe nêu lùi từ ĐANG XỬ LÝ về ĐÃ PHÂN CÔNG, trong khi hợp đồng API chỉ nhận to_status ∈ {DANG_XU_LY, CHO_LINH_KIEN, HOAN_TAT}; hãy làm theo hợp đồng API và hiển thị thông báo dạng "Không thể chuyển từ X về Y").
5. Kết quả bước kiểm clone sạch theo README.