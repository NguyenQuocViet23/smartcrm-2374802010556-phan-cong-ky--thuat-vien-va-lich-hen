"""BT3 test cases TC-01…TC-12 on the real backend and the real-data working database.

Each test builds its precondition with SQL on ``smartcrm_work_test`` (a fresh clone of
``smartcrm_test``), performs the step through Swagger served by the real backend, takes
a real screenshot, records what actually happened, and only then asserts the expected
result. Expected results come from docs/srs.md (sections 6–7) and the error contract
in README section 4.

Run all:   python -m pytest -m bt3
Run one:   python -m pytest -m bt3 -k TC05
"""

from __future__ import annotations

import base64
import json
import os
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timedelta, timezone
from urllib.parse import unquote, urlparse

import psycopg
import pytest
from playwright.sync_api import Page, expect
from psycopg import sql

from app.core.security import _b64encode
from tests.bt3.conftest import ROOT, start_record, shot
from tests.conftest import database_counts, get_test_database_url
from tests.integration.conftest import EXPECTED_COUNTS
from tests.real_system import (
    API_URL, UI_URL, System, _reachable, api, at, swagger_authorize, swagger_execute,
    token_for, ui_login,
)
from tests.service.test_suggestion import three_technicians_with_workloads

pytestmark = pytest.mark.bt3

NOT_LEAKED = ("Traceback", "psycopg", "sqlalchemy", "SELECT ", "File \"")


def iso(value: datetime) -> str:
    return value.isoformat()


def assigned_ticket(s: System) -> tuple[int, int, int, str]:
    """A real DA_PHAN_CONG ticket: (ticket_id, technician_id, center_id, ticket_code)."""
    return s.one(
        """SELECT ticket_id, technician_id, center_id, ticket_code FROM ticket
           WHERE status = 'DA_PHAN_CONG' ORDER BY ticket_id LIMIT 1"""
    )


def ticket_body(**override) -> dict:
    body = {
        "customer_name": "Nguyễn Văn An", "customer_phone": "0912345678",
        "serial_no": "SN10293A", "issue_desc": "Máy không lên nguồn sau khi rơi",
        "category_code": "PIN", "priority": "CAO",
        "due_date": iso(datetime.now(timezone(timedelta(hours=7))) + timedelta(days=3)),
    }
    body.update(override)
    return body


def no_leak(payload) -> bool:
    text = json.dumps(payload, ensure_ascii=False)
    return not any(word in text for word in NOT_LEAKED)


# --- 1. LUỒNG ĐÚNG -----------------------------------------------------------------


@pytest.mark.tc("TC-01")
def test_tc01_goi_y_dung_thu_tu(page: Page, bt3: System) -> None:
    """Gợi ý kỹ thuật viên đúng thứ tự khối lượng công việc tăng dần"""
    s = three_technicians_with_workloads(bt3)
    codes = [bt3.technician_code(t) for t in s["chosen"]]
    expected = [codes[1], codes[0], codes[2]]  # workloads 5, 2, 8 -> 2, 5, 8

    swagger_authorize(page, token_for(s["manager"]))
    status, body, block = swagger_execute(
        page, "GET", "/api/tickets/{ticket_id}/technician-suggestions", {"ticket_id": s["ticket_id"]})
    image = shot(page, "TC-01", block)

    rows = (body or {}).get("suggestions", [])
    bt3.facts.update(
        data=f"{s['manager']}, phiếu MỚI {s['ticket_code']} nhóm {s['category']}; "
             f"khối lượng {codes[0]}=5, {codes[1]}=2, {codes[2]}=8",
        actual=f"HTTP {status}; thứ tự " + " → ".join(f"{r['technician_code']} ({r['workload']})" for r in rows),
        images=[image],
    )
    assert status == 200
    assert [r["technician_code"] for r in rows] == expected
    assert [r["workload"] for r in rows] == [2, 5, 8]


@pytest.mark.tc("TC-02")
def test_tc02_phan_cong_thanh_cong(page: Page, bt3: System) -> None:
    """Phân công kỹ thuật viên đủ điều kiện cho phiếu MỚI và ghi lịch sử"""
    s = three_technicians_with_workloads(bt3)
    technician = s["chosen"][1]
    logs_before = bt3.log_count(s["ticket_id"])

    swagger_authorize(page, token_for(s["manager"]))
    status, body, block = swagger_execute(
        page, "POST", "/api/tickets/{ticket_id}/assignment", {"ticket_id": s["ticket_id"]},
        {"technician_id": technician})
    image = shot(page, "TC-02", block)

    row = bt3.ticket(s["ticket_id"])
    logs_after = bt3.log_count(s["ticket_id"])
    bt3.facts.update(
        data=f"{s['manager']}, phiếu {s['ticket_code']}, technician_id={technician} ({bt3.technician_code(technician)})",
        actual=f"HTTP {status}; ticket.status={row['status']}, technician_id={row['technician_id']}; "
               f"ticket_status_log của phiếu {logs_before} → {logs_after}",
        images=[image],
    )
    assert status == 201
    assert row["status"] == "DA_PHAN_CONG" and row["technician_id"] == technician
    assert logs_after == logs_before + 1


@pytest.mark.tc("TC-03")
def test_tc03_dat_lich_hop_le(page: Page, bt3: System) -> None:
    """Đặt lịch hẹn NHẬN hợp lệ 09:00–10:00 cho phiếu đã phân công"""
    ticket_id, technician, center_id, code = assigned_ticket(bt3)
    day = bt3.free_working_day([technician])
    before = bt3.one("SELECT count(*) FROM appointment")[0]
    request = {"ticket_id": ticket_id, "appointment_type": "NHAN",
               "start_at": iso(at(day, "09:00")), "end_at": iso(at(day, "10:00")), "note": "BT3 TC-03"}

    swagger_authorize(page, token_for(bt3.manager_username(center_id)))
    status, body, block = swagger_execute(page, "POST", "/api/appointments", body=request)
    image = shot(page, "TC-03", block)

    after = bt3.one("SELECT count(*) FROM appointment")[0]
    bt3.facts.update(
        data=f"Phiếu {code} (KTV {bt3.technician_code(technician)}), {day:%d/%m/%Y} 09:00–10:00 NHAN",
        actual=f"HTTP {status}; status={(body or {}).get('status')}, technician_id={(body or {}).get('technician_id')}; "
               f"bảng appointment {before} → {after}",
        images=[image],
    )
    assert status == 201
    assert body["status"] == "DA_HEN" and body["technician_id"] == technician
    assert after == before + 1


# --- 2. GIÁ TRỊ BIÊN ---------------------------------------------------------------


@pytest.mark.tc("TC-04")
def test_tc04_bien_tay_nghe_3_va_2(page: Page, bt3: System) -> None:
    """Biên tay nghề: = 3 được gợi ý, = 2 bị loại và bị từ chối phân công"""
    center_id = bt3.one(
        "SELECT center_id FROM technician WHERE is_active GROUP BY 1 HAVING count(*) >= 2 ORDER BY 1 LIMIT 1")[0]
    three, two = [r[0] for r in bt3.all(
        "SELECT technician_id FROM technician WHERE center_id = %s AND is_active ORDER BY technician_code LIMIT 2",
        center_id)]
    bt3.set_skill(three, "MAN_HINH", 3)
    bt3.set_skill(two, "MAN_HINH", 2)
    ticket_id = bt3.create_ticket(center_id, "MAN_HINH")
    code3, code2 = bt3.technician_code(three), bt3.technician_code(two)

    swagger_authorize(page, token_for(bt3.manager_username(center_id)))
    status_a, body_a, block = swagger_execute(
        page, "GET", "/api/tickets/{ticket_id}/technician-suggestions", {"ticket_id": ticket_id})
    image_a = shot(page, "TC-04", block)
    status_b, body_b, block = swagger_execute(
        page, "POST", "/api/tickets/{ticket_id}/assignment", {"ticket_id": ticket_id}, {"technician_id": two})
    image_b = shot(page, "TC-04_b", block)

    listed = {r["technician_code"]: r["proficiency"] for r in (body_a or {}).get("suggestions", [])}
    row = bt3.ticket(ticket_id)
    bt3.facts.update(
        data=f"Phiếu MỚI MAN_HINH trung tâm {center_id}; {code3} tay nghề 3, {code2} tay nghề 2",
        actual=f"(a) gợi ý HTTP {status_a}: {code3} {'có' if code3 in listed else 'KHÔNG có'}, "
               f"{code2} {'có' if code2 in listed else 'không có'}; (b) phân công {code2}: HTTP {status_b} "
               f"{(body_b or {}).get('error')}; phiếu còn {row['status']}, technician_id={row['technician_id']}",
        images=[image_a, image_b],
    )
    assert status_a == 200 and listed.get(code3) == 3 and code2 not in listed
    assert status_b == 400 and body_b["error"] == "TECHNICIAN_NOT_ELIGIBLE"
    assert row["status"] == "MOI" and row["technician_id"] is None


@pytest.mark.tc("TC-05")
def test_tc05_bien_lich_lien_ke_va_chong_1_phut(page: Page, bt3: System) -> None:
    """Biên lịch hẹn: liền kề (10:00 = 10:00) hợp lệ, chồng 1 phút bị 409"""
    ticket_id, technician, center_id, code = assigned_ticket(bt3)
    day = bt3.free_working_day([technician], "08:00", 180)
    token = token_for(bt3.manager_username(center_id))
    status, _ = api("POST", "/api/appointments", token, {
        "ticket_id": ticket_id, "appointment_type": "NHAN",
        "start_at": iso(at(day, "09:00")), "end_at": iso(at(day, "10:00"))})
    assert status == 201, "Không dựng được lịch A 09:00–10:00 làm tiền điều kiện"
    before = bt3.one("SELECT count(*) FROM appointment WHERE technician_id = %s AND status = 'DA_HEN'", technician)[0]

    swagger_authorize(page, token)
    status_a, body_a, block = swagger_execute(page, "POST", "/api/appointments", body={
        "ticket_id": ticket_id, "appointment_type": "GIAO",
        "start_at": iso(at(day, "10:00")), "end_at": iso(at(day, "11:00"))})
    image_a = shot(page, "TC-05", block)
    status_b, body_b, block = swagger_execute(page, "POST", "/api/appointments", body={
        "ticket_id": ticket_id, "appointment_type": "GIAO",
        "start_at": iso(at(day, "08:00")), "end_at": iso(at(day, "09:01"))})
    image_b = shot(page, "TC-05_b", block)

    after = bt3.one("SELECT count(*) FROM appointment WHERE technician_id = %s AND status = 'DA_HEN'", technician)[0]
    bt3.facts.update(
        data=f"Phiếu {code}, KTV {bt3.technician_code(technician)}, {day:%d/%m/%Y}; đã có lịch A 09:00–10:00; "
             f"(a) 10:00–11:00, (b) 08:00–09:01",
        actual=f"(a) HTTP {status_a}; (b) HTTP {status_b} {(body_b or {}).get('error')}, "
               f"gợi ý {len((body_b or {}).get('free_slots', []))} khung trống; lịch DA_HEN của KTV {before} → {after}",
        images=[image_a, image_b],
    )
    assert status_a == 201
    assert status_b == 409 and body_b["error"] == "APPOINTMENT_OVERLAP"
    assert after == before + 1


# --- 3. DỮ LIỆU SAI ----------------------------------------------------------------


@pytest.mark.tc("TC-06")
def test_tc06_doi_ktv_ly_do_chi_khoang_trang(page: Page, bt3: System) -> None:
    """Đổi kỹ thuật viên với lý do chỉ có khoảng trắng bị từ chối, dữ liệu không đổi"""
    ticket_id, old, new, center_id, code = bt3.one(
        """SELECT t.ticket_id, t.technician_id, k.technician_id, t.center_id, t.ticket_code
           FROM ticket t
           JOIN technician k ON k.center_id = t.center_id AND k.is_active AND k.technician_id <> t.technician_id
           JOIN technician_skill s ON s.technician_id = k.technician_id
                AND s.category_code = t.category_code AND s.proficiency >= 3
           WHERE t.status = 'DA_PHAN_CONG' ORDER BY t.ticket_id, k.technician_code LIMIT 1""")
    logs_before = bt3.log_count(ticket_id)

    swagger_authorize(page, token_for(bt3.manager_username(center_id)))
    status, body, block = swagger_execute(
        page, "PUT", "/api/tickets/{ticket_id}/assignment", {"ticket_id": ticket_id},
        {"technician_id": new, "reason": "   "})
    image = shot(page, "TC-06", block)

    row = bt3.ticket(ticket_id)
    logs_after = bt3.log_count(ticket_id)
    bt3.facts.update(
        data=f"Phiếu {code} của {bt3.technician_code(old)} → {bt3.technician_code(new)}, reason=\"   \" (3 dấu cách)",
        actual=f"HTTP {status} {(body or {}).get('error')} \"{(body or {}).get('message')}\"; "
               f"technician_id vẫn {row['technician_id']}; log {logs_before} → {logs_after}",
        images=[image],
    )
    assert status == 400 and body["error"] == "REASON_REQUIRED"
    assert row["technician_id"] == old and logs_after == logs_before


@pytest.mark.tc("TC-07")
def test_tc07_tao_phieu_du_lieu_sai(page: Page, bt3: System) -> None:
    """Tạo phiếu với SĐT sai và với trường bắt buộc chỉ có khoảng trắng bị từ chối 400"""
    manager = bt3.manager_username(1)
    before = bt3.one("SELECT count(*) FROM ticket")[0]

    swagger_authorize(page, token_for(manager))
    status_a, body_a, block = swagger_execute(
        page, "POST", "/api/tickets", body=ticket_body(customer_phone="09123"))
    image_a = shot(page, "TC-07", block)
    status_b, body_b, block = swagger_execute(
        page, "POST", "/api/tickets", body=ticket_body(customer_name="   ", serial_no="   ", issue_desc="   "))
    image_b = shot(page, "TC-07_b", block)

    after = bt3.one("SELECT count(*) FROM ticket")[0]
    blank = bt3.one("SELECT count(*) FROM ticket WHERE btrim(customer_name) = '' OR btrim(issue_desc) = ''")[0]
    bt3.facts.update(
        data=f"{manager}; (a) customer_phone=\"09123\"; (b) customer_name, serial_no, issue_desc = \"   \"",
        actual=f"(a) HTTP {status_a} {(body_a or {}).get('error')}; (b) HTTP {status_b} "
               f"{(body_b or {}).get('error') or (body_b or {}).get('ticket_code')}; bảng ticket {before} → {after}; "
               f"số phiếu có tên/mô tả rỗng: {blank}",
        images=[image_a, image_b],
    )
    assert status_a == 400 and body_a["error"] == "INVALID_PHONE"
    assert status_b == 400 and "customer_name" in json.dumps(body_b, ensure_ascii=False)
    assert after == before


@pytest.mark.tc("TC-08")
def test_tc08_id_khong_ton_tai(page: Page, bt3: System) -> None:
    """Mã phiếu không tồn tại và mã vượt giới hạn BIGINT trả 404, không phải 500"""
    max_id = bt3.one("SELECT max(ticket_id) FROM ticket")[0]
    missing, huge = 99_999_999, "99999999999999999999"
    assert missing > max_id

    swagger_authorize(page, token_for(bt3.manager_username(1)))
    status_a, body_a, block = swagger_execute(page, "GET", "/api/tickets/{ticket_id}", {"ticket_id": missing})
    image_a = shot(page, "TC-08", block)
    status_b, body_b, block = swagger_execute(page, "GET", "/api/tickets/{ticket_id}", {"ticket_id": huge})
    image_b = shot(page, "TC-08_b", block)

    bt3.facts.update(
        data=f"ticket_id={missing} (max thật {max_id}); ticket_id={huge} (> 2^63−1)",
        actual=f"(a) HTTP {status_a} {(body_a or {}).get('error')}; (b) HTTP {status_b} {(body_b or {}).get('error')}",
        images=[image_a, image_b],
    )
    assert status_a == 404 and body_a["error"] == "TICKET_NOT_FOUND"
    assert status_b == 404 and body_b["error"] == "TICKET_NOT_FOUND"


# --- 4. BẢO MẬT / CHẤT LƯỢNG DỮ LIỆU ----------------------------------------------


@pytest.mark.tc("TC-09")
def test_tc09_a01_sua_phieu_cua_nguoi_khac(page: Page, bt3: System) -> None:
    """A01: KTV đổi trạng thái phiếu của KTV khác và Quản lý sửa phiếu trung tâm khác đều bị 403"""
    ticket_id, owner, _, code = assigned_ticket(bt3)
    intruder = bt3.one(
        "SELECT technician_code FROM technician WHERE is_active AND technician_id <> %s ORDER BY technician_code LIMIT 1",
        owner)[0]
    other_ticket, other_code, other_name = bt3.one(
        "SELECT ticket_id, ticket_code, customer_name FROM ticket WHERE status = 'MOI' AND center_id <> 1 ORDER BY ticket_id LIMIT 1")
    logs_before = bt3.log_count(ticket_id)

    swagger_authorize(page, token_for(intruder))
    status_a, body_a, block = swagger_execute(
        page, "PATCH", "/api/tickets/{ticket_id}/status", {"ticket_id": ticket_id}, {"to_status": "DANG_XU_LY"})
    image_a = shot(page, "TC-09", block)
    manager = bt3.manager_username(1)
    swagger_authorize(page, token_for(manager))
    status_b, body_b, block = swagger_execute(
        page, "PUT", "/api/tickets/{ticket_id}", {"ticket_id": other_ticket}, ticket_body(customer_name="Đã bị sửa"))
    image_b = shot(page, "TC-09_b", block)

    row, other = bt3.ticket(ticket_id), bt3.ticket(other_ticket)
    bt3.facts.update(
        data=f"(a) token {intruder}, phiếu {code} của {bt3.technician_code(owner)}; "
             f"(b) token {manager}, phiếu {other_code} (trung tâm {other['center_id']})",
        actual=f"(a) HTTP {status_a} {(body_a or {}).get('error')}, phiếu vẫn {row['status']}, log {logs_before} → "
               f"{bt3.log_count(ticket_id)}; (b) HTTP {status_b} {(body_b or {}).get('error')}, "
               f"tên khách vẫn \"{other['customer_name']}\"",
        images=[image_a, image_b],
    )
    assert status_a == 403 and row["status"] == "DA_PHAN_CONG" and bt3.log_count(ticket_id) == logs_before
    assert status_b == 403 and other["customer_name"] == other_name


def signed_token(payload: dict) -> str:
    import hashlib
    import hmac
    header = _b64encode(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    body = _b64encode(json.dumps(payload, separators=(",", ":"), ensure_ascii=False).encode())
    signature = hmac.new(os.environ["SECRET_KEY"].encode(), f"{header}.{body}".encode(), hashlib.sha256).digest()
    return f"{header}.{body}.{_b64encode(signature)}"


@pytest.mark.tc("TC-10")
def test_tc10_a07_token_thieu_het_han_bi_sua(page: Page, bt3: System) -> None:
    """A07: không gửi token, token hết hạn, token bị sửa một ký tự đều trả 401"""
    valid = token_for("QL_TT01")
    header, payload, signature = valid.split(".")
    claims = json.loads(base64.urlsafe_b64decode(payload + "=" * (-len(payload) % 4)))
    expired = signed_token({**claims, "exp": int(time.time()) - 60})
    flipped = ("B" if signature[0] != "B" else "C") + signature[1:]
    tampered = f"{header}.{payload}.{flipped}"

    page.goto(f"{API_URL}/docs")
    status_a, body_a, block = swagger_execute(page, "GET", "/api/auth/me")
    image_a = shot(page, "TC-10", block)
    results = [(status_a, body_a)]
    images = [image_a]
    for part, token in (("b", expired), ("c", tampered)):
        swagger_authorize(page, token)
        status, body, block = swagger_execute(page, "GET", "/api/auth/me")
        images.append(shot(page, f"TC-10_{part}", block))
        results.append((status, body))
    control, _ = api("GET", "/api/auth/me", valid)

    bt3.facts.update(
        data="GET /api/auth/me: (a) không header Authorization; (b) token QL_TT01 ký đúng nhưng exp = now − 60 s; "
             "(c) token QL_TT01 hợp lệ đổi ký tự đầu của chữ ký",
        actual="; ".join(f"({p}) HTTP {s} {(b or {}).get('error')}" for p, (s, b) in zip("abc", results))
               + f"; đối chứng token gốc: HTTP {control}",
        images=images,
    )
    assert [s for s, _ in results] == [401, 401, 401]
    assert control == 200


@pytest.mark.tc("TC-11")
def test_tc11_a05_a02_injection_xss_cors(page: Page, bt3: System) -> None:
    """A05/A02: chuỗi SQL injection không trả hết dữ liệu, thẻ script hiện dạng chữ, CORS chỉ mở cho frontend"""
    if not _reachable(UI_URL):
        pytest.fail(f"Frontend chưa chạy tại {UI_URL}: chạy `npm run dev` trong src/frontend.")
    manager = bt3.manager_username(1)
    token = token_for(manager)
    injection = "' OR 1=1 --"

    swagger_authorize(page, token)
    status_a, body_a, block = swagger_execute(page, "GET", "/api/tickets", {"status": injection})
    image_a = shot(page, "TC-11", block)
    status_b, body_b, block = swagger_execute(page, "GET", "/api/tickets", {"status": "MOI", "category_code": injection})
    image_b = shot(page, "TC-11_b", block)

    script = "<script>alert('XSS')</script><img src=x onerror=alert(1)>"
    status_c, created = api("POST", "/api/tickets", token, ticket_body(issue_desc=script))
    assert status_c == 201, f"Không tạo được phiếu chứa thẻ script: {status_c} {created}"
    dialogs: list[str] = []
    page.on("dialog", lambda dialog: (dialogs.append(dialog.message), dialog.dismiss()))
    ui_login(page, manager)
    expect(page).to_have_url(f"{UI_URL}/tickets")
    page.goto(f"{UI_URL}/tickets/{created['ticket_id']}/assign")
    shown = page.get_by_text(script, exact=True)
    expect(shown).to_be_visible()
    page.wait_for_timeout(1000)
    image_c = shot(page, "TC-11_c")

    def preflight(origin: str) -> str | None:
        request = urllib.request.Request(f"{API_URL}/api/tickets", method="OPTIONS", headers={
            "Origin": origin, "Access-Control-Request-Method": "GET"})
        try:
            with urllib.request.urlopen(request) as response:
                return response.headers.get("access-control-allow-origin")
        except urllib.error.HTTPError as error:
            return error.headers.get("access-control-allow-origin")

    cors_evil, cors_ui = preflight("http://evil.example"), preflight(UI_URL)
    bt3.facts.update(
        data=f"{manager}; (a) status=\"{injection}\"; (b) status=MOI&category_code=\"{injection}\"; "
             f"(c) issue_desc=\"{script}\" mở ở M2; (d) preflight OPTIONS từ http://evil.example và {UI_URL}",
        actual=f"(a) HTTP {status_a} {(body_a or {}).get('error')}; (b) HTTP {status_b}, total={(body_b or {}).get('total')}; "
               f"(c) chuỗi hiện nguyên văn, hộp thoại alert bật: {len(dialogs)}; "
               f"(d) Allow-Origin cho evil.example = {cors_evil}, cho {UI_URL} = {cors_ui}; "
               f"phản hồi lỗi không chứa traceback/SQL: {no_leak(body_a)}",
        images=[image_a, image_b, image_c],
    )
    assert status_a == 400 and body_a["error"] == "INVALID_STATUS" and no_leak(body_a)
    assert status_b == 200 and body_b["total"] == 0 and body_b["items"] == []
    assert dialogs == []
    assert cors_evil is None and cors_ui == UI_URL


# --- 5. TÁI LẬP --------------------------------------------------------------------


@pytest.mark.tc("TC-12")
def test_tc12_dung_csdl_hai_lan_khong_nhan_doi(request: pytest.FixtureRequest,
                                               capsys: pytest.CaptureFixture[str]) -> None:
    """Chạy setup_all.py hai lần trên bộ mẫu: số dòng sáu bảng không đổi, không nhân đôi"""
    facts = start_record(request.node)
    load_db = "smartcrm_load_test"
    source = urlparse(get_test_database_url())
    maintenance = source._replace(path="/postgres", query="").geturl()
    target = source._replace(path=f"/{load_db}", query="").geturl()
    env = {**os.environ, "DATA_DIR": "data/sample", "DB_NAME": load_db, "PYTHONIOENCODING": "utf-8",
           "DB_HOST": source.hostname or "localhost", "DB_PORT": str(source.port or 5432),
           "DB_USER": unquote(source.username or "postgres"), "DB_PASSWORD": unquote(source.password or "")}
    env.pop("DATABASE_URL", None)

    def drop() -> None:
        with psycopg.connect(maintenance, autocommit=True) as connection:
            connection.execute(sql.SQL("DROP DATABASE IF EXISTS {}").format(sql.Identifier(load_db)))

    drop()
    counts = []
    try:
        for run in (1, 2):
            result = subprocess.run([sys.executable, "scripts/setup_all.py"], cwd=ROOT, env=env,
                                    capture_output=True, text=True, encoding="utf-8")
            assert result.returncode == 0, result.stdout[-1500:] + result.stderr[-1500:]
            counts.append(database_counts(target))
            with capsys.disabled():
                print(f"\n[TC-12] setup_all.py lần {run} → {load_db}: "
                      + ", ".join(f"{t}={n}" for t, n in counts[-1].items()))
        with psycopg.connect(target) as connection:
            new_tickets = connection.execute("SELECT count(*) FROM ticket WHERE status = 'MOI'").fetchone()[0]
    finally:
        drop()

    facts.update(
        data=f"DATA_DIR=data/sample, database {load_db} (xoá trước khi chạy), chạy `python scripts/setup_all.py` hai lần",
        actual="lần 1: " + ", ".join(f"{t}={n}" for t, n in counts[0].items())
               + "; lần 2: " + ", ".join(f"{t}={n}" for t, n in counts[1].items())
               + f"; phiếu MOI = {new_tickets}",
        images=[],
    )
    assert counts[0] == counts[1] == EXPECTED_COUNTS["bộ mẫu trong repo (data/sample)"]
    assert new_tickets == 30
