# API Reference – Smart CRM (L04)

Base URL: `http://localhost:8000` · Interactive documentation generated from the code: `/docs` (Swagger UI).
All bodies are JSON; times are ISO 8601 **with a time zone** (for example `2026-12-08T09:00:00+07:00`).

**20 endpoints**, one section each, with seven items: (1) method and path, (2) purpose, (3) authentication and role, (4) path and query parameters, (5) request body, (6) success response, (7) error codes. Every request and response below is **copied from a real run** of `scripts/capture_api_examples.py` against the Docker Compose stack with the sample data; the full set, including the error cases, is in [api-examples.md](api-examples.md). Long lists are shortened to their first items.

## 1. Conventions

**Authentication.** Log in with a demo account, then send `Authorization: Bearer <access_token>` on every call except the three public ones (`POST /api/auth/login`, `GET /`, `GET /db-check`). A token is valid for 8 hours.

**Roles.** `QUAN_LY` (center manager, accounts `QL_TT01` … `QL_TT06`) and `KY_THUAT_VIEN` (technician, accounts named by `technician_code`, for example `KT002`). A manager sees only tickets of their own center; a technician sees only tickets assigned to them, with the customer phone masked (`091****678`).

**Ticket statuses.** `MOI → DA_PHAN_CONG → DANG_XU_LY → (CHO_LINH_KIEN) → HOAN_TAT`, plus `DA_DONG` and `DA_HUY`.

**Errors.** Every error has the shape `{"error": "<CODE>", "message": "<Vietnamese message>"}`, sometimes with extra fields (`fields`, `conflicts`, `free_slots`). No error body contains a stack trace or SQL. In the tables below, **captured** means the code was returned by a request in `api-examples.md`; the other codes come from reading the service code and have a unit or BT3 test (`docs/test-report.md`) rather than an example here.

## 2. Authentication

### 1. `POST /api/auth/login`

1. **Method and path:** `POST` `/api/auth/login`
2. **Purpose:** Exchange a demo account name and password for a bearer token (valid 8 hours).
3. **Authentication and role:** Public – no token.
4. **Parameters:** None.
5. **Request body** (real request: `POST /api/auth/login`, valid account):
   ```json
   {
     "username": "QL_TT01",
     "password": "<DEMO_PASSWORD>"
   }
   ```
6. **Success response** – HTTP 200:
   ```json
   {
     "access_token": "eyJhbGciOiJIUzI1NiIsInR5…",
     "token_type": "bearer"
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | yes – body without the required fields |
   | 401 | `INVALID_CREDENTIALS` | unknown account or wrong password | yes – wrong password |
   | 503 | `DEMO_ACCOUNTS_NOT_READY` | `data/processed/demo_accounts.json` does not exist yet | – |
   | 503 | `AUTH_CONFIGURATION_ERROR` | `SECRET_KEY` is shorter than 32 characters | – |

### 2. `GET /api/auth/me`

1. **Method and path:** `GET` `/api/auth/me`
2. **Purpose:** Return the profile of the logged-in user.
3. **Authentication and role:** Bearer token – any role.
4. **Parameters:** None.
5. **Request body:** none.
6. **Success response** – HTTP 200:
   ```json
   {
     "role": "QUAN_LY",
     "center_id": 1,
     "center_name": "TTBH Quận 10",
     "technician_id": null,
     "full_name": "Quản lý TTBH Quận 10",
     "employee_id": 1
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | yes – no token |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |

## 3. Tickets

### 3. `GET /api/tickets`

1. **Method and path:** `GET` `/api/tickets`
2. **Purpose:** List tickets of the manager's own center, ordered by priority (`CAO` first), then due date, one page at a time.
3. **Authentication and role:** Bearer token – role `QUAN_LY` only.
4. **Parameters:** Query: `status` (default `MOI`; one of `MOI`, `DA_PHAN_CONG`, `DANG_XU_LY`, `CHO_LINH_KIEN`, `HOAN_TAT`, `DA_DONG`, `DA_HUY`), `category_code`, `priority`, `page` (≥ 1, default 1), `page_size` (1–100, default 20).
5. **Request body:** none.
6. **Success response** – HTTP 200:
   ```json
   {
     "items": [
       {
         "ticket_id": 5310,
         "ticket_code": "BH-005310/2025",
         "center_id": 1,
         "customer_name": "Võ Bảo Oanh",
         "customer_phone": "0348726247",
         "serial_no": "SN649367951380",
         "issue_desc": "kh nói màn hình bị ám vàng một góc bị từ tuần trước",
         "category_code": "MAN_HINH",
         "priority": "CAO",
         "status": "MOI",
         "technician_id": null,
         "received_at": "2025-10-07T03:00:00Z",
         "due_date": "2025-10-08T03:00:00Z"
       },
       {
         "ticket_id": 6628,
         "ticket_code": "BH-006628/2024",
         "center_id": 1,
         "customer_name": "Trần Quang Quân",
         "customer_phone": "0392013555",
         "serial_no": "SN947432543337",
         "issue_desc": "khách hàng phản ánh pin tụt rất nhanh dùng 2 tiếng đã hết bị từ tuần trước",
         "category_code": "PIN",
         "priority": "TRUNG_BINH",
         "status": "MOI",
         "technician_id": null,
         "received_at": "2024-12-28T03:45:00Z",
         "due_date": "2024-12-31T03:45:00Z"
       }
     ],
     "total": 5,
     "page": 1,
     "page_size": 2
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | yes – page number out of range |
   | 400 | `INVALID_STATUS` | `status` is not one of the seven statuses | yes – invalid status filter |
   | 400 | `INVALID_PRIORITY` | `priority` is not `CAO`, `TRUNG_BINH` or `THAP` | – |
   | 403 | `FORBIDDEN` | the role is not allowed to call this endpoint | – |

### 4. `POST /api/tickets`

1. **Method and path:** `POST` `/api/tickets`
2. **Purpose:** Create a ticket in the manager's center with status `MOI` (minimal CRUD, TD-17).
3. **Authentication and role:** Bearer token – role `QUAN_LY` only.
4. **Parameters:** None.
5. **Request body** (real request: `POST /api/tickets`, valid ticket):
   ```json
   {
     "customer_name": "Nguyễn Văn An (API-DOC)",
     "customer_phone": "0912 345 678",
     "serial_no": "SN-API-DOC-01",
     "issue_desc": "Máy không lên nguồn sau khi rơi",
     "category_code": "PIN",
     "priority": "CAO",
     "due_date": "2026-11-22T17:00:00+07:00"
   }
   ```

   `customer_phone` is normalised to 10 digits starting with 0 (spaces, dots, dashes and `+84` are accepted); `category_code`: `MAN_HINH`, `PIN`, `SAC`, `PHAN_MEM`, `NUOC_VAO`, `KHAC`; `priority`: `CAO`, `TRUNG_BINH`, `THAP`; `due_date` must include a time zone and lie in the future.
6. **Success response** – HTTP 201:
   ```json
   {
     "ticket_id": 7803,
     "ticket_code": "BH-007803/2026",
     "center_id": 1,
     "customer_name": "Nguyễn Văn An (API-DOC)",
     "customer_phone": "0912345678",
     "serial_no": "SN-API-DOC-01",
     "issue_desc": "Máy không lên nguồn sau khi rơi",
     "category_code": "PIN",
     "priority": "CAO",
     "status": "MOI",
     "technician_id": null,
     "received_at": "2026-11-14T18:35:12.174572Z",
     "due_date": "2026-11-22T10:00:00Z",
     "closed_at": null
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | – |
   | 400 | `REQUIRED_FIELD_BLANK` | `customer_name`, `serial_no` or `issue_desc` is empty or only spaces | yes – required fields only spaces |
   | 400 | `INVALID_PHONE` | `customer_phone` is not a valid Vietnamese phone number | yes – invalid phone number |
   | 400 | `INVALID_CATEGORY` | `category_code` is not one of the six codes | – |
   | 400 | `INVALID_PRIORITY` | `priority` is not `CAO`, `TRUNG_BINH` or `THAP` | – |
   | 400 | `INVALID_DATETIME` | `due_date` has no time zone | – |
   | 400 | `INVALID_DUE_DATE` | `due_date` is not in the future | – |
   | 403 | `FORBIDDEN` | the role is not allowed to call this endpoint | – |

### 5. `GET /api/tickets/{ticket_id}`

1. **Method and path:** `GET` `/api/tickets/{ticket_id}`
2. **Purpose:** Read one ticket with its technician and status history.
3. **Authentication and role:** Bearer token – any role, limited to the user's scope: a manager reads tickets of their own center; a technician reads only their own tickets and sees the customer phone masked.
4. **Parameters:** Path: `ticket_id` (integer).
5. **Request body:** none.
6. **Success response** – HTTP 200:
   ```json
   {
     "ticket_id": 7804,
     "ticket_code": "BH-007804/2026",
     "center_id": 1,
     "customer_name": "Nguyễn Văn An (API-DOC)",
     "customer_phone": "0912345678",
     "serial_no": "SN-API-DOC-02",
     "issue_desc": "Máy không lên nguồn sau khi rơi",
     "category_code": "PIN",
     "priority": "CAO",
     "status": "MOI",
     "technician_id": null,
     "received_at": "2026-11-14T18:35:12.191687Z",
     "due_date": "2026-11-22T10:00:00Z",
     "closed_at": null,
     "technician": null,
     "status_history": [
       {
         "log_id": 38120,
         "event_type": "TRANG_THAI",
         "from_status": null,
         "to_status": "MOI",
         "from_technician_id": null,
         "from_technician_code": null,
         "to_technician_id": null,
         "to_technician_code": null,
         "changed_by": 1,
         "changed_at": "2026-11-14T18:35:12.191687Z",
         "note": "Tạo phiếu"
       }
     ]
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | – |
   | 403 | `FORBIDDEN` | the ticket belongs to another center (manager) or to another technician | – |
   | 404 | `TICKET_NOT_FOUND` | no ticket with this id | yes – ticket does not exist |

### 6. `PUT /api/tickets/{ticket_id}`

1. **Method and path:** `PUT` `/api/tickets/{ticket_id}`
2. **Purpose:** Correct a ticket that is still `MOI`.
3. **Authentication and role:** Bearer token – role `QUAN_LY`, own center only.
4. **Parameters:** Path: `ticket_id`.
5. **Request body** (real request: `PUT /api/tickets/7804`, correct a MOI ticket):
   ```json
   {
     "customer_name": "Nguyễn Văn An (API-DOC)",
     "customer_phone": "0912 345 678",
     "serial_no": "SN-API-DOC-02",
     "issue_desc": "Màn hình bị sọc ngang",
     "category_code": "PIN",
     "priority": "CAO",
     "due_date": "2026-11-22T17:00:00+07:00"
   }
   ```

   Same fields and rules as `POST /api/tickets`.
6. **Success response** – HTTP 200:
   ```json
   {
     "ticket_id": 7804,
     "ticket_code": "BH-007804/2026",
     "center_id": 1,
     "customer_name": "Nguyễn Văn An (API-DOC)",
     "customer_phone": "0912345678",
     "serial_no": "SN-API-DOC-02",
     "issue_desc": "Màn hình bị sọc ngang",
     "category_code": "PIN",
     "priority": "CAO",
     "status": "MOI",
     "technician_id": null,
     "received_at": "2026-11-14T18:35:12.191687Z",
     "due_date": "2026-11-22T10:00:00Z",
     "closed_at": null
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | – |
   | 400 | `REQUIRED_FIELD_BLANK` | `customer_name`, `serial_no` or `issue_desc` is empty or only spaces | yes – required field only spaces |
   | 400 | `INVALID_PHONE` | `customer_phone` is not a valid Vietnamese phone number | – |
   | 400 | `INVALID_CATEGORY` | `category_code` is not one of the six codes | – |
   | 400 | `INVALID_PRIORITY` | `priority` is not `CAO`, `TRUNG_BINH` or `THAP` | – |
   | 400 | `INVALID_DATETIME` | `due_date` has no time zone | – |
   | 400 | `INVALID_DUE_DATE` | `due_date` is not in the future | – |
   | 403 | `FORBIDDEN` | the role is not allowed to call this endpoint | – |
   | 403 | `FORBIDDEN` | the ticket belongs to another center (manager) or to another technician | – |
   | 404 | `TICKET_NOT_FOUND` | no ticket with this id | – |
   | 409 | `TICKET_NOT_EDITABLE` | the ticket is no longer `MOI` | – |

### 7. `DELETE /api/tickets/{ticket_id}`

1. **Method and path:** `DELETE` `/api/tickets/{ticket_id}`
2. **Purpose:** Soft cancel: a `MOI` ticket becomes `DA_HUY`; nothing is physically deleted.
3. **Authentication and role:** Bearer token – role `QUAN_LY`, own center only.
4. **Parameters:** Path: `ticket_id`. Query: `reason` (optional, ≤ 255 characters).
5. **Request body:** none.
6. **Success response** – HTTP 200:
   ```json
   {
     "ticket_id": 7804,
     "ticket_code": "BH-007804/2026",
     "status": "DA_HUY",
     "closed_at": "2026-11-14T18:35:12.245961Z"
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | – |
   | 403 | `FORBIDDEN` | the role is not allowed to call this endpoint | – |
   | 403 | `FORBIDDEN` | the ticket belongs to another center (manager) or to another technician | – |
   | 404 | `TICKET_NOT_FOUND` | no ticket with this id | – |
   | 409 | `TICKET_NOT_CANCELLABLE` | the ticket is not `MOI` (already assigned, finished or cancelled) | yes – cancel it again |

### 8. `GET /api/tickets/{ticket_id}/technician-suggestions`

1. **Method and path:** `GET` `/api/tickets/{ticket_id}/technician-suggestions`
2. **Purpose:** Suggest technicians for a ticket: same center, active, proficiency ≥ 3 in the ticket's category, ordered by workload ascending (QT-08). When nobody qualifies, `suggestions` is empty and a `message` explains why.
3. **Authentication and role:** Bearer token – role `QUAN_LY`, own center only.
4. **Parameters:** Path: `ticket_id`.
5. **Request body:** none.
6. **Success response** – HTTP 200:
   ```json
   {
     "ticket_id": 7803,
     "ticket_code": "BH-007803/2026",
     "category": "PIN",
     "center_id": 1,
     "suggestions": [
       {
         "technician_id": 33,
         "technician_code": "KT033",
         "full_name": "Phan Kim Hạnh",
         "level": "CAO_CAP",
         "proficiency": 3,
         "workload": 29
       },
       {
         "technician_id": 20,
         "technician_code": "KT020",
         "full_name": "Trần Văn Thảo",
         "level": "TRUNG_CAP",
         "proficiency": 3,
         "workload": 40
       }
     ]
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | – |
   | 403 | `FORBIDDEN` | the role is not allowed to call this endpoint | yes – a technician is not allowed |
   | 403 | `FORBIDDEN` | the ticket belongs to another center (manager) or to another technician | yes – a technician is not allowed |
   | 404 | `TICKET_NOT_FOUND` | no ticket with this id | – |

### 9. `POST /api/tickets/{ticket_id}/assignment`

1. **Method and path:** `POST` `/api/tickets/{ticket_id}/assignment`
2. **Purpose:** Assign an eligible technician to a `MOI` ticket; the ticket becomes `DA_PHAN_CONG` and the change is logged.
3. **Authentication and role:** Bearer token – role `QUAN_LY`, own center only.
4. **Parameters:** Path: `ticket_id`.
5. **Request body** (real request: `POST /api/tickets/7803/assignment`, assign an eligible technician):
   ```json
   {
     "technician_id": 33
   }
   ```
6. **Success response** – HTTP 201:
   ```json
   {
     "ticket_id": 7803,
     "status": "DA_PHAN_CONG",
     "technician_id": 33,
     "assigned_by": 1,
     "assigned_at": "2026-11-14T18:35:12.337797Z"
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | – |
   | 403 | `FORBIDDEN` | the role is not allowed to call this endpoint | – |
   | 403 | `FORBIDDEN` | the ticket belongs to another center (manager) or to another technician | – |
   | 404 | `TICKET_NOT_FOUND` | no ticket with this id | – |
   | 404 | `TECHNICIAN_NOT_FOUND` | no technician with this id | – |
   | 400 | `TECHNICIAN_NOT_ELIGIBLE` | other center, inactive, or proficiency below 3 | – |
   | 409 | `TICKET_ALREADY_ASSIGNED` | the ticket is not `MOI` or already has a technician | yes – ticket already has a technician |

### 10. `PUT /api/tickets/{ticket_id}/assignment`

1. **Method and path:** `PUT` `/api/tickets/{ticket_id}/assignment`
2. **Purpose:** Change the technician of an assigned, still open ticket; a reason is required and logged.
3. **Authentication and role:** Bearer token – role `QUAN_LY`, own center only.
4. **Parameters:** Path: `ticket_id`.
5. **Request body** (real request: `PUT /api/tickets/7803/assignment`, change the technician with a reason):
   ```json
   {
     "technician_id": 20,
     "reason": "Kỹ thuật viên cũ nghỉ ốm"
   }
   ```
6. **Success response** – HTTP 200:
   ```json
   {
     "ticket_id": 7803,
     "status": "DA_PHAN_CONG",
     "technician_id": 20
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | – |
   | 403 | `FORBIDDEN` | the role is not allowed to call this endpoint | – |
   | 403 | `FORBIDDEN` | the ticket belongs to another center (manager) or to another technician | – |
   | 404 | `TICKET_NOT_FOUND` | no ticket with this id | – |
   | 404 | `TECHNICIAN_NOT_FOUND` | no technician with this id | – |
   | 400 | `REASON_REQUIRED` | `reason` is empty or only spaces | yes – reason only spaces |
   | 400 | `TECHNICIAN_NOT_ELIGIBLE` | other center, inactive, or proficiency below 3 | – |
   | 400 | `SAME_TECHNICIAN` | the new technician is already the ticket's technician | – |
   | 409 | `TICKET_NOT_ASSIGNED` | the ticket has no technician to replace | – |
   | 409 | `TICKET_NOT_CHANGEABLE` | the ticket is already finished or cancelled | – |

### 11. `PATCH /api/tickets/{ticket_id}/status`

1. **Method and path:** `PATCH` `/api/tickets/{ticket_id}/status`
2. **Purpose:** The owner technician moves the ticket one step forward in its lifecycle (`DA_PHAN_CONG → DANG_XU_LY`, `DANG_XU_LY → CHO_LINH_KIEN` or `HOAN_TAT`, `CHO_LINH_KIEN → HOAN_TAT`); the change is logged.
3. **Authentication and role:** Bearer token – role `KY_THUAT_VIEN`, only for a ticket assigned to this technician.
4. **Parameters:** Path: `ticket_id`.
5. **Request body** (real request: `PATCH /api/tickets/7803/status`, start work (owner technician)):
   ```json
   {
     "to_status": "DANG_XU_LY",
     "note": "Bắt đầu kiểm tra máy"
   }
   ```
6. **Success response** – HTTP 200:
   ```json
   {
     "ticket_id": 7803,
     "status": "DANG_XU_LY",
     "technician_id": 20
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | – |
   | 403 | `FORBIDDEN` | the role is not allowed to call this endpoint | yes – a manager is not allowed |
   | 403 | `FORBIDDEN` | the ticket belongs to another center (manager) or to another technician | yes – a manager is not allowed |
   | 404 | `TICKET_NOT_FOUND` | no ticket with this id | – |
   | 400 | `INVALID_STATUS` | `to_status` is not `DANG_XU_LY`, `CHO_LINH_KIEN` or `HOAN_TAT` | yes – go back to an earlier status |
   | 409 | `INVALID_STATUS_TRANSITION` | the target is not a forward step from the ticket's current status | – |

### 12. `GET /api/tickets/{ticket_id}/appointments`

1. **Method and path:** `GET` `/api/tickets/{ticket_id}/appointments`
2. **Purpose:** List the appointments of one ticket, ordered by start time.
3. **Authentication and role:** Bearer token – any role, limited to the user's scope (as for reading a ticket).
4. **Parameters:** Path: `ticket_id`.
5. **Request body:** none.
6. **Success response** – HTTP 200:
   ```json
   [
     {
       "appointment_id": 302,
       "ticket_id": 7803,
       "technician_id": 20,
       "appointment_type": "NHAN",
       "start_at": "2027-01-14T02:00:00Z",
       "end_at": "2027-01-14T03:00:00Z",
       "status": "DA_HEN",
       "note": "API-DOC"
     }
   ]
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | – |
   | 403 | `FORBIDDEN` | the ticket belongs to another center (manager) or to another technician | – |
   | 404 | `TICKET_NOT_FOUND` | no ticket with this id | – |

### 13. `GET /api/technicians/me/tickets`

1. **Method and path:** `GET` `/api/technicians/me/tickets`
2. **Purpose:** All tickets of the logged-in technician, ordered by due date, each with `is_overdue`.
3. **Authentication and role:** Bearer token – role `KY_THUAT_VIEN` only.
4. **Parameters:** None.
5. **Request body:** none.
6. **Success response** – HTTP 200:
   ```json
   [
     {
       "ticket_id": 378,
       "ticket_code": "BH-000378/2024",
       "customer_name": "Đỗ Đức Hạnh",
       "customer_phone": "033****714",
       "serial_no": "SN342435666464",
       "issue_desc": "may bi máy không giữ được pin qua đêm",
       "category_code": "PIN",
       "priority": "TRUNG_BINH",
       "status": "DA_DONG",
       "received_at": "2024-09-01T03:15:00Z",
       "due_date": "2024-09-04T03:15:00Z",
       "technician_id": 20,
       "is_overdue": false
     },
     {
       "ticket_id": 4784,
       "ticket_code": "BH-004784/2024",
       "customer_name": "VŨ ANH NHƯ",
       "customer_phone": "070****579",
       "serial_no": "SN826037062093",
       "issue_desc": "khách báo máy phồng pin cấn màn hình máy còn bảo hành",
       "category_code": "PIN",
       "priority": "TRUNG_BINH",
       "status": "DANG_XU_LY",
       "received_at": "2024-09-09T10:30:00Z",
       "due_date": "2024-09-12T10:30:00Z",
       "technician_id": 20,
       "is_overdue": true
     }
   ]
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 403 | `FORBIDDEN` | the role is not allowed to call this endpoint | yes – a manager is not allowed |

## 4. Appointments

### 14. `POST /api/appointments`

1. **Method and path:** `POST` `/api/appointments`
2. **Purpose:** Book a delivery (`GIAO`) or pick-up (`NHAN`) slot for a ticket; the appointment belongs to the ticket's current technician. Slots are half-open `[start, end)`, so 10:00–11:00 may follow 09:00–10:00.
3. **Authentication and role:** Bearer token – any role, limited to the user's scope.
4. **Parameters:** None.
5. **Request body** (real request: `POST /api/appointments`, valid slot 09:00-10:00):
   ```json
   {
     "ticket_id": 7803,
     "appointment_type": "NHAN",
     "note": "API-DOC",
     "start_at": "2027-01-14T09:00:00+07:00",
     "end_at": "2027-01-14T10:00:00+07:00"
   }
   ```

   `appointment_type`: `GIAO` or `NHAN`; times include a time zone; the slot is in the future, Monday–Saturday, inside 08:00–18:00 (UTC+7), on one day; `note` is optional (≤ 255 characters).
6. **Success response** – HTTP 201:
   ```json
   {
     "appointment_id": 302,
     "ticket_id": 7803,
     "technician_id": 20,
     "appointment_type": "NHAN",
     "start_at": "2027-01-14T02:00:00Z",
     "end_at": "2027-01-14T03:00:00Z",
     "status": "DA_HEN",
     "note": "API-DOC"
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | – |
   | 400 | `INVALID_DATETIME` | `start_at` or `end_at` has no time zone | – |
   | 400 | `INVALID_TIME_RANGE` | `end_at` is not after `start_at`, or the slot spans two days | yes – end before start |
   | 400 | `PAST_APPOINTMENT` | the slot is in the past | yes – slot in the past |
   | 400 | `OUTSIDE_WORKING_HOURS` | the slot is on Sunday or outside 08:00-18:00 (UTC+7) | yes – outside working hours |
   | 400 | `TICKET_NOT_ASSIGNED` | the ticket has no technician yet | – |
   | 400 | `TICKET_CLOSED` | the ticket is finished (`HOAN_TAT`, `DA_DONG`, `DA_HUY`) | – |
   | 409 | `APPOINTMENT_OVERLAP` | the technician already has an appointment in this slot; the response lists `conflicts` and `free_slots` | yes – overlapping slot |
   | 403 | `FORBIDDEN` | the ticket belongs to another center (manager) or to another technician | – |
   | 404 | `TICKET_NOT_FOUND` | no ticket with this id | – |

### 15. `GET /api/appointments`

1. **Method and path:** `GET` `/api/appointments`
2. **Purpose:** List appointments, newest start first: a manager sees the center's, a technician sees their own.
3. **Authentication and role:** Bearer token – any role.
4. **Parameters:** Query: `status` (e.g. `DA_HEN`, `DA_HUY`), `ticket_id`, `page` (≥ 1), `page_size` (1–100, default 20).
5. **Request body:** none.
6. **Success response** – HTTP 200:
   ```json
   {
     "items": [
       {
         "appointment_id": 302,
         "ticket_id": 7803,
         "ticket_code": "BH-007803/2026",
         "technician_id": 20,
         "appointment_type": "NHAN",
         "start_at": "2027-01-14T02:00:00Z",
         "end_at": "2027-01-14T03:00:00Z",
         "status": "DA_HEN",
         "note": "API-DOC"
       }
     ],
     "total": 1,
     "page": 1,
     "page_size": 20
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | – |
   | 400 | `INVALID_STATUS` | `status` is not a valid appointment status | – |

### 16. `GET /api/appointments/{appointment_id}`

1. **Method and path:** `GET` `/api/appointments/{appointment_id}`
2. **Purpose:** Read one appointment.
3. **Authentication and role:** Bearer token – any role, limited to the user's scope.
4. **Parameters:** Path: `appointment_id` (integer).
5. **Request body:** none.
6. **Success response** – HTTP 200:
   ```json
   {
     "appointment_id": 302,
     "ticket_id": 7803,
     "technician_id": 20,
     "appointment_type": "NHAN",
     "start_at": "2027-01-14T02:00:00Z",
     "end_at": "2027-01-14T03:00:00Z",
     "status": "DA_HEN",
     "note": "API-DOC"
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | – |
   | 403 | `FORBIDDEN` | the ticket belongs to another center (manager) or to another technician | – |
   | 404 | `APPOINTMENT_NOT_FOUND` | no appointment with this id | yes – appointment does not exist |

### 17. `PUT /api/appointments/{appointment_id}`

1. **Method and path:** `PUT` `/api/appointments/{appointment_id}`
2. **Purpose:** Reschedule an active appointment; overlap and working hours are checked again.
3. **Authentication and role:** Bearer token – any role, limited to the user's scope.
4. **Parameters:** Path: `appointment_id`.
5. **Request body** (real request: `PUT /api/appointments/302`, reschedule to 10:00-11:00):
   ```json
   {
     "appointment_type": "NHAN",
     "note": "API-DOC đổi giờ",
     "start_at": "2027-01-14T10:00:00+07:00",
     "end_at": "2027-01-14T11:00:00+07:00"
   }
   ```

   Same fields and rules as `POST /api/appointments`, without `ticket_id`.
6. **Success response** – HTTP 200:
   ```json
   {
     "appointment_id": 302,
     "ticket_id": 7803,
     "technician_id": 20,
     "appointment_type": "NHAN",
     "start_at": "2027-01-14T03:00:00Z",
     "end_at": "2027-01-14T04:00:00Z",
     "status": "DA_HEN",
     "note": "API-DOC đổi giờ"
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | – |
   | 400 | `INVALID_DATETIME` | `start_at` or `end_at` has no time zone | – |
   | 400 | `INVALID_TIME_RANGE` | `end_at` is not after `start_at`, or the slot spans two days | – |
   | 400 | `PAST_APPOINTMENT` | the slot is in the past | – |
   | 400 | `OUTSIDE_WORKING_HOURS` | the slot is on Sunday or outside 08:00-18:00 (UTC+7) | – |
   | 400 | `TICKET_CLOSED` | the ticket is finished (`HOAN_TAT`, `DA_DONG`, `DA_HUY`) | – |
   | 409 | `APPOINTMENT_OVERLAP` | the technician already has an appointment in this slot; the response lists `conflicts` and `free_slots` | – |
   | 403 | `FORBIDDEN` | the ticket belongs to another center (manager) or to another technician | – |
   | 404 | `APPOINTMENT_NOT_FOUND` | no appointment with this id | – |
   | 409 | `APPOINTMENT_NOT_EDITABLE` | the appointment is not `DA_HEN` (already cancelled or done) | – |

### 18. `DELETE /api/appointments/{appointment_id}`

1. **Method and path:** `DELETE` `/api/appointments/{appointment_id}`
2. **Purpose:** Soft cancel: the status becomes `DA_HUY` and the slot becomes free.
3. **Authentication and role:** Bearer token – any role, limited to the user's scope.
4. **Parameters:** Path: `appointment_id`.
5. **Request body:** none.
6. **Success response** – HTTP 200:
   ```json
   {
     "appointment_id": 302,
     "ticket_id": 7803,
     "technician_id": 20,
     "appointment_type": "NHAN",
     "start_at": "2027-01-14T03:00:00Z",
     "end_at": "2027-01-14T04:00:00Z",
     "status": "DA_HUY",
     "note": "API-DOC đổi giờ"
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 401 | `UNAUTHORIZED` | no token, or a malformed `Authorization` header | – |
   | 401 | `INVALID_TOKEN` | the token is expired or altered | – |
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |
   | 400 | `VALIDATION_ERROR` | the body or a parameter has the wrong type or is out of range; the response lists `fields` | – |
   | 403 | `FORBIDDEN` | the ticket belongs to another center (manager) or to another technician | – |
   | 404 | `APPOINTMENT_NOT_FOUND` | no appointment with this id | – |
   | 409 | `APPOINTMENT_NOT_CANCELLABLE` | the appointment is not `DA_HEN` | yes – cancel it again |

## 5. Health

### 19. `GET /`

1. **Method and path:** `GET` `/`
2. **Purpose:** Liveness check of the web server.
3. **Authentication and role:** Public – no token.
4. **Parameters:** None.
5. **Request body:** none.
6. **Success response** – HTTP 200:
   ```text
   Hello Smart CRM
   ```
7. **Error codes:** none specific to this endpoint.

### 20. `GET /db-check`

1. **Method and path:** `GET` `/db-check`
2. **Purpose:** Check that the API can reach PostgreSQL; used by the Docker healthcheck.
3. **Authentication and role:** Public – no token.
4. **Parameters:** None.
5. **Request body:** none.
6. **Success response** – HTTP 200:
   ```json
   {
     "database_time": "2026-11-14T18:35:11.940246Z"
   }
   ```
7. **Error codes:**

   | HTTP | Code | When | Captured |
   |---|---|---|---|
   | 503 | `DATABASE_UNAVAILABLE` | the database does not answer within `DB_CONNECT_TIMEOUT` seconds | – |

## 6. Error summary

| HTTP | Meaning | Codes |
|---|---|---|
| 400 | Invalid input or a broken business rule | `VALIDATION_ERROR` (with `fields`), `INVALID_PHONE`, `REQUIRED_FIELD_BLANK`, `INVALID_STATUS`, `INVALID_PRIORITY`, `INVALID_CATEGORY`, `INVALID_DUE_DATE`, `INVALID_DATETIME`, `TECHNICIAN_NOT_ELIGIBLE`, `REASON_REQUIRED`, `SAME_TECHNICIAN`, `INVALID_TIME_RANGE`, `PAST_APPOINTMENT`, `OUTSIDE_WORKING_HOURS`, `TICKET_NOT_ASSIGNED`, `TICKET_CLOSED` |
| 401 | Not logged in, expired or altered token, wrong password | `UNAUTHORIZED`, `INVALID_TOKEN`, `INVALID_CREDENTIALS` |
| 403 | Wrong role, another center's ticket, another technician's ticket | `FORBIDDEN` |
| 404 | Record does not exist | `TICKET_NOT_FOUND`, `TECHNICIAN_NOT_FOUND`, `APPOINTMENT_NOT_FOUND` |
| 409 | Valid request, but the current state forbids it | `TICKET_ALREADY_ASSIGNED`, `INVALID_STATUS_TRANSITION`, `TICKET_NOT_CHANGEABLE`, `TICKET_NOT_EDITABLE`, `TICKET_NOT_CANCELLABLE`, `TICKET_NOT_ASSIGNED`, `APPOINTMENT_OVERLAP`, `APPOINTMENT_NOT_EDITABLE`, `APPOINTMENT_NOT_CANCELLABLE` |
| 503 | Database or login configuration unavailable | `DATABASE_UNAVAILABLE`, `DEMO_ACCOUNTS_NOT_READY`, `AUTH_CONFIGURATION_ERROR` |
| 500 | Unexpected error (logged on the server) | `INTERNAL_ERROR` |

`TICKET_NOT_ASSIGNED` is returned with 400 when booking an appointment for a ticket without a technician (invalid input, SRS UC6) and with 409 when changing the technician of a ticket that has none (state conflict, UC4).
