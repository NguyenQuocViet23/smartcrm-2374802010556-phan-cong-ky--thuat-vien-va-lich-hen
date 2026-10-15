-- =====================================================================
-- Smart CRM – Mekong Mobile | Luồng L04: Phân công kỹ thuật viên và lịch hẹn
-- SQL DDL skeleton (PostgreSQL 16) – BT1 mục 4, track SE
-- Sinh viên: Nguyễn Quốc Việt – MSSV 2374802010556
-- 6 bảng: service_center, technician, technician_skill, ticket,
--         appointment, ticket_status_log
-- =====================================================================
CREATE EXTENSION IF NOT EXISTS btree_gist;   -- cần cho EXCLUDE của appointment

-- 1. Trung tâm bảo hành ------------------------------------------------
CREATE TABLE service_center (
    center_id    BIGSERIAL    PRIMARY KEY,
    center_code  VARCHAR(20)  NOT NULL UNIQUE,
    center_name  VARCHAR(120) NOT NULL,
    city         VARCHAR(60)  NOT NULL
);

-- 2. Kỹ thuật viên -----------------------------------------------------
CREATE TABLE technician (
    technician_id    BIGSERIAL    PRIMARY KEY,
    technician_code  VARCHAR(20)  NOT NULL UNIQUE,
    full_name        VARCHAR(120) NOT NULL,
    center_id        BIGINT       NOT NULL REFERENCES service_center (center_id),
    level            VARCHAR(10)  NOT NULL
                     CHECK (level IN ('SO_CAP', 'TRUNG_CAP', 'CAO_CAP')),
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE
);
-- FR2 / NFR1: lọc kỹ thuật viên theo trung tâm và đang làm việc (A6)
CREATE INDEX idx_technician_center_active ON technician (center_id, is_active);

-- 3. Tay nghề của kỹ thuật viên theo nhóm sự cố (N:M) ------------------
CREATE TABLE technician_skill (
    technician_id  BIGINT      NOT NULL REFERENCES technician (technician_id),
    category_code  VARCHAR(20) NOT NULL
                   CHECK (category_code IN
                          ('MAN_HINH','PIN','SAC','PHAN_MEM','NUOC_VAO','KHAC')),
    proficiency    SMALLINT    NOT NULL CHECK (proficiency BETWEEN 1 AND 5),
    PRIMARY KEY (technician_id, category_code)
);
-- FR2 / NFR1: tìm kỹ thuật viên có proficiency >= 3 theo nhóm sự cố (QT-08)
CREATE INDEX idx_skill_category_prof ON technician_skill (category_code, proficiency);

-- 4. Phiếu bảo hành ----------------------------------------------------
CREATE TABLE ticket (
    ticket_id       BIGSERIAL    PRIMARY KEY,
    ticket_code     VARCHAR(20)  NOT NULL UNIQUE,          -- BH-000123/2026
    center_id       BIGINT       NOT NULL REFERENCES service_center (center_id),
    customer_name   VARCHAR(120) NOT NULL,                 -- ảnh chụp lúc tiếp nhận (L2)
    customer_phone  VARCHAR(10)  NOT NULL                  -- QT-02; hiển thị che theo QT-15
                    CHECK (customer_phone ~ '^0[0-9]{9}$'),
    serial_no       VARCHAR(50)  NOT NULL,
    issue_desc      TEXT         NOT NULL,
    category_code   VARCHAR(20)
                    CHECK (category_code IN
                           ('MAN_HINH','PIN','SAC','PHAN_MEM','NUOC_VAO','KHAC')),
    priority        VARCHAR(10)  NOT NULL
                    CHECK (priority IN ('CAO', 'TRUNG_BINH', 'THAP')),
    status          VARCHAR(20)  NOT NULL DEFAULT 'MOI'
                    CHECK (status IN ('MOI','DA_PHAN_CONG','DANG_XU_LY',
                                      'CHO_LINH_KIEN','HOAN_TAT','DA_DONG','DA_HUY')),
    technician_id   BIGINT       REFERENCES technician (technician_id),   -- QT-07: tối đa 1
    received_at     TIMESTAMPTZ  NOT NULL,
    due_date        TIMESTAMPTZ  NOT NULL,                 -- hạn cam kết (L2 sinh theo QT-04)
    closed_at       TIMESTAMPTZ,
    CHECK (status <> 'MOI' OR technician_id IS NULL)       -- phiếu MỚI chưa có người
);
-- FR1 / NFR1: danh sách phiếu MỚI của trung tâm, sắp theo hạn cam kết (A4), phân trang 20 dòng
CREATE INDEX idx_ticket_center_status_due ON ticket (center_id, status, due_date);
-- FR2 (khối lượng, A1) / FR5 / NFR1: phiếu của một kỹ thuật viên theo hạn cam kết
CREATE INDEX idx_ticket_tech_status_due   ON ticket (technician_id, status, due_date);

-- 5. Lịch hẹn giao/nhận thiết bị --------------------------------------
CREATE TABLE appointment (
    appointment_id    BIGSERIAL    PRIMARY KEY,
    ticket_id         BIGINT       NOT NULL REFERENCES ticket (ticket_id),
    technician_id     BIGINT       NOT NULL REFERENCES technician (technician_id),
    appointment_type  VARCHAR(10)  NOT NULL CHECK (appointment_type IN ('GIAO', 'NHAN')),
    start_at          TIMESTAMPTZ  NOT NULL,
    end_at            TIMESTAMPTZ  NOT NULL,
    status            VARCHAR(10)  NOT NULL DEFAULT 'DA_HEN'
                      CHECK (status IN ('DA_HEN', 'DA_HUY')),   -- QT-13: chỉ đánh dấu, không xóa
    note              VARCHAR(255),
    created_by        BIGINT       NOT NULL,                    -- mã nhân viên từ hệ thống đăng nhập
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CHECK (end_at > start_at),
    -- FR7 / A3: hai lịch DA_HEN của cùng kỹ thuật viên không được giao nhau;
    -- khoảng nửa mở [start, end) nên lịch liền kề (kết thúc = bắt đầu) vẫn hợp lệ.
    CONSTRAINT ex_appointment_no_overlap
        EXCLUDE USING gist (technician_id WITH =,
                            tstzrange(start_at, end_at, '[)') WITH &&)
        WHERE (status = 'DA_HEN')
);
CREATE INDEX idx_appointment_ticket ON appointment (ticket_id);

-- 6. Lịch sử trạng thái (gồm cả sự kiện đổi kỹ thuật viên) --------------
CREATE TABLE ticket_status_log (
    log_id              BIGSERIAL    PRIMARY KEY,
    ticket_id           BIGINT       NOT NULL REFERENCES ticket (ticket_id),
    event_type          VARCHAR(20)  NOT NULL
                        CHECK (event_type IN ('TRANG_THAI', 'DOI_KTV')),
    from_status         VARCHAR(20),                            -- NULL ở lần ghi đầu tiên
    to_status           VARCHAR(20)  NOT NULL,
    from_technician_id  BIGINT       REFERENCES technician (technician_id),
    to_technician_id    BIGINT       REFERENCES technician (technician_id),
    changed_by          BIGINT       NOT NULL,                  -- mã nhân viên từ hệ thống đăng nhập
    changed_at          TIMESTAMPTZ  NOT NULL DEFAULT now(),
    note                VARCHAR(255),
    -- QT-07: đổi kỹ thuật viên bắt buộc có lý do (không rỗng)
    CHECK (event_type <> 'DOI_KTV' OR (note IS NOT NULL AND length(btrim(note)) > 0))
);
-- FR3 / FR4 / FR8: tra lịch sử của một phiếu theo thời gian
CREATE INDEX idx_log_ticket_changed ON ticket_status_log (ticket_id, changed_at);

-- QT-13: không xóa vật lý. Khi triển khai: REVOKE DELETE ON ticket, appointment,
-- ticket_status_log FROM <app_user>;
