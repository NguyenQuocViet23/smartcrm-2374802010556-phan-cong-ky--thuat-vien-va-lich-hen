"""Call every API endpoint on a running backend and write the real requests and responses
to docs/api-examples.md, so docs/api.md can quote them instead of invented examples.

It only uses the standard library and needs a backend loaded with the sample data, for example
the Docker Compose stack (`docker compose up -d --build backend`).

Usage:
    DEMO_PASSWORD=<value from .env> python scripts/capture_api_examples.py [output.md]
Environment: API_BASE_URL (default http://localhost:8000), DEMO_PASSWORD (required).

The script creates its own tickets and appointments (marked "API-DOC") and leaves the sample
tickets untouched, but it does write to the database: run it on a throw-away stack.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")
PASSWORD = os.environ["DEMO_PASSWORD"]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "api-examples.md"
TZ = timezone(timedelta(hours=7))

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

TOKENS: dict[str, str] = {}
EXAMPLES: list[dict] = []  # in call order; grouped by endpoint when written
ORDER: list[str] = []


def raw_call(method: str, path: str, token: str | None, body) -> tuple[int, object]:
    data = json.dumps(body).encode("utf-8") if body is not None else None
    request = urllib.request.Request(BASE + path, data=data, method=method)
    if data is not None:
        request.add_header("Content-Type", "application/json")
    if token:
        request.add_header("Authorization", f"Bearer {token}")
    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            status, text = response.status, response.read().decode("utf-8")
    except urllib.error.HTTPError as error:
        status, text = error.code, error.read().decode("utf-8")
    try:
        return status, json.loads(text)
    except ValueError:
        return status, text


def login(username: str) -> str:
    if username not in TOKENS:
        status, body = raw_call("POST", "/api/auth/login", None, {"username": username, "password": PASSWORD})
        if status != 200:
            raise SystemExit(f"cannot log in as {username}: {status} {body}")
        TOKENS[username] = body["access_token"]
    return TOKENS[username]


def shorten(value, notes: list[str]):
    """Keep examples readable: only the first element of long lists, and no full tokens."""
    if isinstance(value, dict):
        out = {}
        for key, item in value.items():
            if key == "access_token" and isinstance(item, str):
                out[key] = item[:24] + "…"
                notes.append("the token is shortened")
            else:
                out[key] = shorten(item, notes)
        return out
    if isinstance(value, list) and len(value) > 2:
        notes.append(f"a list of {len(value)} items is shortened to its first 2")
        return [shorten(item, notes) for item in value[:2]]
    if isinstance(value, list):
        return [shorten(item, notes) for item in value]
    return value


def example(endpoint: str, title: str, method: str, path: str, who: str | None, body=None, shown=None):
    """Send the request; `shown` replaces the body in the document (used to hide the real password)."""
    token = login(who) if who else None
    status, response = raw_call(method, path, token, body)
    notes: list[str] = []
    EXAMPLES.append({
        "endpoint": endpoint, "title": title, "method": method, "path": path, "who": who,
        "body": shown if shown is not None else body, "status": status, "response": shorten(response, notes), "notes": sorted(set(notes)),
    })
    if endpoint not in ORDER:
        ORDER.append(endpoint)
    print(f"{status}  {method} {path}  [{title}]")
    return status, response


def find_list(value, key: str):
    """Return the first list of dicts that contain `key` anywhere inside a response."""
    if isinstance(value, list) and value and isinstance(value[0], dict) and key in value[0]:
        return value
    if isinstance(value, dict):
        for item in value.values():
            found = find_list(item, key)
            if found:
                return found
    return None


def ticket_body(**overrides) -> dict:
    due = (datetime.now(TZ) + timedelta(days=7)).replace(hour=17, minute=0, second=0, microsecond=0)
    body = {
        "customer_name": "Nguyễn Văn An (API-DOC)", "customer_phone": "0912 345 678",
        "serial_no": "SN-API-DOC-01", "issue_desc": "Máy không lên nguồn sau khi rơi",
        "category_code": "PIN", "priority": "CAO", "due_date": due.isoformat(),
    }
    body.update(overrides)
    return body


def free_monday_to_saturday(days_ahead: int) -> datetime:
    day = datetime.now(TZ) + timedelta(days=days_ahead)
    while day.weekday() == 6:  # Sunday is not a working day
        day += timedelta(days=1)
    return day.replace(hour=0, minute=0, second=0, microsecond=0)


def slot(day: datetime, start: str, end: str) -> dict:
    start_at = day.replace(hour=int(start[:2]), minute=int(start[3:]))
    end_at = day.replace(hour=int(end[:2]), minute=int(end[3:]))
    return {"start_at": start_at.isoformat(), "end_at": end_at.isoformat()}


def run() -> None:
    manager = "QL_TT01"

    # ---- health ----
    example("GET /", "service is up", "GET", "/", None)
    example("GET /db-check", "database answers", "GET", "/db-check", None)

    # ---- authentication ----
    example("POST /api/auth/login", "valid account", "POST", "/api/auth/login", None,
            {"username": manager, "password": PASSWORD},
            shown={"username": manager, "password": "<DEMO_PASSWORD>"})
    example("POST /api/auth/login", "wrong password", "POST", "/api/auth/login", None,
            {"username": manager, "password": "wrong-password"})
    example("POST /api/auth/login", "body without the required fields", "POST", "/api/auth/login", None, {})
    example("GET /api/auth/me", "manager", "GET", "/api/auth/me", manager)
    example("GET /api/auth/me", "no token", "GET", "/api/auth/me", None)

    # ---- tickets: list, create, read, update, cancel ----
    status, listing = example("GET /api/tickets", "new tickets of the manager's center", "GET",
                              "/api/tickets?status=MOI&page=1&page_size=2", manager)
    example("GET /api/tickets", "invalid status filter", "GET", "/api/tickets?status=XX", manager)
    example("GET /api/tickets", "page number out of range", "GET", "/api/tickets?page=0", manager)

    status, created = example("POST /api/tickets", "valid ticket", "POST", "/api/tickets", manager, ticket_body())
    flow_id = created["ticket_id"]
    example("POST /api/tickets", "invalid phone number", "POST", "/api/tickets", manager,
            ticket_body(customer_phone="09123"))
    example("POST /api/tickets", "required fields only spaces", "POST", "/api/tickets", manager,
            ticket_body(customer_name="   ", serial_no="   ", issue_desc="   "))

    status, spare = example("POST /api/tickets", "second ticket for update and cancel", "POST",
                            "/api/tickets", manager, ticket_body(serial_no="SN-API-DOC-02"))
    spare_id = spare["ticket_id"]
    example("GET /api/tickets/{ticket_id}", "manager reads a ticket of the center", "GET",
            f"/api/tickets/{spare_id}", manager)
    example("GET /api/tickets/{ticket_id}", "ticket does not exist", "GET", "/api/tickets/99999999", manager)
    example("PUT /api/tickets/{ticket_id}", "correct a MOI ticket", "PUT", f"/api/tickets/{spare_id}", manager,
            ticket_body(serial_no="SN-API-DOC-02", issue_desc="Màn hình bị sọc ngang"))
    example("PUT /api/tickets/{ticket_id}", "required field only spaces", "PUT", f"/api/tickets/{spare_id}",
            manager, ticket_body(issue_desc="   "))
    example("DELETE /api/tickets/{ticket_id}", "soft cancel a MOI ticket", "DELETE",
            f"/api/tickets/{spare_id}?reason=Khach%20huy%20yeu%20cau", manager)
    example("DELETE /api/tickets/{ticket_id}", "cancel it again", "DELETE", f"/api/tickets/{spare_id}", manager)

    # ---- tickets: suggestions, assignment, status ----
    status, suggestions = example("GET /api/tickets/{ticket_id}/technician-suggestions", "eligible technicians",
                                  "GET", f"/api/tickets/{flow_id}/technician-suggestions", manager)
    items = find_list(suggestions, "technician_id") or []
    if len(items) < 2:
        raise SystemExit(f"need at least two suggested technicians, got: {suggestions}")
    first, second = items[0], items[1]
    code = lambda item: item.get("technician_code") or item.get("employee_id") or item.get("username")  # noqa: E731

    example("GET /api/tickets/{ticket_id}/technician-suggestions", "a technician is not allowed", "GET",
            f"/api/tickets/{flow_id}/technician-suggestions", code(first))
    example("POST /api/tickets/{ticket_id}/assignment", "assign an eligible technician", "POST",
            f"/api/tickets/{flow_id}/assignment", manager, {"technician_id": first["technician_id"]})
    example("POST /api/tickets/{ticket_id}/assignment", "ticket already has a technician", "POST",
            f"/api/tickets/{flow_id}/assignment", manager, {"technician_id": second["technician_id"]})
    example("PUT /api/tickets/{ticket_id}/assignment", "change the technician with a reason", "PUT",
            f"/api/tickets/{flow_id}/assignment", manager,
            {"technician_id": second["technician_id"], "reason": "Kỹ thuật viên cũ nghỉ ốm"})
    example("PUT /api/tickets/{ticket_id}/assignment", "reason only spaces", "PUT",
            f"/api/tickets/{flow_id}/assignment", manager, {"technician_id": first["technician_id"], "reason": "   "})

    tech = code(second)
    example("GET /api/technicians/me/tickets", "technician's own tickets", "GET",
            "/api/technicians/me/tickets", tech)
    example("GET /api/technicians/me/tickets", "a manager is not allowed", "GET",
            "/api/technicians/me/tickets", manager)
    example("PATCH /api/tickets/{ticket_id}/status", "start work (owner technician)", "PATCH",
            f"/api/tickets/{flow_id}/status", tech, {"to_status": "DANG_XU_LY", "note": "Bắt đầu kiểm tra máy"})
    example("PATCH /api/tickets/{ticket_id}/status", "go back to an earlier status", "PATCH",
            f"/api/tickets/{flow_id}/status", tech, {"to_status": "DA_PHAN_CONG"})
    example("PATCH /api/tickets/{ticket_id}/status", "a manager is not allowed", "PATCH",
            f"/api/tickets/{flow_id}/status", manager, {"to_status": "HOAN_TAT"})
    example("GET /api/tickets/{ticket_id}", "technician reads own ticket (phone masked)", "GET",
            f"/api/tickets/{flow_id}", tech)

    # ---- appointments ----
    day = free_monday_to_saturday(60)
    appointment = {"ticket_id": flow_id, "appointment_type": "NHAN", "note": "API-DOC"}
    status, booked = example("POST /api/appointments", "valid slot 09:00-10:00", "POST", "/api/appointments",
                             manager, {**appointment, **slot(day, "09:00", "10:00")})
    appointment_id = booked["appointment_id"]
    example("POST /api/appointments", "overlapping slot", "POST", "/api/appointments", manager,
            {**appointment, **slot(day, "09:30", "10:30")})
    example("POST /api/appointments", "end before start", "POST", "/api/appointments", manager,
            {**appointment, **slot(day, "11:00", "10:00")})
    example("POST /api/appointments", "outside working hours", "POST", "/api/appointments", manager,
            {**appointment, **slot(day, "20:00", "21:00")})
    past = datetime.now(TZ) - timedelta(days=3)
    example("POST /api/appointments", "slot in the past", "POST", "/api/appointments", manager,
            {**appointment, **slot(past.replace(hour=0, minute=0), "09:00", "10:00")})
    example("GET /api/tickets/{ticket_id}/appointments", "appointments of the ticket", "GET",
            f"/api/tickets/{flow_id}/appointments", manager)
    example("GET /api/appointments", "appointments of the ticket (filter)", "GET",
            f"/api/appointments?ticket_id={flow_id}", manager)
    example("GET /api/appointments/{appointment_id}", "one appointment", "GET",
            f"/api/appointments/{appointment_id}", manager)
    example("GET /api/appointments/{appointment_id}", "appointment does not exist", "GET",
            "/api/appointments/99999999", manager)
    example("PUT /api/appointments/{appointment_id}", "reschedule to 10:00-11:00", "PUT",
            f"/api/appointments/{appointment_id}", manager,
            {"appointment_type": "NHAN", "note": "API-DOC đổi giờ", **slot(day, "10:00", "11:00")})
    example("DELETE /api/appointments/{appointment_id}", "soft cancel", "DELETE",
            f"/api/appointments/{appointment_id}", manager)
    example("DELETE /api/appointments/{appointment_id}", "cancel it again", "DELETE",
            f"/api/appointments/{appointment_id}", manager)


def write_markdown() -> None:
    commit = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=ROOT, capture_output=True,
                            text=True).stdout.strip()
    lines = [
        "# API examples captured from a real run",
        "",
        f"Captured on {datetime.now(TZ):%d/%m/%Y %H:%M} (UTC+7) by `scripts/capture_api_examples.py` against "
        f"`{BASE}` (Docker Compose stack, sample data `data/sample/`, code at commit `{commit}`).",
        "Every request below was sent and every response was received; nothing is invented. Tokens are shortened and "
        "long lists keep their first items, as noted under each example. `<DEMO_PASSWORD>` stands for the value in `.env`.",
        "",
    ]
    for endpoint in ORDER:
        lines += [f"## {endpoint}", ""]
        for item in (e for e in EXAMPLES if e["endpoint"] == endpoint):
            auth = f"Authorization: Bearer <token of {item['who']}>" if item["who"] else "no Authorization header"
            lines += [f"### {item['title']} → HTTP {item['status']}", "", "```http",
                      f"{item['method']} {item['path']}", auth]
            if item["body"] is not None:
                lines += ["Content-Type: application/json", "", json.dumps(item["body"], indent=2, ensure_ascii=False)]
            lines += ["```", "", "```json", json.dumps(item["response"], indent=2, ensure_ascii=False), "```", ""]
            if item["notes"]:
                lines += [f"*Note: {'; '.join(item['notes'])}.*", ""]
    OUT.write_text("\n".join(lines), encoding="utf-8")
    print(f"wrote {OUT} ({len(EXAMPLES)} examples, {len(ORDER)} endpoints)")


if __name__ == "__main__":
    run()
    write_markdown()
