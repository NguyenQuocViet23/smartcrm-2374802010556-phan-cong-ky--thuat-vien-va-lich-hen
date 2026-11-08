# API Reference – Smart CRM (L04)

Base URL: `http://localhost:8000` · Interactive documentation generated from the code: `/docs` (Swagger UI).
All bodies are JSON; times are ISO 8601 **with a time zone** (for example `2026-12-08T09:00:00+07:00`).
Ticket statuses: `MOI → DA_PHAN_CONG → DANG_XU_LY → (CHO_LINH_KIEN) → HOAN_TAT`, plus `DA_DONG`, `DA_HUY`.

## 1. Authentication

Log in with a demo account, then send the token on every other call:
`Authorization: Bearer <access_token>`. A token is valid for 8 hours.

| Method | Path | Role | Description |
|---|---|---|---|
| POST | `/api/auth/login` | public | Body `{"username": "QL_TT01", "password": "<DEMO_PASSWORD>"}` → 200 `{"access_token": "...", "token_type": "bearer"}`; 401 `INVALID_CREDENTIALS` |
| GET | `/api/auth/me` | any | 200 `{"role", "center_id", "center_name", "technician_id", "full_name", "employee_id"}` |

Roles: `QUAN_LY` (center manager, accounts `QL_TT01…QL_TT06`) and `KY_THUAT_VIEN` (technician, accounts named by
`technician_code`, e.g. `KT002`). Access rules: a manager sees only tickets of their own center; a technician sees
only tickets assigned to them, with the customer phone masked (`091****678`).

## 2. Tickets

| Method | Path | Role | Description |
|---|---|---|---|
| GET | `/api/tickets?status=MOI&category_code=&priority=&page=1&page_size=20` | manager | Tickets of the manager's center → `{"items": [...], "total", "page", "page_size"}`. `page_size` 1–100 |
| POST | `/api/tickets` | manager | Create a new ticket (status `MOI`) in the manager's center → 201 with the ticket |
| GET | `/api/tickets/{ticket_id}` | any (scoped) | Ticket detail with `technician` and `status_history` |
| PUT | `/api/tickets/{ticket_id}` | manager | Correct a ticket that is still `MOI` |
| DELETE | `/api/tickets/{ticket_id}?reason=` | manager | Soft delete: a `MOI` ticket becomes `DA_HUY` (nothing is physically deleted) |
| GET | `/api/tickets/{ticket_id}/technician-suggestions` | manager | Eligible technicians: same center, active, proficiency ≥ 3, ordered by workload ascending |
| POST | `/api/tickets/{ticket_id}/assignment` | manager | Body `{"technician_id": 22}` → 201; ticket becomes `DA_PHAN_CONG` and the change is logged |
| PUT | `/api/tickets/{ticket_id}/assignment` | manager | Change technician; body `{"technician_id": 12, "reason": "..."}`; reason is required and not blank |
| PATCH | `/api/tickets/{ticket_id}/status` | technician (owner) | Body `{"to_status": "DANG_XU_LY", "note": "..."}`; only forward steps of the lifecycle |
| GET | `/api/tickets/{ticket_id}/appointments` | any (scoped) | Appointments of a ticket |
| GET | `/api/technicians/me/tickets` | technician | All tickets of the logged-in technician, ordered by due date, with `is_overdue` |

Ticket body for POST and PUT:

```json
{
  "customer_name": "Nguyễn Văn An",
  "customer_phone": "0912 345 678",
  "serial_no": "SN10293A",
  "issue_desc": "Máy không lên nguồn sau khi rơi",
  "category_code": "PIN",
  "priority": "CAO",
  "due_date": "2026-11-11T17:00:00+07:00"
}
```

- `customer_name`, `serial_no`, `issue_desc`: required and must not be blank (only spaces → 400 `REQUIRED_FIELD_BLANK`).
- `customer_phone`: normalised to 10 digits starting with 0; spaces, dots, dashes and `+84` are accepted.
- `category_code`: `MAN_HINH`, `PIN`, `SAC`, `PHAN_MEM`, `NUOC_VAO`, `KHAC` · `priority`: `CAO`, `TRUNG_BINH`, `THAP`.
- `due_date`: must include a time zone and lie in the future.

Response of `POST /api/tickets` (201):

```json
{"ticket_id": 7801, "ticket_code": "BH-007801/2026", "center_id": 1, "customer_name": "Nguyễn Văn An",
 "customer_phone": "0912345678", "serial_no": "SN10293A", "issue_desc": "Máy không lên nguồn sau khi rơi",
 "category_code": "PIN", "priority": "CAO", "status": "MOI", "technician_id": null,
 "received_at": "2026-11-08T16:34:36+07:00", "due_date": "2026-11-11T17:00:00+07:00", "closed_at": null}
```

## 3. Appointments

| Method | Path | Role | Description |
|---|---|---|---|
| POST | `/api/appointments` | any (scoped) | Book a delivery/pick-up slot → 201 |
| GET | `/api/appointments?status=&ticket_id=&page=&page_size=` | any | Manager: appointments of the center; technician: their own |
| GET | `/api/appointments/{appointment_id}` | any (scoped) | One appointment |
| PUT | `/api/appointments/{appointment_id}` | any (scoped) | Reschedule; overlap and working hours are checked again |
| DELETE | `/api/appointments/{appointment_id}` | any (scoped) | Soft cancel: status `DA_HUY`, the slot becomes free |

```json
{"ticket_id": 9, "appointment_type": "NHAN",
 "start_at": "2026-12-08T09:00:00+07:00", "end_at": "2026-12-08T10:00:00+07:00", "note": "optional"}
```

Rules: `appointment_type` is `GIAO` or `NHAN`; the slot must be in the future, Monday–Saturday, inside 08:00–18:00
(UTC+7), on one day, with `end_at > start_at`. The ticket must have a technician and must not be finished. The
appointment always belongs to the ticket's current technician. Slots are half-open `[start, end)`, so back-to-back
appointments (10:00–11:00 after 09:00–10:00) are allowed. An overlap returns 409 with the conflicts and the
nearest free 30-minute slots:

```json
{"error": "APPOINTMENT_OVERLAP", "message": "Kỹ thuật viên đã có lịch trong khung giờ này.",
 "conflicts": [{"appointment_id": 301, "ticket_code": "BH-000009/2026", "start_at": "...", "end_at": "..."}],
 "free_slots": [{"start_at": "2026-12-08T11:00:00+07:00", "end_at": "2026-12-08T11:30:00+07:00"}]}
```

## 4. Health

| Method | Path | Description |
|---|---|---|
| GET | `/` | `Hello Smart CRM` (plain text) |
| GET | `/db-check` | 200 `{"database_time": "..."}` when the database answers; used by the Docker healthcheck |

## 5. Errors

Every error has the same shape, `{"error": "<CODE>", "message": "<Vietnamese message>"}`, sometimes with extra fields
(`fields`, `conflicts`, `free_slots`). No error body contains a stack trace or SQL.

| HTTP | Meaning | Main codes |
|---|---|---|
| 400 | Invalid input or a broken business rule | `VALIDATION_ERROR` (with `fields`), `INVALID_PHONE`, `REQUIRED_FIELD_BLANK`, `INVALID_STATUS`, `INVALID_PRIORITY`, `INVALID_CATEGORY`, `INVALID_DUE_DATE`, `INVALID_DATETIME`, `TECHNICIAN_NOT_ELIGIBLE`, `REASON_REQUIRED`, `SAME_TECHNICIAN`, `INVALID_TIME_RANGE`, `PAST_APPOINTMENT`, `OUTSIDE_WORKING_HOURS`, `TICKET_NOT_ASSIGNED`, `TICKET_CLOSED` |
| 401 | Not logged in, expired or altered token, wrong password | `UNAUTHORIZED`, `INVALID_TOKEN`, `INVALID_CREDENTIALS` |
| 403 | Wrong role, another center's ticket, another technician's ticket | `FORBIDDEN` |
| 404 | Record does not exist | `TICKET_NOT_FOUND`, `TECHNICIAN_NOT_FOUND`, `APPOINTMENT_NOT_FOUND` |
| 409 | Valid request, but the current state forbids it | `TICKET_ALREADY_ASSIGNED`, `INVALID_STATUS_TRANSITION`, `TICKET_NOT_CHANGEABLE`, `TICKET_NOT_EDITABLE`, `TICKET_NOT_CANCELLABLE`, `APPOINTMENT_OVERLAP`, `APPOINTMENT_NOT_EDITABLE`, `APPOINTMENT_NOT_CANCELLABLE` |
| 503 | Database or login configuration unavailable | `DATABASE_UNAVAILABLE`, `DEMO_ACCOUNTS_NOT_READY`, `AUTH_CONFIGURATION_ERROR` |
| 500 | Unexpected error (logged on the server) | `INTERNAL_ERROR` |

`TICKET_NOT_ASSIGNED` is returned with 400 when booking an appointment for a ticket without a technician
(invalid input, SRS UC6) and with 409 when changing the technician of a ticket that has none (state conflict, UC4).
