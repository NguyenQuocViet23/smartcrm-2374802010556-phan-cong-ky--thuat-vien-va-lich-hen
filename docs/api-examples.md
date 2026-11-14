# API examples captured from a real run

Captured on 15/11/2026 01:35 (UTC+7) by `scripts/capture_api_examples.py` against `http://localhost:8000` (Docker Compose stack, sample data `data/sample/`, code at commit `f047797`).
Every request below was sent and every response was received; nothing is invented. Tokens are shortened and long lists keep their first items, as noted under each example. `<DEMO_PASSWORD>` stands for the value in `.env`.

## GET /

### service is up → HTTP 200

```http
GET /
no Authorization header
```

```json
"Hello Smart CRM"
```

## GET /db-check

### database answers → HTTP 200

```http
GET /db-check
no Authorization header
```

```json
{
  "database_time": "2026-11-14T18:35:11.940246Z"
}
```

## POST /api/auth/login

### valid account → HTTP 200

```http
POST /api/auth/login
no Authorization header
Content-Type: application/json

{
  "username": "QL_TT01",
  "password": "<DEMO_PASSWORD>"
}
```

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5…",
  "token_type": "bearer"
}
```

*Note: the token is shortened.*

### wrong password → HTTP 401

```http
POST /api/auth/login
no Authorization header
Content-Type: application/json

{
  "username": "QL_TT01",
  "password": "wrong-password"
}
```

```json
{
  "error": "INVALID_CREDENTIALS",
  "message": "Sai tên đăng nhập hoặc mật khẩu"
}
```

### body without the required fields → HTTP 400

```http
POST /api/auth/login
no Authorization header
Content-Type: application/json

{}
```

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Dữ liệu gửi lên không hợp lệ.",
  "fields": [
    {
      "field": "body.username",
      "message": "Field required"
    },
    {
      "field": "body.password",
      "message": "Field required"
    }
  ]
}
```

## GET /api/auth/me

### manager → HTTP 200

```http
GET /api/auth/me
Authorization: Bearer <token of QL_TT01>
```

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

### no token → HTTP 401

```http
GET /api/auth/me
no Authorization header
```

```json
{
  "error": "UNAUTHORIZED",
  "message": "Vui lòng đăng nhập."
}
```

## GET /api/tickets

### new tickets of the manager's center → HTTP 200

```http
GET /api/tickets?status=MOI&page=1&page_size=2
Authorization: Bearer <token of QL_TT01>
```

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

### invalid status filter → HTTP 400

```http
GET /api/tickets?status=XX
Authorization: Bearer <token of QL_TT01>
```

```json
{
  "error": "INVALID_STATUS",
  "message": "Trạng thái phiếu không hợp lệ."
}
```

### page number out of range → HTTP 400

```http
GET /api/tickets?page=0
Authorization: Bearer <token of QL_TT01>
```

```json
{
  "error": "VALIDATION_ERROR",
  "message": "Dữ liệu gửi lên không hợp lệ.",
  "fields": [
    {
      "field": "query.page",
      "message": "Input should be greater than or equal to 1"
    }
  ]
}
```

## POST /api/tickets

### valid ticket → HTTP 201

```http
POST /api/tickets
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

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

### invalid phone number → HTTP 400

```http
POST /api/tickets
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "customer_name": "Nguyễn Văn An (API-DOC)",
  "customer_phone": "09123",
  "serial_no": "SN-API-DOC-01",
  "issue_desc": "Máy không lên nguồn sau khi rơi",
  "category_code": "PIN",
  "priority": "CAO",
  "due_date": "2026-11-22T17:00:00+07:00"
}
```

```json
{
  "error": "INVALID_PHONE",
  "message": "Số điện thoại phải gồm 10 chữ số và bắt đầu bằng 0."
}
```

### required fields only spaces → HTTP 400

```http
POST /api/tickets
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "customer_name": "   ",
  "customer_phone": "0912 345 678",
  "serial_no": "   ",
  "issue_desc": "   ",
  "category_code": "PIN",
  "priority": "CAO",
  "due_date": "2026-11-22T17:00:00+07:00"
}
```

```json
{
  "error": "REQUIRED_FIELD_BLANK",
  "message": "Các trường bắt buộc không được để trống hoặc chỉ có khoảng trắng: customer_name, serial_no, issue_desc.",
  "fields": [
    "customer_name",
    "serial_no"
  ]
}
```

*Note: a list of 3 items is shortened to its first 2.*

### second ticket for update and cancel → HTTP 201

```http
POST /api/tickets
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "customer_name": "Nguyễn Văn An (API-DOC)",
  "customer_phone": "0912 345 678",
  "serial_no": "SN-API-DOC-02",
  "issue_desc": "Máy không lên nguồn sau khi rơi",
  "category_code": "PIN",
  "priority": "CAO",
  "due_date": "2026-11-22T17:00:00+07:00"
}
```

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
  "closed_at": null
}
```

## GET /api/tickets/{ticket_id}

### manager reads a ticket of the center → HTTP 200

```http
GET /api/tickets/7804
Authorization: Bearer <token of QL_TT01>
```

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

### ticket does not exist → HTTP 404

```http
GET /api/tickets/99999999
Authorization: Bearer <token of QL_TT01>
```

```json
{
  "error": "TICKET_NOT_FOUND",
  "message": "Không tìm thấy phiếu."
}
```

### technician reads own ticket (phone masked) → HTTP 200

```http
GET /api/tickets/7803
Authorization: Bearer <token of KT020>
```

```json
{
  "ticket_id": 7803,
  "ticket_code": "BH-007803/2026",
  "center_id": 1,
  "customer_name": "Nguyễn Văn An (API-DOC)",
  "customer_phone": "091****678",
  "serial_no": "SN-API-DOC-01",
  "issue_desc": "Máy không lên nguồn sau khi rơi",
  "category_code": "PIN",
  "priority": "CAO",
  "status": "DANG_XU_LY",
  "technician_id": 20,
  "received_at": "2026-11-14T18:35:12.174572Z",
  "due_date": "2026-11-22T10:00:00Z",
  "closed_at": null,
  "technician": {
    "technician_id": 20,
    "technician_code": "KT020",
    "full_name": "Trần Văn Thảo",
    "level": "TRUNG_CAP"
  },
  "status_history": [
    {
      "log_id": 38119,
      "event_type": "TRANG_THAI",
      "from_status": null,
      "to_status": "MOI",
      "from_technician_id": null,
      "from_technician_code": null,
      "to_technician_id": null,
      "to_technician_code": null,
      "changed_by": 1,
      "changed_at": "2026-11-14T18:35:12.174572Z",
      "note": "Tạo phiếu"
    },
    {
      "log_id": 38122,
      "event_type": "TRANG_THAI",
      "from_status": "MOI",
      "to_status": "DA_PHAN_CONG",
      "from_technician_id": null,
      "from_technician_code": null,
      "to_technician_id": 33,
      "to_technician_code": "KT033",
      "changed_by": 1,
      "changed_at": "2026-11-14T18:35:12.337797Z",
      "note": null
    }
  ]
}
```

*Note: a list of 4 items is shortened to its first 2.*

## PUT /api/tickets/{ticket_id}

### correct a MOI ticket → HTTP 200

```http
PUT /api/tickets/7804
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

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

### required field only spaces → HTTP 400

```http
PUT /api/tickets/7804
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "customer_name": "Nguyễn Văn An (API-DOC)",
  "customer_phone": "0912 345 678",
  "serial_no": "SN-API-DOC-01",
  "issue_desc": "   ",
  "category_code": "PIN",
  "priority": "CAO",
  "due_date": "2026-11-22T17:00:00+07:00"
}
```

```json
{
  "error": "REQUIRED_FIELD_BLANK",
  "message": "Các trường bắt buộc không được để trống hoặc chỉ có khoảng trắng: issue_desc.",
  "fields": [
    "issue_desc"
  ]
}
```

## DELETE /api/tickets/{ticket_id}

### soft cancel a MOI ticket → HTTP 200

```http
DELETE /api/tickets/7804?reason=Khach%20huy%20yeu%20cau
Authorization: Bearer <token of QL_TT01>
```

```json
{
  "ticket_id": 7804,
  "ticket_code": "BH-007804/2026",
  "status": "DA_HUY",
  "closed_at": "2026-11-14T18:35:12.245961Z"
}
```

### cancel it again → HTTP 409

```http
DELETE /api/tickets/7804
Authorization: Bearer <token of QL_TT01>
```

```json
{
  "error": "TICKET_NOT_CANCELLABLE",
  "message": "Chỉ hủy được phiếu ở trạng thái MỚI."
}
```

## GET /api/tickets/{ticket_id}/technician-suggestions

### eligible technicians → HTTP 200

```http
GET /api/tickets/7803/technician-suggestions
Authorization: Bearer <token of QL_TT01>
```

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

### a technician is not allowed → HTTP 403

```http
GET /api/tickets/7803/technician-suggestions
Authorization: Bearer <token of KT033>
```

```json
{
  "error": "FORBIDDEN",
  "message": "Bạn không có quyền thực hiện thao tác này."
}
```

## POST /api/tickets/{ticket_id}/assignment

### assign an eligible technician → HTTP 201

```http
POST /api/tickets/7803/assignment
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "technician_id": 33
}
```

```json
{
  "ticket_id": 7803,
  "status": "DA_PHAN_CONG",
  "technician_id": 33,
  "assigned_by": 1,
  "assigned_at": "2026-11-14T18:35:12.337797Z"
}
```

### ticket already has a technician → HTTP 409

```http
POST /api/tickets/7803/assignment
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "technician_id": 20
}
```

```json
{
  "error": "TICKET_ALREADY_ASSIGNED",
  "message": "Phiếu đã được phân công cho kỹ thuật viên KT033."
}
```

## PUT /api/tickets/{ticket_id}/assignment

### change the technician with a reason → HTTP 200

```http
PUT /api/tickets/7803/assignment
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "technician_id": 20,
  "reason": "Kỹ thuật viên cũ nghỉ ốm"
}
```

```json
{
  "ticket_id": 7803,
  "status": "DA_PHAN_CONG",
  "technician_id": 20
}
```

### reason only spaces → HTTP 400

```http
PUT /api/tickets/7803/assignment
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "technician_id": 33,
  "reason": "   "
}
```

```json
{
  "error": "REASON_REQUIRED",
  "message": "Lý do đổi kỹ thuật viên là bắt buộc."
}
```

## GET /api/technicians/me/tickets

### technician's own tickets → HTTP 200

```http
GET /api/technicians/me/tickets
Authorization: Bearer <token of KT020>
```

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

*Note: a list of 49 items is shortened to its first 2.*

### a manager is not allowed → HTTP 403

```http
GET /api/technicians/me/tickets
Authorization: Bearer <token of QL_TT01>
```

```json
{
  "error": "FORBIDDEN",
  "message": "Bạn không có quyền thực hiện thao tác này."
}
```

## PATCH /api/tickets/{ticket_id}/status

### start work (owner technician) → HTTP 200

```http
PATCH /api/tickets/7803/status
Authorization: Bearer <token of KT020>
Content-Type: application/json

{
  "to_status": "DANG_XU_LY",
  "note": "Bắt đầu kiểm tra máy"
}
```

```json
{
  "ticket_id": 7803,
  "status": "DANG_XU_LY",
  "technician_id": 20
}
```

### go back to an earlier status → HTTP 400

```http
PATCH /api/tickets/7803/status
Authorization: Bearer <token of KT020>
Content-Type: application/json

{
  "to_status": "DA_PHAN_CONG"
}
```

```json
{
  "error": "INVALID_STATUS",
  "message": "Trạng thái đích không hợp lệ."
}
```

### a manager is not allowed → HTTP 403

```http
PATCH /api/tickets/7803/status
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "to_status": "HOAN_TAT"
}
```

```json
{
  "error": "FORBIDDEN",
  "message": "Bạn không có quyền thực hiện thao tác này."
}
```

## POST /api/appointments

### valid slot 09:00-10:00 → HTTP 201

```http
POST /api/appointments
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "ticket_id": 7803,
  "appointment_type": "NHAN",
  "note": "API-DOC",
  "start_at": "2027-01-14T09:00:00+07:00",
  "end_at": "2027-01-14T10:00:00+07:00"
}
```

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

### overlapping slot → HTTP 409

```http
POST /api/appointments
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "ticket_id": 7803,
  "appointment_type": "NHAN",
  "note": "API-DOC",
  "start_at": "2027-01-14T09:30:00+07:00",
  "end_at": "2027-01-14T10:30:00+07:00"
}
```

```json
{
  "error": "APPOINTMENT_OVERLAP",
  "message": "Kỹ thuật viên đã có lịch trong khung giờ này.",
  "conflicts": [
    {
      "appointment_id": 302,
      "ticket_code": "BH-007803/2026",
      "start_at": "2027-01-14T02:00:00+00:00",
      "end_at": "2027-01-14T03:00:00+00:00"
    }
  ],
  "free_slots": [
    {
      "start_at": "2027-01-14T10:00:00+07:00",
      "end_at": "2027-01-14T10:30:00+07:00"
    },
    {
      "start_at": "2027-01-14T08:30:00+07:00",
      "end_at": "2027-01-14T09:00:00+07:00"
    }
  ]
}
```

### end before start → HTTP 400

```http
POST /api/appointments
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "ticket_id": 7803,
  "appointment_type": "NHAN",
  "note": "API-DOC",
  "start_at": "2027-01-14T11:00:00+07:00",
  "end_at": "2027-01-14T10:00:00+07:00"
}
```

```json
{
  "error": "INVALID_TIME_RANGE",
  "message": "Giờ kết thúc phải sau giờ bắt đầu."
}
```

### outside working hours → HTTP 400

```http
POST /api/appointments
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "ticket_id": 7803,
  "appointment_type": "NHAN",
  "note": "API-DOC",
  "start_at": "2027-01-14T20:00:00+07:00",
  "end_at": "2027-01-14T21:00:00+07:00"
}
```

```json
{
  "error": "OUTSIDE_WORKING_HOURS",
  "message": "Giờ làm việc là 08:00–18:00."
}
```

### slot in the past → HTTP 400

```http
POST /api/appointments
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "ticket_id": 7803,
  "appointment_type": "NHAN",
  "note": "API-DOC",
  "start_at": "2026-11-12T09:00:12.503365+07:00",
  "end_at": "2026-11-12T10:00:12.503365+07:00"
}
```

```json
{
  "error": "PAST_APPOINTMENT",
  "message": "Thời điểm hẹn phải ở tương lai."
}
```

## GET /api/tickets/{ticket_id}/appointments

### appointments of the ticket → HTTP 200

```http
GET /api/tickets/7803/appointments
Authorization: Bearer <token of QL_TT01>
```

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

## GET /api/appointments

### appointments of the ticket (filter) → HTTP 200

```http
GET /api/appointments?ticket_id=7803
Authorization: Bearer <token of QL_TT01>
```

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

## GET /api/appointments/{appointment_id}

### one appointment → HTTP 200

```http
GET /api/appointments/302
Authorization: Bearer <token of QL_TT01>
```

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

### appointment does not exist → HTTP 404

```http
GET /api/appointments/99999999
Authorization: Bearer <token of QL_TT01>
```

```json
{
  "error": "APPOINTMENT_NOT_FOUND",
  "message": "Không tìm thấy lịch hẹn."
}
```

## PUT /api/appointments/{appointment_id}

### reschedule to 10:00-11:00 → HTTP 200

```http
PUT /api/appointments/302
Authorization: Bearer <token of QL_TT01>
Content-Type: application/json

{
  "appointment_type": "NHAN",
  "note": "API-DOC đổi giờ",
  "start_at": "2027-01-14T10:00:00+07:00",
  "end_at": "2027-01-14T11:00:00+07:00"
}
```

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

## DELETE /api/appointments/{appointment_id}

### soft cancel → HTTP 200

```http
DELETE /api/appointments/302
Authorization: Bearer <token of QL_TT01>
```

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

### cancel it again → HTTP 409

```http
DELETE /api/appointments/302
Authorization: Bearer <token of QL_TT01>
```

```json
{
  "error": "APPOINTMENT_NOT_CANCELLABLE",
  "message": "Lịch hẹn này đã được hủy trước đó."
}
```
