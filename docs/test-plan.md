# Test Plan rút gọn – Smart CRM L04 (BT3)

Sinh viên: Nguyễn Quốc Việt – MSSV 2374802010556 · Track SE · Luồng L04 Phân công kỹ thuật viên và lịch hẹn
Kết quả chạy: [test-report.md](test-report.md) · Bug Log: [bug-log.md](bug-log.md)

## 1. Phạm vi và phần chủ ý KHÔNG kiểm

**Kiểm:** các quy tắc nghiệp vụ đã hiện thực của L04 qua API thật trên dữ liệu case-study thật:
gợi ý kỹ thuật viên (FR2, QT-08), phân công và đổi kỹ thuật viên (FR3, FR4, QT-07), đặt lịch hẹn và
chống trùng (FR6, FR7), vòng đời trạng thái (FR8, QT-06), tạo/sửa phiếu (QT-02), phân quyền theo trung
tâm/kỹ thuật viên (QT-14), che số điện thoại (QT-15), hợp đồng lỗi của API (400/401/403/404/409, không 500),
năm mục OWASP mức nhận biết (A01, A02, A04, A05, A07) và tính tái lập của bước dựng CSDL.

**Chủ ý KHÔNG kiểm (và lý do):**

| Không kiểm | Lý do |
|---|---|
| Hiệu năng, tải đồng thời lớn | Prototype một người dùng; NFR hiệu năng ngoài phạm vi BT3 |
| Giao diện trên nhiều trình duyệt / thiết bị di động | Chỉ kiểm Chromium; giao diện đã có TC14–TC18 (Buổi 10) |
| UC8 báo cáo khối lượng, SMS/Zalo, tồn kho linh kiện | Ngoài phạm vi L04 (TD-05, TD-15) |
| Luồng tiếp nhận phiếu L2 đầy đủ | Ngoài phạm vi; tạo phiếu chỉ là CRUD tối giản (TD-17) |
| Rà soát bảo mật đầy đủ, kiểm thử xâm nhập | Thuộc Chuyên đề tốt nghiệp 2; BT3 chỉ kiểm năm mục OWASP bằng tay/tự động |
| A04 bằng truy vấn bảng users | Hệ thống không có bảng tài khoản (TD-02); kiểm băm mật khẩu trong `demo_accounts.json` ở [checklist bảo mật](security-checklist.md) |

**Kỹ thuật chọn dữ liệu:** phân vùng tương đương (hợp lệ / sai định dạng / sai quyền) và giá trị biên hai
bên ranh giới: tay nghề **3 | 2** (TC-04), lịch liền kề **10:00 = 10:00 | chồng 1 phút 09:01** (TC-05),
mã phiếu **không tồn tại | vượt BIGINT** (TC-08), chuỗi **có chữ | chỉ khoảng trắng** (TC-06, TC-07).

## 2. Loại test và số lượng mỗi tầng

| Tầng | Công cụ | Số lượng | Lệnh |
|---|---|---|---|
| Unit (lớp service, không CSDL) | pytest | 104 test (quy tắc phiếu, lịch hẹn, ánh xạ lỗi, xác thực) | `python -m pytest` |
| Integration (PostgreSQL thật) | pytest + TestClient | 7 test (CRUD, chạy lại không nhân đôi, TC22–TC25) | `python -m pytest tests/integration -m integration` |
| API / end-to-end (HTTP thật, Swagger, UI) | pytest + Playwright | **12 test case TC-01…TC-12 của Test Report** | `python -m pytest -m bt3` |

12 test case phủ đủ năm loại: luồng đúng (TC-01, TC-02, TC-03) · giá trị biên (TC-04, TC-05) · dữ liệu sai
(TC-06, TC-07, TC-08) · bảo mật/chất lượng dữ liệu (TC-09, TC-10, TC-11) · tái lập (TC-12). Mỗi quy tắc
nghiệp vụ đã hiện thực có ít nhất một test. TC01–TC18 của Buổi 10 (`-m system`) vẫn giữ để kiểm giao diện.

## 3. Tiêu chí thành công đo được

1. 12/12 test case đã **chạy thật**, mỗi case có kết quả thực tế cụ thể (mã HTTP, mã lỗi, đếm bản ghi
   trước/sau) và ảnh chụp trong `docs/screenshots/TC-xx*.png` (TC-12: ảnh terminal).
2. Sau khi sửa bug: `python -m pytest` (unit), `-m integration` và `-m bt3` đều **0 FAIL**.
3. Không còn bug Critical mở; mọi bug Major trở lên có commit sửa riêng và test case chạy lại PASS.
4. Mọi lỗi nghiệp vụ biết trước trả đúng 400/401/403/404/409 – **không có phản hồi 500**; phản hồi lỗi
   không chứa traceback, tên bảng hay câu SQL.
5. Bước dựng CSDL chạy lần hai cho cùng số dòng ở cả sáu bảng.

## 4. Môi trường và dữ liệu thử

| Mục | Giá trị |
|---|---|
| Máy | Windows 11, Python 3.14 (venv, `requirements-dev.txt`), Node.js 24, PostgreSQL 18, Chromium của Playwright 1.64 |
| CSDL nguồn | `smartcrm_test` = dữ liệu case-study đầy đủ (7.317 phiếu, 35.719 dòng log, 300 lịch hẹn, 38 KTV, 6 trung tâm) |
| Cô lập | Mỗi test case tạo lại `smartcrm_work_test` từ `smartcrm_test` và chạy backend riêng trên bản sao (TD-12); không ghi vào `smartcrm` |
| Tiền điều kiện | Dựng bằng SQL trên bản sao từ bản ghi thật (ví dụ khối lượng 5/2/8, tay nghề 3/2), không dựa vào dữ liệu còn sót |
| TC-12 | Bộ mẫu trong repo `data/sample` nạp vào `smartcrm_load_test` (xoá trước và sau khi chạy) |
| Tài khoản | Tài khoản demo `QL_TT01…06`, `KT002…` sinh từ `DEMO_PASSWORD` trong `.env`; token ký bằng `SECRET_KEY` |
| Cần chạy trước | `.env` có `TEST_DB_NAME=smartcrm_test`; `python scripts/setup_all.py --with-test-db`; frontend `npm run dev` (cho TC-11); cổng 8000 trống |
