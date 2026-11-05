# Tích hợp luồng chính end-to-end – Buổi 10

Tài liệu ghi lại cách ghép các module thành luồng chính L04, các chỗ đứt gãy đã gặp và kết quả chạy toàn luồng trên dữ liệu thật. Ảnh minh chứng nằm ở [docs/test-evidence/](test-evidence/).

## 1. Luồng chính (dùng lại use case BT1)

| Bước | Use case | Ai làm | Màn hình | API |
|---|---|---|---|---|
| 1 | Đăng nhập | Quản lý | Đăng nhập | `POST /api/auth/login`, `GET /api/auth/me` |
| 2 | UC1 – Xem phiếu chờ phân công | Quản lý | M1 | `GET /api/tickets?status=MOI` |
| 3 | UC2 – Gợi ý kỹ thuật viên | Quản lý | M2 | `GET /api/tickets/{id}`, `GET /api/tickets/{id}/technician-suggestions` |
| 4 | UC3 – Phân công | Quản lý | M2 | `POST /api/tickets/{id}/assignment` |
| 5 | UC6 – Đặt lịch giao/nhận | Quản lý | M2 | `POST /api/appointments` |
| 6 | UC5 – Xem phiếu của tôi | Kỹ thuật viên | M3 | `GET /api/technicians/me/tickets`, `GET /api/tickets/{id}/appointments` |
| 7 | UC7 – Cập nhật trạng thái đến HOÀN TẤT | Kỹ thuật viên | M3 | `PATCH /api/tickets/{id}/status` |

Điểm bắt đầu: phiếu `MOI` chưa có kỹ thuật viên. Điểm kết thúc: phiếu `HOAN_TAT`, có lịch hẹn `DA_HEN` và đủ lịch sử trạng thái.

## 2. Ghép tăng dần

1. **Từng bước riêng lẻ:** nạp dữ liệu (`scripts/load_*.py`) đối chiếu số dòng; mỗi endpoint kiểm bằng unit test (TestClient) và integration TC22–TC25 trên PostgreSQL; mỗi màn hình kiểm bằng test UI TC19–TC21 với API giả lập.
2. **Ghép frontend ↔ backend:** đăng nhập + M1 trên backend thật.
3. **Ghép thêm M2:** gợi ý → phân công → đặt lịch, đối chiếu bằng SQL.
4. **Ghép thêm M3:** đăng nhập kỹ thuật viên được phân công → cập nhật trạng thái.
5. **Toàn luồng:** `tests/e2e/test_main_flow.py` chạy một lần từ bước 1 đến 7, không can thiệp tay.

## 3. Chỗ đứt gãy đã gặp và cách xử lý

| # | Triệu chứng | Loại lỗi | Nguyên nhân | Xử lý |
|---|---|---|---|---|
| 1 | M3 hiện mã thô `DA_DONG` trong cột Trạng thái | Hợp đồng dữ liệu | Backend trả đủ 7 mã trạng thái, frontend chỉ có nhãn cho 4 mã | Bổ sung nhãn cho mọi mã (`MyTicketsPage.jsx`) |
| 2 | M3 của KT033 dài 437 dòng (≈ 20.000 px), phiếu cần làm bị chìm | Logic / ý nghĩa | Dữ liệu thật: mỗi KTV giữ trung bình 192, tối đa 443 phiếu, phần lớn `DA_DONG`; màn hình không có cách lọc | Thêm ô lọc "Trạng thái" (mặc định Tất cả). Không ẩn phiếu đã đóng/đã hủy vì KTV vẫn có quyền xem phiếu của chính mình – TD-13 |
| 3 | pytest dừng với `INTERNALERROR UnicodeEncodeError` khi tên test có tiếng Việt | Logic (môi trường) | Hook in kết quả dùng `print` trên stdout cp1252 (pipe của Git Bash) | Mã hoá an toàn trong `tests/conftest.py` |
| 4 | TC21 (UI giả lập) báo `strict mode violation` sau khi thêm bộ lọc | Test | Locator `get_by_text("HOÀN TẤT")` không phân biệt hoa thường, khớp cả `<option>Hoàn tất</option>` | Đổi sang ô bảng khớp chính xác, giữ nguyên ý nghĩa kiểm tra |
| 5 | M2: đặt lịch thành công chỉ đóng form, không có thông báo | Logic (giao diện) | Form không trả lịch vừa tạo cho trang cha | Form trả lịch API vừa tạo; M2 hiện "Đã đặt lịch GIAO lúc 08:00–08:30 ngày …" (E2E_06b) |
| 6 | M3: chọn phiếu hoặc đổi trạng thái làm cả danh sách nhấp nháy "Đang tải dữ liệu…" | Logic (giao diện) | `load` phụ thuộc `selected`, mỗi lần chọn phiếu tải lại và bật trạng thái đang tải | `load` không phụ thuộc `selected`; đổi trạng thái làm mới ngầm. Test e2e theo dõi DOM bằng `MutationObserver` và fail nếu trạng thái đang tải xuất hiện (đã thử: hành vi cũ làm test fail) |
| 7 | M3 hiển thị mức ưu tiên dạng mã `TRUNG_BINH`, M1 hiển thị `TRUNG BÌNH` | Hợp đồng dữ liệu | Nhãn chỉ khai báo trong M1 | Nhãn dùng chung `src/frontend/src/labels.js` cho M1, M2, M3 |
| 8 | Đối chiếu kỳ vọng TC18 (b3, b4, b7) và TC12: M2 không báo phân công/đổi KTV thành công, không có bảng lịch hẹn, lịch sử hiện mã `DOI_KTV`; M3 không báo đổi trạng thái | Hợp đồng dữ liệu (nhãn) và giao diện | Màn hình chưa hiển thị đủ kết quả mà đặc tả kiểm thử yêu cầu | Thêm thông báo thành công ở M2/M3, bảng "Lịch hẹn của phiếu" ở M2, nhãn "ĐỔI KỸ THUẬT VIÊN"; kiểm chứng bằng TC12, TC18 |

## 4. Chạy toàn luồng trên dữ liệu thật

**Dữ liệu:** database `smartcrm_test` nạp từ CSV case-study (6 trung tâm, 38 KTV, 159 tay nghề, 7.317 phiếu, 35.719 log, 300 lịch hẹn). Test tạo lại `smartcrm_work_test` từ đó và chạy backend trên bản này, nên `smartcrm` và `smartcrm_test` không bị ghi.

**Lệnh** (frontend đang chạy ở cổng 5173, cổng 8000 trống):

```powershell
$env:TEST_DB_NAME = "smartcrm_test"
python -m pytest tests\e2e -m e2e
```

**Đầu vào và đầu ra quan sát được** (lần chạy 06/11/2026, `1 passed`, ~24 giây):

| Bước | Đầu vào | Đầu ra quan sát được | Ảnh |
|---|---|---|---|
| 1–2 | `QL_TT01` (TTBH Quận 10) | 5 phiếu MOI, sắp theo ưu tiên/hạn; đầu danh sách `BH-005310/2025` (MAN_HINH, CAO) | E2E_01 |
| – | Lọc nhóm sự cố không có phiếu | "Không có phiếu chờ phân công" | E2E_02 |
| – | Tắt backend, đổi bộ lọc | "Không thể kết nối máy chủ. Vui lòng thử lại." + nút Thử lại; bật lại, bấm Thử lại → danh sách trở lại | E2E_03 |
| 3 | Mở `BH-005310/2025` | 2 gợi ý: KT033 (tay nghề 5, khối lượng 61), KT020 (5, 76) | E2E_04 |
| 4 | Chọn KT033, Xác nhận phân công | Trạng thái ĐÃ PHÂN CÔNG; log `MOI → DA_PHAN_CONG`; SQL xác nhận `ticket.technician_id` = KT033 | E2E_05 |
| 5 | GIAO, khung trống đầu tiên của KT033 ngày 11/12/2026 08:00–08:30 | Thông báo "Đã đặt lịch GIAO lúc 08:00–08:30 ngày 11/12/2026."; SQL: 1 lịch `GIAO`/`DA_HEN` đúng giờ | E2E_06, E2E_06b |
| 6 | `KT033`, lọc "Đang làm" | Thấy phiếu và lịch hẹn ĐÃ HẸN; SĐT khách bị che | E2E_07 |
| 7 | Ghi chú "Đã kiểm tra thiết bị", Bắt đầu sửa → Hoàn tất | Phiếu HOÀN TẤT, nút Đặt lịch ẩn; SQL: log `DA_PHAN_CONG → DANG_XU_LY` (có ghi chú) và `DANG_XU_LY → HOAN_TAT` | E2E_08 |
| – | Lọc "Đã đóng" | 359 / 437 phiếu, đúng bằng số phiếu `DA_DONG` của KT033 trong DB | E2E_09 |
| – | Token không hợp lệ | API trả 401 → token bị xoá, về trang đăng nhập | E2E_10 |

Tên phiếu, kỹ thuật viên và khung giờ được test chọn từ dữ liệu thật ở mỗi lần chạy, nên có thể khác bảng trên nếu dữ liệu nguồn thay đổi.

## 5. Thử clone mới và chạy theo README

Ngày 06/11/2026: clone repo vào một thư mục trống, làm đúng từng lệnh README mục 3.1 (Windows PowerShell, venv mới, `npm ci` mới, bộ 7 CSV từ LMS). Khác biệt duy nhất: dùng database `smartcrm_clone`/`smartcrm_clone_test` để không ghi đè database đang có.

| Bước README | Kết quả |
|---|---|
| 1–9 (clone, `.env`, venv, thư viện, Chromium, chép CSV) | Lần đầu **lỗi** ở bước 9: thư mục `data/raw/` không có trong bản clone vì bị `.gitignore` bỏ cả thư mục → sửa bằng `data/raw/.gitkeep`; lần hai chạy được |
| 10–15 (tạo DB, migrate, nạp dữ liệu) | Đúng 6 / 38 / 159 / 7.317 / 35.719 / 300 dòng; bất biến đều 0; chạy lại các loader không nhân đôi dòng |
| 16 (tài khoản demo) | 41 tài khoản (không có 3 KTV đã nghỉ) → **sửa README** mục 4 vốn ghi `KT001 … KT038` |
| 17–22 (database kiểm thử) | Số dòng giống database chính |
| 23–26 (backend, frontend) | `QL_TT01`, `KT033` đăng nhập được; `KT001` (đã nghỉ) bị 401 |
| Mục 5: unit / UI / integration / e2e | 65 passed / 3 passed / 4 passed / 1 passed |

Lần đầu bản clone được lấy từ repo cục bộ. Sau khi push, lặp lại từ GitHub (commit `3b5fe4b`, đúng URL trong README):

| Bước | Kết quả |
|---|---|
| 1–23 | Như trên: đủ 6 bảng ở hai database, 41 tài khoản |
| Mục 5 lần đầu | **Lỗi** `DLL load failed ... The filename or extension is too long`: thư mục clone dài 174 ký tự, tệp sâu nhất trong `.venv` vượt 260 ký tự → thêm lưu ý "clone vào đường dẫn ngắn" ở README mục 3 |
| Mục 5, clone lại vào đường dẫn 97 ký tự | unit 65 passed, UI 3 passed, integration 4 passed, e2e 1 passed |
| Mục 3.3 Docker Compose (trên repo gốc) | Container chạy, migration tự áp dụng; nạp đủ 6 bảng qua cổng 5433; đăng nhập `QL_TT01` trên giao diện thấy 5 phiếu MOI. Bước sinh tài khoản từ chối ghi đè tệp đã có → README ghi rõ bỏ qua bước này nếu đã có tệp |
