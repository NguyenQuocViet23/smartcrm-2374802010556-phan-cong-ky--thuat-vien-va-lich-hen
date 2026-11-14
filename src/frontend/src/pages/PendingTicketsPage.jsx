import { useCallback, useEffect, useRef, useState } from 'react';
import { Link, useNavigate, useSearchParams } from 'react-router-dom';
import { cancelTicket, countTickets, listTickets } from '../api/tickets.api.js';
import AppHeader from '../components/AppHeader.jsx';
import ConfirmDialog from '../components/ConfirmDialog.jsx';
import DataState from '../components/DataState.jsx';
import Modal from '../components/Modal.jsx';
import StatusBadge from '../components/StatusBadge.jsx';
import TicketForm from '../components/TicketForm.jsx';
import { CATEGORIES, CLOSED, PRIORITIES, categoryLabel, isOverdue, priorityLabel } from '../labels.js';

export const STATUS_TABS = [
  ['MOI', 'Chờ phân công'], ['DA_PHAN_CONG', 'Đã phân công'], ['DANG_XU_LY', 'Đang xử lý'],
  ['CHO_LINH_KIEN', 'Chờ linh kiện'], ['HOAN_TAT', 'Hoàn tất'], ['DA_DONG', 'Đã đóng'], ['DA_HUY', 'Đã hủy'],
];
const PAGE_SIZE = 20;

export default function PendingTicketsPage({ user, onLogout }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const status = STATUS_TABS.some(([code]) => code === searchParams.get('status')) ? searchParams.get('status') : 'MOI';
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [category, setCategory] = useState('');
  const [priority, setPriority] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [counts, setCounts] = useState({});
  const [notice, setNotice] = useState('');
  const [editing, setEditing] = useState(null); // 'new' or a ticket
  const [cancelling, setCancelling] = useState(null);
  const [cancelReason, setCancelReason] = useState('');
  const [cancelBusy, setCancelBusy] = useState(false);
  const [cancelError, setCancelError] = useState(null);
  const countsLoaded = useRef(false);
  const navigate = useNavigate();

  // Tab counts are extra information: a failure only leaves the number out.
  const loadCounts = useCallback(async () => {
    const results = await Promise.allSettled(STATUS_TABS.map(([code]) => countTickets(code)));
    countsLoaded.current = results.every((result) => result.status === 'fulfilled');
    setCounts(Object.fromEntries(results.map((result, index) => [
      STATUS_TABS[index][0], result.status === 'fulfilled' ? result.value : undefined,
    ])));
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    // The list request is sent first; the counts follow in the same tick.
    const listing = listTickets({
      status,
      category_code: category,
      priority,
      page: String(page),
      page_size: String(PAGE_SIZE),
    });
    if (!countsLoaded.current) loadCounts();
    try {
      const result = await listing;
      setItems(result.items);
      setTotal(result.total);
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  }, [status, category, priority, page, loadCounts]);

  useEffect(() => { load(); }, [load]);

  function chooseTab(code) {
    setPage(1);
    setNotice('');
    setSearchParams(code === 'MOI' ? {} : { status: code });
  }

  async function afterChange(message) {
    setNotice(message);
    countsLoaded.current = false;
    await load();
  }

  async function confirmCancel() {
    setCancelBusy(true);
    setCancelError(null);
    try {
      await cancelTicket(cancelling.ticket_id, cancelReason);
      const code = cancelling.ticket_code;
      setCancelling(null);
      setCancelReason('');
      await afterChange(`Đã hủy phiếu ${code}. Phiếu chuyển sang tab "Đã hủy".`);
    } catch (requestError) {
      setCancelError(requestError);
    } finally {
      setCancelBusy(false);
    }
  }

  const tabLabel = STATUS_TABS.find(([code]) => code === status)[1];
  const pages = Math.max(1, Math.ceil(total / PAGE_SIZE));

  return (
    <>
      <AppHeader title={status === 'MOI' ? 'Phiếu chờ phân công' : `Phiếu – ${tabLabel}`} user={user} onLogout={onLogout} />
      <main className="page">
        <section className="toolbar">
          <div className="tabs" role="tablist" aria-label="Lọc phiếu theo tình trạng">
            {STATUS_TABS.map(([code, label]) => (
              <button key={code} type="button" role="tab" aria-selected={code === status}
                className={`tab ${code === status ? 'active' : ''}`} onClick={() => chooseTab(code)}>
                {label}{counts[code] !== undefined && <span className="count">{counts[code]}</span>}
              </button>
            ))}
          </div>
          <button className="button" type="button" onClick={() => { setNotice(''); setEditing('new'); }}>+ Tạo phiếu mới</button>
        </section>
        <section className="filters panel">
          <label>Nhóm sự cố
            <select value={category} onChange={(event) => { setCategory(event.target.value); setPage(1); }}>
              <option value="">Tất cả</option>
              {CATEGORIES.map((item) => <option key={item} value={item}>{categoryLabel[item]}</option>)}
            </select>
          </label>
          <label>Mức ưu tiên
            <select value={priority} onChange={(event) => { setPriority(event.target.value); setPage(1); }}>
              <option value="">Tất cả</option>
              {PRIORITIES.map((item) => <option key={item} value={item}>{priorityLabel[item]}</option>)}
            </select>
          </label>
        </section>
        {notice && <div className="notice success" role="status">{notice}</div>}
        <DataState loading={loading} error={error} isEmpty={!items.length}
          emptyMessage={status === 'MOI' ? 'Không có phiếu chờ phân công' : `Không có phiếu ở trạng thái "${tabLabel}"`}
          onRetry={load}>
          <div className="panel table-wrap">
            <table>
              <thead><tr><th>Mã phiếu</th><th>Khách hàng</th><th>Số điện thoại</th><th>Nhóm sự cố</th><th>Mức ưu tiên</th><th>Hạn cam kết</th><th>Trạng thái</th><th>Thao tác</th></tr></thead>
              <tbody>{items.map((ticket) => (
                <tr key={ticket.ticket_id}>
                  <td><Link to={`/tickets/${ticket.ticket_id}`}>{ticket.ticket_code}</Link></td>
                  <td>{ticket.customer_name}</td>
                  <td>{ticket.customer_phone}</td>
                  <td>{categoryLabel[ticket.category_code] || ticket.category_code}</td>
                  <td>{priorityLabel[ticket.priority]}</td>
                  <td>{new Date(ticket.due_date).toLocaleString('vi-VN')}{isOverdue(ticket) && <strong className="overdue"> QUÁ HẠN</strong>}</td>
                  <td><StatusBadge status={ticket.status} /></td>
                  <td className="row-actions">
                    {ticket.status === 'MOI' ? <>
                      <button className="button small" onClick={() => navigate(`/tickets/${ticket.ticket_id}/assign`)}>Phân công</button>
                      <button className="button small secondary" onClick={() => { setNotice(''); setEditing(ticket); }}>Sửa</button>
                      <button className="button small danger-outline" onClick={() => { setNotice(''); setCancelError(null); setCancelling(ticket); }}>Hủy phiếu</button>
                    </> : (
                      <button className="button small secondary" onClick={() => navigate(`/tickets/${ticket.ticket_id}`)}>
                        {CLOSED.includes(ticket.status) ? 'Xem' : 'Chi tiết / Đổi KTV'}
                      </button>
                    )}
                  </td>
                </tr>
              ))}</tbody>
            </table>
            <footer className="pagination">
              <span>Tổng số phiếu: {total}</span>
              <button className="button secondary" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>Trước</button>
              <span>Trang {page} / {pages}</span>
              <button className="button secondary" disabled={page >= Math.ceil(total / PAGE_SIZE)} onClick={() => setPage((value) => value + 1)}>Sau</button>
            </footer>
          </div>
        </DataState>
      </main>
      {editing && (
        <Modal title={editing === 'new' ? 'Tạo phiếu bảo hành mới' : `Sửa phiếu ${editing.ticket_code}`} onClose={() => setEditing(null)} wide>
          <TicketForm
            ticket={editing === 'new' ? null : editing}
            onClose={() => setEditing(null)}
            onSaved={async (saved) => {
              const created = editing === 'new';
              setEditing(null);
              if (created && status !== 'MOI') chooseTab('MOI');
              await afterChange(created ? `Đã tạo phiếu ${saved.ticket_code} (trạng thái MỚI).` : `Đã lưu thay đổi phiếu ${saved.ticket_code}.`);
            }}
          />
        </Modal>
      )}
      {cancelling && (
        <ConfirmDialog
          title={`Hủy phiếu ${cancelling.ticket_code}?`}
          message="Phiếu chuyển sang trạng thái ĐÃ HỦY (không xoá khỏi hệ thống) và không thể phân công nữa."
          confirmLabel="Xác nhận hủy phiếu"
          danger busy={cancelBusy} error={cancelError}
          onCancel={() => { setCancelling(null); setCancelReason(''); }}
          onConfirm={confirmCancel}
        >
          <label>Lý do hủy (không bắt buộc)
            <input maxLength="255" value={cancelReason} onChange={(event) => setCancelReason(event.target.value)} />
          </label>
        </ConfirmDialog>
      )}
    </>
  );
}
