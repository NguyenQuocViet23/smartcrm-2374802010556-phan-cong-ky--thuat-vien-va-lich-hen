import { useCallback, useEffect, useRef, useState } from 'react';
import { useSearchParams } from 'react-router-dom';
import { cancelAppointment, listAllAppointments } from '../api/appointments.api.js';
import { getMyTickets } from '../api/technicians.api.js';
import { getTicket, getTicketAppointments, updateStatus } from '../api/tickets.api.js';
import AppHeader from '../components/AppHeader.jsx';
import AppointmentForm from '../components/AppointmentForm.jsx';
import ConfirmDialog from '../components/ConfirmDialog.jsx';
import DataState from '../components/DataState.jsx';
import StatusBadge from '../components/StatusBadge.jsx';
import {
  CLOSED, IN_PROGRESS, appointmentRange, appointmentTypeLabel, categoryLabel, priorityLabel, statusLabel, vnParts, vnToday,
} from '../labels.js';

// Technicians keep access to all their own tickets, including closed and cancelled ones.
const statusFilters = [
  ['', 'Tất cả'],
  ['DANG_LAM', 'Đang làm'],
  ['HOAN_TAT', 'Hoàn tất'],
  ['DA_DONG', 'Đã đóng'],
  ['DA_HUY', 'Đã hủy'],
];
const matchesFilter = (ticket, filter) =>
  !filter || (filter === 'DANG_LAM' ? IN_PROGRESS.includes(ticket.status) : ticket.status === filter);
const nextStatus = {
  DA_PHAN_CONG: [['DANG_XU_LY', 'Bắt đầu sửa']],
  DANG_XU_LY: [['CHO_LINH_KIEN', 'Thiếu linh kiện'], ['HOAN_TAT', 'Hoàn tất']],
  CHO_LINH_KIEN: [['HOAN_TAT', 'Hoàn tất']],
};
const eventLabel = { TRANG_THAI: 'Đổi trạng thái', DOI_KTV: 'Đổi kỹ thuật viên' };

export default function MyTicketsPage({ user, onLogout }) {
  const [searchParams, setSearchParams] = useSearchParams();
  const [tickets, setTickets] = useState([]);
  const [selected, setSelected] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [note, setNote] = useState('');
  const [actionError, setActionError] = useState(null);
  const [showAppointment, setShowAppointment] = useState(false);
  const [editingAppointment, setEditingAppointment] = useState(null);
  const [statusFilter, setStatusFilter] = useState('');
  const [notice, setNotice] = useState('');
  const [todayAppointments, setTodayAppointments] = useState(null);
  const [confirm, setConfirm] = useState(null); // {kind: 'finish'} or {kind: 'appointment', target}
  const [confirmBusy, setConfirmBusy] = useState(false);
  const [confirmError, setConfirmError] = useState(null);
  const openedFromLink = useRef(false);
  const visibleTickets = tickets.filter((ticket) => matchesFilter(ticket, statusFilter));
  const inProgress = tickets.filter((ticket) => IN_PROGRESS.includes(ticket.status));

  // A silent refresh keeps the list and the selected ticket on screen (no loading state).
  const load = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const result = await getMyTickets();
      setTickets(result);
      setSelected((current) => (
        current && !result.some((ticket) => ticket.ticket_id === current.ticket_id) ? null : current
      ));
    } catch (requestError) {
      setError(requestError);
    } finally {
      if (!silent) setLoading(false);
    }
  }, []);

  // "Appointments today" is extra information: if it cannot be loaded the box shows a dash.
  const loadToday = useCallback(async () => {
    try {
      const items = await listAllAppointments({ status: 'DA_HEN' });
      const today = vnToday();
      setTodayAppointments(items.filter((item) => vnParts(item.start_at).date === today).length);
    } catch {
      setTodayAppointments(null);
    }
  }, []);

  useEffect(() => { load(); loadToday(); }, [load, loadToday]);
  useEffect(() => { if (!selected) setAppointments([]); }, [selected]);

  async function selectTicket(ticket, { keepNotice = false } = {}) {
    if (!keepNotice) setNotice('');
    setEditingAppointment(null);
    try {
      setSelected(await getTicket(ticket.ticket_id));
      setAppointments(await getTicketAppointments(ticket.ticket_id));
      setActionError(null);
    } catch (requestError) {
      setActionError(requestError);
    }
  }

  // Link from the appointments page: /my-tickets?ticket=<id> opens that ticket once the list is in.
  useEffect(() => {
    const wanted = Number(searchParams.get('ticket'));
    if (!wanted || openedFromLink.current || loading) return;
    openedFromLink.current = true;
    if (tickets.some((ticket) => ticket.ticket_id === wanted)) selectTicket({ ticket_id: wanted });
    setSearchParams({}, { replace: true });
  }, [searchParams, tickets, loading, setSearchParams]); // eslint-disable-line react-hooks/exhaustive-deps

  async function applyStatus(status) {
    setNotice('');
    try {
      await updateStatus(selected.ticket_id, status, note);
      setNote('');
      setNotice(`Đã chuyển trạng thái sang ${statusLabel[status]}.`);
      await load({ silent: true });
      await selectTicket({ ticket_id: selected.ticket_id }, { keepNotice: true });
    } catch (requestError) {
      setActionError(requestError);
    }
  }

  function changeStatus(status) {
    if (status === 'HOAN_TAT') {
      setConfirmError(null);
      setConfirm({ kind: 'finish' });
      return;
    }
    applyStatus(status);
  }

  async function reloadAppointments() {
    setAppointments(await getTicketAppointments(selected.ticket_id));
    setShowAppointment(false);
    setEditingAppointment(null);
    loadToday();
  }

  async function runConfirm() {
    if (confirm.kind === 'finish') {
      setConfirm(null);
      await applyStatus('HOAN_TAT');
      return;
    }
    setConfirmBusy(true);
    setConfirmError(null);
    try {
      await cancelAppointment(confirm.target.appointment_id);
      setNotice(`Đã hủy lịch hẹn ${appointmentRange(confirm.target)}.`);
      setConfirm(null);
      await reloadAppointments();
    } catch (requestError) {
      setConfirmError(requestError);
    } finally {
      setConfirmBusy(false);
    }
  }

  const closed = selected ? CLOSED.includes(selected.status) : false;

  return (
    <>
      <AppHeader title="Phiếu của tôi" user={user} onLogout={onLogout} />
      <main className="page">
        <section className="stats" aria-label="Tổng hợp">
          <div className="stat"><span>Đang làm</span><strong>{loading ? '…' : inProgress.length}</strong></div>
          <div className="stat warn"><span>Quá hạn</span><strong>{loading ? '…' : inProgress.filter((ticket) => ticket.is_overdue).length}</strong></div>
          <div className="stat ok"><span>Đã xong</span><strong>{loading ? '…' : tickets.filter((ticket) => ticket.status === 'HOAN_TAT').length}</strong></div>
          <div className="stat"><span>Lịch hẹn hôm nay</span><strong>{todayAppointments ?? '–'}</strong></div>
        </section>
        <section className="filters panel">
          <label>Trạng thái
            <select value={statusFilter} onChange={(event) => setStatusFilter(event.target.value)}>
              {statusFilters.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
          {!loading && !error && <span className="muted">Hiển thị {visibleTickets.length} / {tickets.length} phiếu · bấm vào một phiếu để xem chi tiết</span>}
        </section>
        <DataState
          loading={loading}
          error={error}
          isEmpty={!visibleTickets.length}
          emptyMessage={tickets.length ? 'Không có phiếu ở trạng thái đã chọn' : 'Chưa có phiếu được giao'}
          onRetry={() => load()}
        >
          <div className={`split ${selected ? 'with-detail' : ''}`}>
            <section className="panel table-wrap list-pane">
              <table><thead><tr><th>Mã phiếu</th><th>Nhóm sự cố</th><th>Ưu tiên</th><th>Hạn cam kết</th><th>Trạng thái</th><th>SĐT khách</th></tr></thead>
                <tbody>{visibleTickets.map((ticket) => <tr key={ticket.ticket_id} className={selected?.ticket_id === ticket.ticket_id ? 'selected' : ''} onClick={() => selectTicket(ticket)}>
                  <td><button className="link-button" onClick={(event) => { event.stopPropagation(); selectTicket(ticket); }}>{ticket.ticket_code}</button></td>
                  <td>{categoryLabel[ticket.category_code] || ticket.category_code}</td><td>{priorityLabel[ticket.priority] || ticket.priority}</td>
                  <td>{new Date(ticket.due_date).toLocaleString('vi-VN')}{ticket.is_overdue && <strong className="overdue"> QUÁ HẠN</strong>}</td>
                  <td><StatusBadge status={ticket.status} /></td><td>{ticket.customer_phone}</td>
                </tr>)}</tbody>
              </table>
            </section>
            {selected && <section className="panel ticket-details detail-pane">
              <div className="section-head">
                <h2>{selected.ticket_code}</h2>
                <button className="button small secondary" type="button" onClick={() => setSelected(null)}>Đóng chi tiết</button>
              </div>
              <div className="detail-grid">
                <span>Khách hàng</span><strong>{selected.customer_name}</strong>
                <span>Số điện thoại</span><strong>{selected.customer_phone}</strong>
                <span>Serial</span><strong>{selected.serial_no}</strong>
                <span>Mô tả lỗi</span><strong>{selected.issue_desc}</strong>
                <span>Nhóm sự cố</span><strong>{categoryLabel[selected.category_code] || selected.category_code}</strong>
                <span>Ưu tiên</span><strong>{priorityLabel[selected.priority] || selected.priority}</strong>
                <span>Hạn cam kết</span><strong>{new Date(selected.due_date).toLocaleString('vi-VN')}</strong>
                <span>Trạng thái</span><strong><StatusBadge status={selected.status} /></strong>
              </div>
              {notice && <div className="notice success" role="status">{notice}</div>}
              {!closed && <>
                <label>Ghi chú (tối đa 255 ký tự)
                  <input maxLength="255" value={note} onChange={(event) => setNote(event.target.value)} />
                </label>
                <div className="form-actions">
                  {(nextStatus[selected.status] || []).map(([status, label]) => <button className="button" key={status} onClick={() => changeStatus(status)}>{label}</button>)}
                  <button className="button secondary" onClick={() => { setEditingAppointment(null); setShowAppointment((value) => !value); }}>Đặt lịch hẹn</button>
                </div>
              </>}
              {actionError && <div className="notice error" role="alert">
                <strong>{actionError.code === 'INVALID_STATUS_TRANSITION' ? 'EX-8.1: ' : ''}</strong>
                {actionError.message}
              </div>}
              {showAppointment && <AppointmentForm ticketId={selected.ticket_id} onSaved={reloadAppointments} onCancel={() => setShowAppointment(false)} />}
              {editingAppointment && <AppointmentForm key={editingAppointment.appointment_id} appointment={editingAppointment} onSaved={reloadAppointments} onCancel={() => setEditingAppointment(null)} />}
              <h3>Lịch hẹn của phiếu</h3>
              {appointments.length === 0 ? <p className="muted">Chưa có lịch hẹn.</p> : (
                <div className="table-wrap"><table><thead><tr><th>Giờ</th><th>Loại</th><th>Trạng thái</th><th>Thao tác</th></tr></thead><tbody>
                  {appointments.map((appointment) => <tr key={appointment.appointment_id}>
                    <td>{appointmentRange(appointment)}</td>
                    <td>{appointmentTypeLabel[appointment.appointment_type] || appointment.appointment_type}</td>
                    <td><StatusBadge kind="appointment" status={appointment.status} /></td>
                    <td className="row-actions">{appointment.status === 'DA_HEN' && !closed && <>
                      <button className="button small secondary" type="button" onClick={() => { setShowAppointment(false); setEditingAppointment(appointment); }}>Đổi giờ</button>
                      <button className="button small danger-outline" type="button" onClick={() => { setConfirmError(null); setConfirm({ kind: 'appointment', target: appointment }); }}>Hủy lịch</button>
                    </>}</td>
                  </tr>)}
                </tbody></table></div>
              )}
              {selected.status_history?.length > 0 && <>
                <h3>Lịch sử phiếu</h3>
                <ol className="history">
                  {selected.status_history.map((event) => (
                    <li key={event.log_id}>
                      <span className="muted">{new Date(event.changed_at).toLocaleString('vi-VN')}</span>{' '}
                      {eventLabel[event.event_type] || event.event_type}: {event.from_status ? `${statusLabel[event.from_status]} → ` : ''}{statusLabel[event.to_status]}
                      {event.note ? ` · ${event.note}` : ''}
                    </li>
                  ))}
                </ol>
              </>}
            </section>}
          </div>
        </DataState>
      </main>
      {confirm && (
        <ConfirmDialog
          title={confirm.kind === 'finish' ? `Hoàn tất phiếu ${selected?.ticket_code}?` : 'Hủy lịch hẹn này?'}
          message={confirm.kind === 'finish'
            ? 'Phiếu chuyển sang HOÀN TẤT và không đổi được trạng thái nữa. Hãy chắc rằng máy đã sửa xong.'
            : `${appointmentRange(confirm.target)} · ${appointmentTypeLabel[confirm.target.appointment_type]}. Lịch chuyển sang ĐÃ HỦY, khung giờ được giải phóng.`}
          confirmLabel={confirm.kind === 'finish' ? 'Xác nhận' : 'Xác nhận hủy lịch'}
          danger={confirm.kind !== 'finish'} busy={confirmBusy} error={confirmError}
          onCancel={() => setConfirm(null)} onConfirm={runConfirm}
        />
      )}
    </>
  );
}
