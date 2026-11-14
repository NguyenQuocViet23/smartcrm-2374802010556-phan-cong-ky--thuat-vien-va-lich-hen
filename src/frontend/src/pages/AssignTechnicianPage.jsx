import { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { cancelAppointment } from '../api/appointments.api.js';
import { assignTicket, cancelTicket, changeAssignment, getSuggestions, getTicket, getTicketAppointments } from '../api/tickets.api.js';
import AppHeader from '../components/AppHeader.jsx';
import AppointmentForm from '../components/AppointmentForm.jsx';
import ConfirmDialog from '../components/ConfirmDialog.jsx';
import DataState from '../components/DataState.jsx';
import Modal from '../components/Modal.jsx';
import StatusBadge from '../components/StatusBadge.jsx';
import TicketForm from '../components/TicketForm.jsx';
import {
  CLOSED, appointmentRange, appointmentTypeLabel, categoryLabel, isOverdue, priorityLabel, statusLabel,
} from '../labels.js';

function appointmentSavedMessage(appointment, moved = false) {
  if (!appointment?.start_at) return moved ? 'Đã đổi giờ lịch hẹn.' : 'Đã đặt lịch hẹn.';
  const start = new Date(appointment.start_at);
  const end = new Date(appointment.end_at);
  return `${moved ? 'Đã đổi lịch' : 'Đã đặt lịch'} ${appointment.appointment_type === 'NHAN' ? 'NHẬN' : 'GIAO'} lúc `
    + `${start.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })}–`
    + `${end.toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' })} `
    + `ngày ${start.toLocaleDateString('vi-VN')}.`;
}

const eventLabel = { TRANG_THAI: 'ĐỔI TRẠNG THÁI', DOI_KTV: 'ĐỔI KỸ THUẬT VIÊN' };

// Ticket detail for a manager: assign or change the technician, book and manage appointments,
// correct or cancel a new ticket, and read the history. Routes: /tickets/:id and /tickets/:id/assign.
export default function AssignTechnicianPage({ user, onLogout }) {
  const { id } = useParams();
  const navigate = useNavigate();
  const [ticket, setTicket] = useState(null);
  const [suggestions, setSuggestions] = useState([]);
  const [selectedId, setSelectedId] = useState('');
  const [reason, setReason] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [actionError, setActionError] = useState(null);
  const [busy, setBusy] = useState(false);
  const [showAppointment, setShowAppointment] = useState(false);
  const [editingAppointment, setEditingAppointment] = useState(null);
  const [notice, setNotice] = useState('');
  const [appointments, setAppointments] = useState([]);
  const [appointmentsError, setAppointmentsError] = useState(false);
  const [editingTicket, setEditingTicket] = useState(false);
  const [confirm, setConfirm] = useState(null); // {kind: 'ticket'|'appointment', target}
  const [confirmBusy, setConfirmBusy] = useState(false);
  const [confirmError, setConfirmError] = useState(null);
  const [cancelReason, setCancelReason] = useState('');

  // Appointments are secondary information: a failure here must not hide the ticket.
  const loadAppointments = useCallback(async () => {
    try {
      setAppointments(await getTicketAppointments(id));
      setAppointmentsError(false);
    } catch {
      setAppointmentsError(true);
    }
  }, [id]);

  // A silent refresh keeps the page on screen (no loading state) after a save.
  const load = useCallback(async ({ silent = false } = {}) => {
    if (!silent) setLoading(true);
    setError(null);
    try {
      const [details, choices] = await Promise.all([getTicket(id), getSuggestions(id)]);
      setTicket(details);
      setSuggestions(choices.suggestions);
      setSelectedId(String(choices.suggestions[0]?.technician_id || ''));
    } catch (requestError) {
      setError(requestError);
    } finally {
      if (!silent) setLoading(false);
    }
    loadAppointments();
  }, [id, loadAppointments]);

  useEffect(() => { load(); }, [load]);

  async function saveAssignment() {
    setBusy(true);
    setActionError(null);
    setNotice('');
    const chosen = suggestions.find((item) => String(item.technician_id) === selectedId);
    const chosenLabel = chosen ? `${chosen.technician_code} · ${chosen.full_name}` : `#${selectedId}`;
    try {
      if (ticket.technician_id == null) {
        await assignTicket(id, Number(selectedId));
        setNotice(`Đã phân công phiếu cho kỹ thuật viên ${chosenLabel}.`);
      } else {
        await changeAssignment(id, Number(selectedId), reason);
        setNotice(`Đã đổi kỹ thuật viên sang ${chosenLabel}.`);
      }
      setReason('');
      await load({ silent: true });
    } catch (requestError) {
      setActionError(requestError);
    } finally {
      setBusy(false);
    }
  }

  async function runConfirm() {
    setConfirmBusy(true);
    setConfirmError(null);
    try {
      if (confirm.kind === 'ticket') {
        await cancelTicket(ticket.ticket_id, cancelReason);
        setNotice(`Đã hủy phiếu ${ticket.ticket_code}.`);
        setCancelReason('');
        setConfirm(null);
        await load({ silent: true });
      } else {
        await cancelAppointment(confirm.target.appointment_id);
        setNotice(`Đã hủy lịch hẹn ${appointmentRange(confirm.target)}.`);
        setConfirm(null);
        await loadAppointments();
      }
    } catch (requestError) {
      setConfirmError(requestError);
    } finally {
      setConfirmBusy(false);
    }
  }

  const selected = suggestions.find((item) => String(item.technician_id) === selectedId);
  const firstSuggested = suggestions[0];
  const closed = ticket ? CLOSED.includes(ticket.status) : false;
  const errorLabel = actionError?.code === 'TICKET_ALREADY_ASSIGNED'
    ? 'EX-2a'
    : actionError?.code === 'TECHNICIAN_NOT_ELIGIBLE'
      ? 'EX-6a'
      : actionError?.code === 'NETWORK_ERROR'
        ? 'EX-7b'
        : actionError?.code === 'TICKET_NOT_CHANGEABLE'
          ? 'EX-5.3'
          : actionError?.code === 'REASON_REQUIRED'
            ? 'EX-5.1'
            : 'Lỗi';
  const title = !ticket ? 'Chi tiết phiếu' : closed ? 'Chi tiết phiếu' : ticket.technician_id ? 'Đổi kỹ thuật viên' : 'Phân công kỹ thuật viên';

  return (
    <>
      <AppHeader title={title} user={user} onLogout={onLogout} />
      <main className="page">
        <DataState loading={loading} error={error} onRetry={() => load()}>
          {ticket && <>
            <section className="panel ticket-details">
              <div className="section-head">
                <h2>{ticket.ticket_code}</h2>
                <div className="row-actions">
                  {ticket.status === 'MOI' && <>
                    <button className="button small secondary" type="button" onClick={() => { setNotice(''); setEditingTicket(true); }}>Sửa phiếu</button>
                    <button className="button small danger-outline" type="button" onClick={() => { setNotice(''); setConfirmError(null); setConfirm({ kind: 'ticket' }); }}>Hủy phiếu</button>
                  </>}
                  <button className="button small secondary" type="button" onClick={() => navigate(ticket.status === 'MOI' ? '/tickets' : `/tickets?status=${ticket.status}`)}>← Quay lại danh sách</button>
                </div>
              </div>
              <div className="detail-grid">
                <span>Khách hàng</span><strong>{ticket.customer_name}</strong>
                <span>Số điện thoại</span><strong>{ticket.customer_phone}</strong>
                <span>Serial</span><strong>{ticket.serial_no}</strong>
                <span>Mô tả lỗi</span><strong>{ticket.issue_desc}</strong>
                <span>Nhóm sự cố</span><strong>{categoryLabel[ticket.category_code] || ticket.category_code}</strong>
                <span>Mức ưu tiên</span><strong>{priorityLabel[ticket.priority] || ticket.priority}</strong>
                <span>Hạn cam kết</span><strong>{new Date(ticket.due_date).toLocaleString('vi-VN')}{isOverdue(ticket) && <span className="overdue"> QUÁ HẠN</span>}</strong>
                <span>Trạng thái</span><strong><StatusBadge status={ticket.status} /></strong>
                {ticket.technician && <><span>Kỹ thuật viên hiện tại</span><strong>{ticket.technician.technician_code} · {ticket.technician.full_name}</strong></>}
              </div>
            </section>
            {closed ? (
              <section className="panel">
                <p className="notice">Phiếu đã {statusLabel[ticket.status]?.toLowerCase()}: không phân công, đổi kỹ thuật viên hay đặt lịch hẹn mới được nữa.</p>
                <div className="form-actions">
                  <button className="button secondary" onClick={() => navigate(`/tickets?status=${ticket.status}`)}>Hủy</button>
                </div>
              </section>
            ) : (
              <section className="panel table-wrap">
                <h3>Gợi ý kỹ thuật viên</h3>
                {suggestions.length === 0 ? <p className="notice warning">EX-3a: Không có kỹ thuật viên phù hợp (không có người cùng trung tâm đủ tay nghề ≥ 3). Phiếu vẫn ở trạng thái MỚI.</p> : (
                  <table>
                    <thead><tr><th>Chọn</th><th>Mã</th><th>Họ tên</th><th>Bậc</th><th>Tay nghề nhóm sự cố</th><th>Khối lượng</th></tr></thead>
                    <tbody>{suggestions.map((item) => (
                      <tr key={item.technician_id}>
                        <td><input type="radio" name="technician" value={item.technician_id} checked={selectedId === String(item.technician_id)} onChange={() => setSelectedId(String(item.technician_id))} /></td>
                        <td>{item.technician_code}</td><td>{item.full_name}</td><td>{item.level}</td><td>{item.proficiency}</td><td>{item.workload}</td>
                      </tr>
                    ))}</tbody>
                  </table>
                )}
                {ticket.technician_id != null && <label className="reason-field">Lý do đổi
                  <input maxLength="255" value={reason} onChange={(event) => setReason(event.target.value)} required />
                </label>}
                {actionError && <div className="notice error" role="alert">
                  <strong>{errorLabel}:</strong> {actionError.code === 'NETWORK_ERROR' ? 'Chưa lưu được (mất kết nối).' : actionError.message}
                  {actionError.code === 'NETWORK_ERROR' && <button className="button secondary" disabled={busy} onClick={saveAssignment}>Thử lại</button>}
                </div>}
                {selected && firstSuggested && selected.technician_id !== firstSuggested.technician_id && selected.workload > firstSuggested.workload && (
                  <div className="notice warning">EX-4a: Kỹ thuật viên đã chọn đang giữ nhiều hơn người đầu danh sách {selected.workload - firstSuggested.workload} phiếu.</div>
                )}
                <div className="form-actions">
                  <button className="button" disabled={busy || !selectedId || (ticket.technician_id != null && !reason.trim())} onClick={saveAssignment}>
                    {ticket.technician_id == null ? 'Xác nhận phân công' : 'Lưu đổi kỹ thuật viên'}
                  </button>
                  {ticket.technician_id != null && <button className="button secondary" onClick={() => { setNotice(''); setEditingAppointment(null); setShowAppointment((value) => !value); }}>Đặt lịch hẹn</button>}
                  <button className="button secondary" onClick={() => navigate('/tickets')}>Hủy</button>
                </div>
              </section>
            )}
            {notice && <div className="notice success" role="status">{notice}</div>}
            {showAppointment && <AppointmentForm ticketId={Number(id)} onSaved={async (appointment) => { setShowAppointment(false); setNotice(appointmentSavedMessage(appointment)); await loadAppointments(); }} onCancel={() => setShowAppointment(false)} />}
            {editingAppointment && <AppointmentForm key={editingAppointment.appointment_id} appointment={editingAppointment} onSaved={async (appointment) => { setEditingAppointment(null); setNotice(appointmentSavedMessage(appointment, true)); await loadAppointments(); }} onCancel={() => setEditingAppointment(null)} />}
            <section className="panel table-wrap">
              <h3>Lịch hẹn của phiếu</h3>
              {appointmentsError ? <p className="notice error">Không tải được lịch hẹn.</p> : appointments.length === 0 ? <p className="muted">Chưa có lịch hẹn.</p> : (
                <table><thead><tr><th>Giờ</th><th>Loại</th><th>Trạng thái</th><th>Ghi chú</th><th>Thao tác</th></tr></thead>
                  <tbody>{appointments.map((appointment) => <tr key={appointment.appointment_id}>
                    <td>{appointmentRange(appointment)}</td>
                    <td>{appointmentTypeLabel[appointment.appointment_type] || appointment.appointment_type}</td>
                    <td><StatusBadge kind="appointment" status={appointment.status} /></td>
                    <td>{appointment.note || ''}</td>
                    <td className="row-actions">{appointment.status === 'DA_HEN' && !closed && <>
                      <button className="button small secondary" type="button" onClick={() => { setNotice(''); setShowAppointment(false); setEditingAppointment(appointment); }}>Đổi giờ</button>
                      <button className="button small danger-outline" type="button" onClick={() => { setNotice(''); setConfirmError(null); setConfirm({ kind: 'appointment', target: appointment }); }}>Hủy lịch</button>
                    </>}</td>
                  </tr>)}</tbody>
                </table>
              )}
            </section>
            <section className="panel table-wrap">
              <h3>Lịch sử trạng thái</h3>
              <table><thead><tr><th>Thời điểm</th><th>Sự kiện</th><th>Từ → Đến</th><th>Kỹ thuật viên cũ → mới</th><th>Ghi chú</th></tr></thead>
                <tbody>{ticket.status_history.map((event) => <tr key={event.log_id}>
                  <td>{new Date(event.changed_at).toLocaleString('vi-VN')}</td><td>{eventLabel[event.event_type] || event.event_type}</td><td>{event.from_status ? `${statusLabel[event.from_status]} → ` : ''}{statusLabel[event.to_status]}</td>
                  <td>{event.from_technician_code || '—'} → {event.to_technician_code || '—'}</td><td>{event.note || ''}</td>
                </tr>)}</tbody>
              </table>
            </section>
          </>}
        </DataState>
      </main>
      {editingTicket && ticket && (
        <Modal title={`Sửa phiếu ${ticket.ticket_code}`} onClose={() => setEditingTicket(false)} wide>
          <TicketForm ticket={ticket} onClose={() => setEditingTicket(false)}
            onSaved={async () => { setEditingTicket(false); setNotice(`Đã lưu thay đổi phiếu ${ticket.ticket_code}.`); await load({ silent: true }); }} />
        </Modal>
      )}
      {confirm && (
        <ConfirmDialog
          title={confirm.kind === 'ticket' ? `Hủy phiếu ${ticket.ticket_code}?` : 'Hủy lịch hẹn này?'}
          message={confirm.kind === 'ticket'
            ? 'Phiếu chuyển sang trạng thái ĐÃ HỦY (không xoá khỏi hệ thống) và không thể phân công nữa.'
            : `${appointmentRange(confirm.target)} · ${appointmentTypeLabel[confirm.target.appointment_type]}. Lịch chuyển sang ĐÃ HỦY, khung giờ được giải phóng.`}
          confirmLabel={confirm.kind === 'ticket' ? 'Xác nhận hủy phiếu' : 'Xác nhận hủy lịch'}
          danger busy={confirmBusy} error={confirmError}
          onCancel={() => { setConfirm(null); setCancelReason(''); }}
          onConfirm={runConfirm}
        >
          {confirm.kind === 'ticket' && <label>Lý do hủy (không bắt buộc)
            <input maxLength="255" value={cancelReason} onChange={(event) => setCancelReason(event.target.value)} />
          </label>}
        </ConfirmDialog>
      )}
    </>
  );
}
