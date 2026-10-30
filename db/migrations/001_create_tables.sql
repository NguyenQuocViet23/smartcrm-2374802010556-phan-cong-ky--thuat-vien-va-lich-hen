-- Smart CRM – Mekong Mobile | L04
-- Idempotent migration based on db/schema.sql.
CREATE EXTENSION IF NOT EXISTS btree_gist;

CREATE TABLE IF NOT EXISTS service_center (
    center_id    BIGSERIAL    PRIMARY KEY,
    center_code  VARCHAR(20)  NOT NULL UNIQUE,
    center_name  VARCHAR(120) NOT NULL,
    city         VARCHAR(60)  NOT NULL
);

CREATE TABLE IF NOT EXISTS technician (
    technician_id    BIGSERIAL    PRIMARY KEY,
    technician_code  VARCHAR(20)  NOT NULL UNIQUE,
    full_name        VARCHAR(120) NOT NULL,
    center_id        BIGINT       NOT NULL REFERENCES service_center (center_id),
    level            VARCHAR(10)  NOT NULL
                     CHECK (level IN ('SO_CAP', 'TRUNG_CAP', 'CAO_CAP')),
    is_active        BOOLEAN      NOT NULL DEFAULT TRUE
);
CREATE INDEX IF NOT EXISTS idx_technician_center_active
    ON technician (center_id, is_active);

CREATE TABLE IF NOT EXISTS technician_skill (
    technician_id  BIGINT      NOT NULL REFERENCES technician (technician_id),
    category_code  VARCHAR(20) NOT NULL
                   CHECK (category_code IN
                          ('MAN_HINH','PIN','SAC','PHAN_MEM','NUOC_VAO','KHAC')),
    proficiency    SMALLINT    NOT NULL CHECK (proficiency BETWEEN 1 AND 5),
    PRIMARY KEY (technician_id, category_code)
);
CREATE INDEX IF NOT EXISTS idx_skill_category_prof
    ON technician_skill (category_code, proficiency);

CREATE TABLE IF NOT EXISTS ticket (
    ticket_id       BIGSERIAL    PRIMARY KEY,
    ticket_code     VARCHAR(20)  NOT NULL UNIQUE,
    center_id       BIGINT       NOT NULL REFERENCES service_center (center_id),
    customer_name   VARCHAR(120) NOT NULL,
    customer_phone  VARCHAR(10)  NOT NULL
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
    technician_id   BIGINT       REFERENCES technician (technician_id),
    received_at     TIMESTAMPTZ  NOT NULL,
    due_date        TIMESTAMPTZ  NOT NULL,
    closed_at       TIMESTAMPTZ,
    CHECK (status <> 'MOI' OR technician_id IS NULL)
);
CREATE INDEX IF NOT EXISTS idx_ticket_center_status_due
    ON ticket (center_id, status, due_date);
CREATE INDEX IF NOT EXISTS idx_ticket_tech_status_due
    ON ticket (technician_id, status, due_date);

CREATE TABLE IF NOT EXISTS appointment (
    appointment_id    BIGSERIAL    PRIMARY KEY,
    ticket_id         BIGINT       NOT NULL REFERENCES ticket (ticket_id),
    technician_id     BIGINT       NOT NULL REFERENCES technician (technician_id),
    appointment_type  VARCHAR(10)  NOT NULL CHECK (appointment_type IN ('GIAO', 'NHAN')),
    start_at          TIMESTAMPTZ  NOT NULL,
    end_at            TIMESTAMPTZ  NOT NULL,
    status            VARCHAR(10)  NOT NULL DEFAULT 'DA_HEN'
                      CHECK (status IN ('DA_HEN', 'DA_HUY')),
    note              VARCHAR(255),
    created_by        BIGINT       NOT NULL,
    created_at        TIMESTAMPTZ  NOT NULL DEFAULT now(),
    CHECK (end_at > start_at),
    CONSTRAINT ex_appointment_no_overlap
        EXCLUDE USING gist (technician_id WITH =,
                            tstzrange(start_at, end_at, '[)') WITH &&)
        WHERE (status = 'DA_HEN')
);
CREATE INDEX IF NOT EXISTS idx_appointment_ticket ON appointment (ticket_id);

CREATE TABLE IF NOT EXISTS ticket_status_log (
    log_id              BIGSERIAL    PRIMARY KEY,
    ticket_id           BIGINT       NOT NULL REFERENCES ticket (ticket_id),
    event_type          VARCHAR(20)  NOT NULL
                        CHECK (event_type IN ('TRANG_THAI', 'DOI_KTV')),
    from_status         VARCHAR(20),
    to_status           VARCHAR(20)  NOT NULL,
    from_technician_id  BIGINT       REFERENCES technician (technician_id),
    to_technician_id    BIGINT       REFERENCES technician (technician_id),
    changed_by          BIGINT       NOT NULL,
    changed_at          TIMESTAMPTZ  NOT NULL DEFAULT now(),
    note                VARCHAR(255),
    CHECK (event_type <> 'DOI_KTV' OR (note IS NOT NULL AND length(btrim(note)) > 0))
);
CREATE INDEX IF NOT EXISTS idx_log_ticket_changed
    ON ticket_status_log (ticket_id, changed_at);
