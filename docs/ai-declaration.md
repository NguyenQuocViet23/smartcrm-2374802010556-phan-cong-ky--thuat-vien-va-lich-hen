# Khai báo sử dụng công cụ AI – BT1, luồng L04

| | |
|---|---|
| **Sinh viên** | Nguyễn Quốc Việt – MSSV 2374802010556 |
| **Học phần** | Chuyên đề Tốt nghiệp 1 (71ITGR40203) – Trường ĐH Văn Lang |
| **Đề tài** | Smart CRM – Mekong Mobile, luồng L04: Phân công kỹ thuật viên và lịch hẹn (track SE) |
| **Phạm vi** | Bài tập 1 (BT1): SRS, Use Case, kiến trúc, mô hình dữ liệu, wireframe |
| **Phiên bản / ngày** | v0.1 – [điền ngày] |

> **Cách dùng tệp này:** cột "Cách tự kiểm chứng" ghi những việc em cần làm thật. Mỗi ô `[ ]` chỉ được đánh dấu `[x]` sau khi em đã làm xong việc đó. Dòng nào chưa làm thì để trống hoặc xóa, không ghi cho đủ.

## 1. Công cụ đã dùng

| Công cụ | Dùng vào việc gì | Cách tự kiểm chứng |
|---|---|---|
| **Claude** (Anthropic) | **Mục 1 – SRS.** Soạn bản nháp SRS rút gọn (`docs/srs.md`) từ case study, phiếu phạm vi, tài liệu buổi 3–4; gợi ý 7 User Story, tiêu chí Given–When–Then, bảng truy vết | [ ] Đối chiếu từng quy tắc QT-xx với case study<br>[ ] Rà lại giả định A1–A6 và hỏi giảng viên những điểm case study không quy định<br>[ ] Đối chiếu số lượng User Story (7) và MoSCoW (3 MUST) với yêu cầu buổi 3–4 |
| **Claude** (Anthropic) | **Mục 2 – Use Case.** Gợi ý danh sách 7 use case, đặc tả UC3 và UC6; sinh tệp `usecase.drawio` | [ ] Mở `usecase.drawio` trong draw.io, kiểm actor, ranh giới hệ thống, «include»<br>[ ] Đối chiếu từng use case với User Story và FR ở bảng truy vết |
| **Claude** (Anthropic) | **Mục 3 – Kiến trúc.** Gợi ý kiến trúc 4 lớp, danh sách thành phần, bốn câu lập luận theo khuôn "Vì NFR… tôi chọn… đánh đổi là…"; sinh tệp `architecture.drawio` | [ ] Đọc lại từng câu lập luận, sửa bằng lời của em và giải thích được khi bảo vệ<br>[ ] Kiểm mã NFR và ngưỡng số khớp mục 1.4 của SRS<br>[ ] Kiểm sáu tên bảng ở lớp lưu trữ khớp ERD |
| **Claude** (Anthropic) | **Mục 4 – Mô hình dữ liệu.** Gợi ý ERD 6 bảng, chỉ mục, quyết định thiết kế; viết `db/schema.sql`; sinh tệp `erd.drawio` | [ ] Chạy `db/schema.sql` trên PostgreSQL 16 thật, ghi lại kết quả<br>[ ] Nạp thử dữ liệu mẫu (`tickets_history.csv`, `technicians.csv`, …) và sửa lỗi nếu có<br>[ ] Kiểm lại 5 lỗi ERD (bảng cô lập, thiếu lịch sử, giá trị tính được, thiếu index, khóa nghiệp vụ làm khóa chính)<br>[ ] Quyết định giữ hay đổi các điểm thiết kế ở mục 4.6 sau khi hỏi giảng viên |
| **Claude** (Anthropic) | **Mục 5 – Wireframe.** Sinh tệp `wireframe.drawio` 3 màn hình và bảng đối chiếu trường dữ liệu với ERD | [ ] Kiểm từng trường trên wireframe có cột tương ứng trong ERD (hoặc ghi rõ là giá trị tính)<br>[ ] Kiểm mỗi ngoại lệ của UC3, UC6 có chỗ hiển thị trên màn hình |
| **Claude** (Anthropic) | **Báo cáo Word.** Dựng file `BT1_2374802010556_NguyenQuocViet.docx`: trang bìa, mục lục, trình bày bảng, chèn hình xuất từ các tệp `.drawio` | [ ] Đọc lại toàn bộ báo cáo, sửa lỗi chính tả và diễn đạt<br>[ ] Cập nhật mục lục, kiểm số trang<br>[ ] Điền lớp, ngày nộp; xuất PDF và kiểm hình hiển thị đủ |

## 2. Những việc công cụ AI đã tự kiểm tra (chỉ mang tính tham khảo)

- Cú pháp `db/schema.sql` đã được kiểm bằng bộ phân tích cú pháp PostgreSQL (13 câu lệnh hợp lệ). Đây **chưa phải** chạy thật trên cơ sở dữ liệu.
- Các tệp `.drawio` đã được kiểm đúng định dạng XML và các liên kết giữa các thành phần.
- Hình trong báo cáo Word được vẽ lại từ tệp `.drawio` bằng chương trình riêng nên có thể khác đôi chút so với hình hiển thị trong draw.io.

## 3. Phần do em tự làm

- Chọn luồng nghiệp vụ L04, viết phiếu phạm vi và danh sách User Story sơ bộ (buổi 2).
- Cung cấp case study, tài liệu buổi 3–6 và dữ liệu mẫu cho công cụ.
- Chỉnh sửa bố cục các sơ đồ `erd.drawio` và `architecture.drawio` trong draw.io.
- [Bổ sung các việc khác em đã thật sự làm.]

## 4. Cam kết

Em đã đọc, hiểu và chịu trách nhiệm về toàn bộ nội dung nộp. Các phần có sự hỗ trợ của công cụ AI được khai báo ở trên. [Ký tên / ghi rõ họ tên sau khi đã kiểm chứng.]
