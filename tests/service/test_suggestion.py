"""TC01–TC03: technician suggestions (UC2) on the real system."""

from __future__ import annotations

import pytest
from playwright.sync_api import Page, expect

from tests.real_system import (
    ACTIVE_STATUSES, System, api, capture, open_assign_page, suggestion_rows, token_for,
)

pytestmark = pytest.mark.system


def three_technicians_with_workloads(system: System, workloads=(5, 2, 8)) -> dict:
    """TC01 scenario built from real rows on the working copy.

    A (center, category) with at least 3 eligible technicians is taken from the real data;
    their real active tickets are closed, then 5/2/8 tickets are created for them, and the
    remaining eligible technicians of that pair are switched off.
    """
    center_id, category = system.one(
        """SELECT t.center_id, s.category_code
           FROM technician t JOIN technician_skill s USING (technician_id)
           WHERE t.is_active AND s.proficiency >= 3
           GROUP BY 1, 2
           HAVING count(*) >= 3 AND (SELECT count(*) FROM technician x WHERE x.center_id = t.center_id) >= 6
           ORDER BY count(*) DESC, 1, 2 LIMIT 1"""
    )
    eligible = [row[0] for row in system.all(
        """SELECT t.technician_id FROM technician t JOIN technician_skill s USING (technician_id)
           WHERE t.center_id = %s AND s.category_code = %s AND t.is_active AND s.proficiency >= 3
           ORDER BY t.technician_code""",
        center_id, category,
    )]
    chosen, others = eligible[:3], eligible[3:]
    system.run(
        "UPDATE ticket SET status = 'DA_DONG', closed_at = now() WHERE technician_id = ANY(%s) AND status = ANY(%s)",
        chosen, list(ACTIVE_STATUSES),
    )
    for technician_id, count in zip(chosen, workloads):
        for _ in range(count):
            system.create_ticket(center_id, category, status="DA_PHAN_CONG",
                                 technician_id=technician_id, priority="TRUNG_BINH")
    system.run("UPDATE technician SET is_active = false WHERE technician_id = ANY(%s)", others)
    ticket_id = system.create_ticket(center_id, category)
    return {
        "center_id": center_id, "category": category, "chosen": chosen, "others": others,
        "ticket_id": ticket_id, "ticket_code": system.ticket(ticket_id)["ticket_code"],
        "manager": system.manager_username(center_id),
    }


@pytest.mark.tc("TC01")
def test_tc01_goi_y_dung_thu_tu(page: Page, system: System) -> None:
    """Gợi ý kỹ thuật viên đúng thứ tự khối lượng công việc"""
    s = three_technicians_with_workloads(system)
    codes = {t: system.technician_code(t) for t in s["chosen"]}
    expected = [codes[s["chosen"][1]], codes[s["chosen"][0]], codes[s["chosen"][2]]]

    status, body = api("GET", f"/api/tickets/{s['ticket_id']}/technician-suggestions", token_for(s["manager"]))

    assert status == 200
    rows = body["suggestions"]
    assert [r["technician_code"] for r in rows] == expected
    assert [r["workload"] for r in rows] == [2, 5, 8]
    for r in rows:
        assert r["technician_code"] and r["full_name"] and r["proficiency"] >= 3 and "workload" in r
    sql_workload = dict(system.all(
        """SELECT technician_id, count(*) FROM ticket WHERE status = ANY(%s) AND technician_id = ANY(%s)
           GROUP BY technician_id""", list(ACTIVE_STATUSES), s["chosen"],
    ))
    assert [sql_workload[t] for t in s["chosen"]] == [5, 2, 8]

    open_assign_page(page, s["manager"], s["ticket_id"])
    ui_rows = suggestion_rows(page)
    assert [(code, workload) for code, _, workload in ui_rows] == list(zip(expected, [2, 5, 8]))
    capture(page, "TC01_goi_y_dung_thu_tu")
    system.facts["data"] = (f"Trung tâm {s['manager'][3:]}, nhóm {s['category']}, phiếu MỚI {s['ticket_code']} "
                            f"(tạo trên bản sao); KTV {', '.join(codes.values())}; "
                            f"{len(s['others'])} KTV đủ điều kiện khác được tắt")
    system.facts["actual"] = ("HTTP 200; gợi ý theo thứ tự " + " → ".join(f"{c} (khối lượng {w})" for c, _, w in ui_rows)
                              + "; SQL đếm khối lượng khớp")


@pytest.mark.tc("TC02")
def test_tc02_goi_y_loai_ktv_khong_du_dieu_kien(page: Page, system: System) -> None:
    """Gợi ý loại bỏ kỹ thuật viên không đủ điều kiện"""
    s = three_technicians_with_workloads(system)
    center_id, category = s["center_id"], s["category"]
    spare = [row[0] for row in system.all(
        "SELECT technician_id FROM technician WHERE center_id = %s AND NOT (technician_id = ANY(%s)) ORDER BY technician_code",
        center_id, s["chosen"],
    )]
    low_skill, inactive = spare[0], spare[1]
    system.run("UPDATE technician SET is_active = true WHERE technician_id = %s", low_skill)
    system.set_skill(low_skill, category, 2)
    system.set_skill(inactive, category, 4)
    system.run("UPDATE technician SET is_active = false WHERE technician_id = %s", inactive)
    other_center = system.one(
        "SELECT technician_id FROM technician WHERE center_id <> %s AND is_active ORDER BY technician_code LIMIT 1",
        center_id,
    )[0]
    system.set_skill(other_center, category, 5)
    excluded = {system.technician_code(t): reason for t, reason in (
        (low_skill, "tay nghề 2"), (other_center, "trung tâm khác, tay nghề 5"), (inactive, "đã nghỉ, tay nghề 4"))}

    status, body = api("GET", f"/api/tickets/{s['ticket_id']}/technician-suggestions", token_for(s["manager"]))

    assert status == 200
    codes = [r["technician_code"] for r in body["suggestions"]]
    assert not set(codes) & set(excluded)
    for code in codes:
        row = system.one(
            """SELECT t.center_id, t.is_active, s.proficiency FROM technician t
               JOIN technician_skill s ON s.technician_id = t.technician_id AND s.category_code = %s
               WHERE t.technician_code = %s""", category, code,
        )
        assert row[0] == center_id and row[1] is True and row[2] >= 3

    open_assign_page(page, s["manager"], s["ticket_id"])
    ui_codes = [code for code, _, _ in suggestion_rows(page)]
    assert ui_codes == codes
    capture(page, "TC02_goi_y_loai_ktv_khong_du_dieu_kien")
    system.facts["data"] = (f"Trung tâm {s['manager'][3:]}, nhóm {category}, phiếu {s['ticket_code']}; KTV bị loại: "
                            + "; ".join(f"{c} ({r})" for c, r in excluded.items()))
    system.facts["actual"] = f"HTTP 200; danh sách gợi ý {', '.join(codes)}; không có {', '.join(excluded)}"


@pytest.mark.tc("TC03")
def test_tc03_goi_y_rong_khong_co_ktv(page: Page, system: System) -> None:
    """Gợi ý trả danh sách rỗng kèm lý do khi không có kỹ thuật viên phù hợp"""
    ticket_id, ticket_code, center_id, category = system.one(
        """SELECT t.ticket_id, t.ticket_code, t.center_id, t.category_code FROM ticket t
           WHERE t.status = 'MOI' AND EXISTS (
             SELECT 1 FROM technician k JOIN technician_skill s USING (technician_id)
             WHERE k.center_id = t.center_id AND k.is_active AND s.category_code = t.category_code
               AND s.proficiency >= 3)
           ORDER BY t.ticket_id LIMIT 1"""
    )
    lowered = system.one(
        """SELECT count(*) FROM technician_skill WHERE category_code = %s AND proficiency >= 3
             AND technician_id IN (SELECT technician_id FROM technician WHERE center_id = %s)""",
        category, center_id,
    )[0]
    system.run(
        """UPDATE technician_skill SET proficiency = 2 WHERE category_code = %s AND proficiency >= 3
             AND technician_id IN (SELECT technician_id FROM technician WHERE center_id = %s)""",
        category, center_id,
    )
    manager = system.manager_username(center_id)

    status, body = api("GET", f"/api/tickets/{ticket_id}/technician-suggestions", token_for(manager))

    assert status == 200
    assert body["suggestions"] == []
    assert "tay nghề từ 3" in body["message"]
    after = system.ticket(ticket_id)
    assert after["status"] == "MOI" and after["technician_id"] is None

    open_assign_page(page, manager, ticket_id)
    expect(page.get_by_text("EX-3a: Không có kỹ thuật viên phù hợp")).to_be_visible()
    capture(page, "TC03_goi_y_rong_khong_co_ktv")
    system.facts["data"] = (f"Phiếu MỚI thật {ticket_code} (trung tâm {manager[3:]}, nhóm {category}); "
                            f"hạ tay nghề {category} của {lowered} KTV trung tâm này xuống 2 trên bản sao")
    system.facts["actual"] = f"HTTP 200; suggestions = []; message: \"{body['message']}\"; phiếu vẫn MOI, chưa có KTV"
