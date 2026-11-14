# Khai báo sử dụng công cụ AI – luồng L04

| | |
|---|---|
| **Sinh viên** | Nguyễn Quốc Việt – MSSV 2374802010556 – Lớp 261_71ITGR40203_05 |
| **Học phần** | Chuyên đề Tốt nghiệp 1 (71ITGR40203) – Trường ĐH Văn Lang |
| **Đề tài** | Smart CRM – Mekong Mobile, luồng L04: Phân công kỹ thuật viên và lịch hẹn (track SE) |
| **Phạm vi** | BT1 (đặc tả, thiết kế), BT2 (hệ thống chạy được, tag `v0.2`) và BT3 (kiểm thử, sửa lỗi, đóng gói, tag `v1.0`) |
| **Cập nhật** | 15/11/2026 |

Nguyên tắc: mọi phần có AI hỗ trợ đều được em đọc lại, chạy lại và giải thích được; kết quả ghi trong repo là kết quả chạy thật, phần chưa làm được ghi rõ là chưa làm.

## 1. Bảng khai báo

| Công cụ | Việc AI hỗ trợ | Tệp / hàm liên quan | Cách em kiểm chứng |
|---|---|---|---|
| Claude (Anthropic, chat) | BT1: bản nháp SRS, use case, kiến trúc, ERD, wireframe; viết prompt giao việc cho Copilot | `docs/srs.md`, `docs/*.drawio`, `db/schema.sql` | Đối chiếu từng QT-xx với case study; chạy `db/schema.sql` trên PostgreSQL thật; mở từng `.drawio` kiểm tác nhân, ERD, trường dữ liệu |
| GitHub Copilot (VS Code) | Buổi 8–10: dựng giao diện M1–M3, API ban đầu, script nạp dữ liệu, sinh lịch hẹn | `src/frontend/src/**`, `scripts/load_*.py`, `scripts/gen_appointments.py` | Chạy `npm run build`; đếm số dòng 6 bảng bằng SQL; truy vấn bất biến trả 0 dòng; xem `git diff` trước khi commit |
| Claude Code (Anthropic) | Tách 3 lớp backend | `app/routers/*`, `app/services/ticket_service.py`, `appointment_service.py`, `app/repositories/*`, `app/domain/errors.py`, `app/main.py` (ánh xạ lỗi → HTTP) | Toàn bộ test cũ (18 TC, e2e, integration) vẫn pass sau khi tách; `grep` service/repository không còn mã HTTP; router không còn SQL |
| Claude Code | Quy tắc nghiệp vụ thuần và unit test 3 loại | `app/services/ticket_rules.py`, `appointment_rules.py`; `tests/test_ticket_rules.py`, `test_crud_rules.py`, `test_appointment_validation.py` | `python -m pytest` (100 passed); đọc từng test, đối chiếu QT-02, QT-06, QT-08, QT-13 trong SRS |
| Claude Code | CRUD phiếu và lịch hẹn (hủy mềm) | `ticket_service.create_ticket / update_ticket / cancel_ticket`, `appointment_service.update_appointment / cancel_appointment`, `tests/integration/test_crud.py` | Test tích hợp kiểm từng bước bằng SQL; thử lại bằng Swagger |
| Claude Code | Xử lý CSDL tắt (503) và lỗi ngoài dự kiến (500) | `app/main.py: handle_database_unavailable, handle_unexpected_error`; `tests/test_error_handling.py` | Tắt PostgreSQL thật rồi gọi API; test kiểm phản hồi không lộ lỗi thô |
| Claude Code | Bộ dữ liệu mẫu và dựng hệ thống một lệnh | `scripts/make_sample_data.py`, `scripts/data_source.py`, `scripts/setup_all.py`, `data/sample/*.csv`, `tests/integration/test_idempotent_load.py` | Chạy `setup_all.py` hai lần, số dòng không đổi; so 30 phiếu MOI của bộ mẫu trùng dữ liệu đầy đủ |
| Claude Code | 18 test case TC01–TC18 trên hệ thống thật, test e2e, ảnh minh chứng | `tests/service/*`, `tests/ui/test_states.py`, `tests/ui/test_e2e_main_flow.py`, `tests/e2e/test_main_flow.py`, `tests/real_system.py` | Chạy `python -m pytest -m system` (18 passed); mở từng ảnh trong `docs/test-evidence/`; thử phá hành vi cũ để chắc test bắt được lỗi |
| Claude Code | README, khoá phiên bản, `.env.example`, nhật ký lỗi, báo cáo | `README.md`, `requirements*.txt`, `.env.example`, `docs/bug-log.md`, `docs/thay-doi-thiet-ke.md`, báo cáo Word/PDF | Clone repo vào thư mục trống và làm đúng từng bước README; quét toàn bộ lịch sử Git không có secret |
| Claude Code | BT3: kế hoạch thực hiện từ slide Buổi 14 và tài liệu tự học Buổi 13; Test Plan; 12 test case TC-01…TC-12 chạy trên backend thật với ảnh Swagger | `docs/test-plan.md`, `tests/bt3/test_bt3.py`, `tests/bt3/conftest.py`, `docs/screenshots/*` | Chạy `python -m pytest -m bt3`: lần 1 11/12 (TC-07 FAIL, ghi trung thực), sau sửa 12/12; mở từng ảnh xem lệnh curl và phản hồi thật; kết quả thực tế lấy từ tệp test tự ghi `bt3-ket-qua-chay.md` |
| Claude Code | BT3: sửa BUG-08 (trường bắt buộc chỉ có khoảng trắng) và 4 unit test | `app/services/ticket_rules.py: require_text_fields`, `ticket_service._clean_fields`, `tests/test_crud_rules.py` | TC-07 FAIL trước sửa, PASS sau sửa; TC-11 và integration CRUD vẫn tạo được phiếu hợp lệ; `python -m pytest` 104 passed |
| Claude Code | BT3: Test Report, Bug Log 7 dòng, TD-20…TD-24, Deployment Guide, checklist bảo mật, tài liệu API (tiếng Anh), tệp `.http`, Docker Compose 2 lệnh, CI | `docs/test-report.md`, `docs/bug-log.md`, `docs/thay-doi-thiet-ke.md`, `docs/deployment-guide.md`, `docs/security-checklist.md`, `docs/api.md`, `docs/api-requests.http`, `docker-compose.yml`, `Dockerfile.backend`, `.github/workflows/ci.yml` | Đối chiếu từng số trong Test Report với lần chạy thật; kiểm link commit; Docker Compose: phép thử máy trắng ngày 10/11/2026 trong `C:\BT3test` – 2 lệnh, mã thoát 0, `db`/`backend`/`frontend` healthy, `init` thoát 0, đăng nhập QL_TT01 được; CI: lần chạy #1 Success |
| Claude Code | BT3 Buổi 16: dịch vụ `test` trong Docker Compose; viết lại Deployment Guide theo năm mục; checklist bảo mật với nhãn ĐÃ LÀM/CHƯA LÀM; script chụp ví dụ API và tài liệu API bảy mục cho mỗi endpoint; sửa bảng khai báo này | `Dockerfile.backend`, `docker-compose.yml`, `docs/deployment-guide.md`, `docs/security-checklist.md`, `scripts/capture_api_examples.py`, `docs/api-examples.md`, `docs/api.md` | `docker compose run --rm test`: 104 passed; chạy script trên stack Docker thật (44 yêu cầu), ví dụ trong `docs/api.md` được chép nguyên từ kết quả đó; so 20 route trong mã với 20 endpoint trong tài liệu; chạy lại từng lệnh minh chứng của checklist |

## 2. Quyết định do em đưa ra khi rà soát kết quả AI

- Không ẩn phiếu đã đóng/đã hủy ở M3: kỹ thuật viên vẫn xem được phiếu của chính mình nhưng không xem được phiếu người khác; thêm bộ lọc thay vì ẩn (TD-13).
- Bỏ ảnh minh chứng vẽ bằng Pillow, chỉ dùng ảnh chụp trình duyệt thật.
- Giữ nguyên thư mục `docs/diagrams/`.
- Chọn CRUD cho hai thực thể Phiếu và Lịch hẹn; xoá là hủy mềm theo QT-13 (TD-17).
- Đưa bộ dữ liệu mẫu nhỏ trích từ dữ liệu thật vào repo để người khác clone chạy được ngay (TD-19).
- Yêu cầu kiểm chứng lại bằng bản clone từ GitHub trước khi gắn tag.
- BT3: ảnh minh chứng chụp bằng Playwright trên Swagger/giao diện thật; ảnh terminal (TC-12, BUG-08-fixed) em tự chụp.
- BT3: săn bug mới bằng test case thay vì chỉ dùng lại bug cũ; không ghi bug nào chưa tái lập được (giả thuyết TC-08 trả 500 đã chạy và không đúng, nên không ghi bug).
- BT3: đóng gói Docker Compose hai lệnh (`cp .env.example .env`, `docker compose up -d --build`).
- BT3 Buổi 16: ví dụ request/response trong tài liệu API được chép từ lần chạy thật của script, không viết tay; mã lỗi nào chưa chạy thật thì đánh dấu rõ trong bảng.
- BT3 Buổi 16: chạy unit test trong container riêng (`docker compose run --rm test`) để người chấm không cần cài Python.

## 3. Phần do em tự làm

- Chọn luồng nghiệp vụ L04, viết phiếu phạm vi và danh sách User Story sơ bộ (buổi 2).
- Cung cấp case study, tài liệu các buổi và bộ CSV cho công cụ.
- Chỉnh bố cục các sơ đồ `erd.drawio`, `architecture.drawio` trong draw.io.
- Kiểm thử thủ công MT01–MT11 trong báo cáo Buổi 10.

## 4. Cam kết

Em đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung nộp, kể cả phần có AI hỗ trợ, và giải thích được từng hàm khi được hỏi. 

Họ tên: Nguyễn Quốc Việt – MSSV 2374802010556.
