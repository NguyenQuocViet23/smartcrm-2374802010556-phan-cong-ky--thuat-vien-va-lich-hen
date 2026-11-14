import { useCallback, useEffect, useMemo, useState } from 'react';
import { Link } from 'react-router-dom';
import { cancelAppointment, listAllAppointments } from '../api/appointments.api.js';
import AppHeader from '../components/AppHeader.jsx';
import AppointmentForm from '../components/AppointmentForm.jsx';
import ConfirmDialog from '../components/ConfirmDialog.jsx';
import DataState from '../components/DataState.jsx';
import Modal from '../components/Modal.jsx';
import StatusBadge from '../components/StatusBadge.jsx';
import { appointmentRange, appointmentTypeLabel, vnParts, vnToday } from '../labels.js';

const PAGE_SIZE = 20;
const STATUS_FILTERS = [['DA_HEN', 'Đã hẹn'], ['DA_HUY', 'Đã hủy'], ['', 'Tất cả']];
const TIME_FILTERS = [['upcoming', 'Sắp tới'], ['today', 'Hôm nay'], ['past', 'Đã qua'], ['', 'Mọi thời điểm']];

function matchesTime(appointment, filter, today) {
  if (!filter) return true;
  const day = vnParts(appointment.start_at).date;
  if (filter === 'today') return day === today;
  if (filter === 'upcoming') return new Date(appointment.end_at) >= new Date();
  return new Date(appointment.end_at) < new Date();
}

// All appointments the user may see: a manager the center's, a technician their own (scoped by the API).
export default function AppointmentsPage({ user, onLogout }) {
  const isManager = user?.role === 'QUAN_LY';
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [status, setStatus] = useState('DA_HEN');
  const [time, setTime] = useState('upcoming');
  const [page, setPage] = useState(1);
  const [notice, setNotice] = useState('');
  const [editing, setEditing] = useState(null);
  const [cancelling, setCancelling] = useState(null);
  const [cancelBusy, setCancelBusy] = useState(false);
  const [cancelError, setCancelError] = useState(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      setItems(await listAllAppointments(status ? { status } : {}));
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  }, [status]);

  useEffect(() => { load(); }, [load]);

  const today = vnToday();
  const filtered = useMemo(() => {
    const rows = items.filter((appointment) => matchesTime(appointment, time, today));
    // Upcoming and today read best soonest first; the rest newest first (API order).
    return time === 'upcoming' || time === 'today'
      ? [...rows].sort((a, b) => new Date(a.start_at) - new Date(b.start_at))
      : rows;
  }, [items, time, today]);
  const pages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const shown = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);
  const todayCount = items.filter((a) => a.status === 'DA_HEN' && vnParts(a.start_at).date === today).length;

  async function confirmCancel() {
    setCancelBusy(true);
    setCancelError(null);
    try {
      await cancelAppointment(cancelling.appointment_id);
      setNotice(`Đã hủy lịch hẹn ${appointmentRange(cancelling)} của phiếu ${cancelling.ticket_code}.`);
      setCancelling(null);
      await load();
    } catch (requestError) {
      setCancelError(requestError);
    } finally {
      setCancelBusy(false);
    }
  }

  const ticketLink = (appointment) => (isManager
    ? `/tickets/${appointment.ticket_id}`
    : `/my-tickets?ticket=${appointment.ticket_id}`);

  return (
    <>
      <AppHeader title={isManager ? 'Lịch hẹn của trung tâm' : 'Lịch hẹn của tôi'} user={user} onLogout={onLogout} />
      <main className="page">
        <section className="filters panel">
          <label>Trạng thái lịch
            <select value={status} onChange={(event) => { setStatus(event.target.value); setPage(1); }}>
              {STATUS_FILTERS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
          <label>Thời gian
            <select value={time} onChange={(event) => { setTime(event.target.value); setPage(1); }}>
              {TIME_FILTERS.map(([value, label]) => <option key={value} value={value}>{label}</option>)}
            </select>
          </label>
          {!loading && !error && <span className="muted">Hiển thị {filtered.length} lịch · hôm nay có {todayCount} lịch đã hẹn</span>}
        </section>
        <p className="hint">Đặt lịch mới từ trang chi tiết của phiếu ({isManager ? 'menu Phiếu → mở phiếu' : 'Phiếu của tôi → chọn phiếu'}). Lịch đã hủy không xoá khỏi hệ thống.</p>
        {notice && <div className="notice success" role="status">{notice}</div>}
        <DataState loading={loading} error={error} isEmpty={!filtered.length} emptyMessage="Không có lịch hẹn phù hợp bộ lọc" onRetry={load}>
          <div className="panel table-wrap">
            <table>
              <thead><tr><th>Thời gian</th><th>Loại</th><th>Phiếu</th><th>Trạng thái</th><th>Ghi chú</th><th>Thao tác</th></tr></thead>
              <tbody>{shown.map((appointment) => (
                <tr key={appointment.appointment_id}>
                  <td>{appointmentRange(appointment)}</td>
                  <td>{appointmentTypeLabel[appointment.appointment_type] || appointment.appointment_type}</td>
                  <td><Link to={ticketLink(appointment)}>{appointment.ticket_code}</Link></td>
                  <td><StatusBadge kind="appointment" status={appointment.status} /></td>
                  <td>{appointment.note || ''}</td>
                  <td className="row-actions">{appointment.status === 'DA_HEN' && <>
                    <button className="button small secondary" type="button" onClick={() => { setNotice(''); setEditing(appointment); }}>Đổi giờ</button>
                    <button className="button small danger-outline" type="button" onClick={() => { setNotice(''); setCancelError(null); setCancelling(appointment); }}>Hủy lịch</button>
                  </>}</td>
                </tr>
              ))}</tbody>
            </table>
            <footer className="pagination">
              <span>Tổng số lịch: {filtered.length}</span>
              <button className="button secondary" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>Trước</button>
              <span>Trang {page} / {pages}</span>
              <button className="button secondary" disabled={page >= pages} onClick={() => setPage((value) => value + 1)}>Sau</button>
            </footer>
          </div>
        </DataState>
      </main>
      {editing && (
        <Modal title={`Đổi giờ lịch hẹn – phiếu ${editing.ticket_code}`} onClose={() => setEditing(null)} wide>
          <AppointmentForm appointment={editing} onCancel={() => setEditing(null)}
            onSaved={async (saved) => {
              setEditing(null);
              setNotice(`Đã đổi lịch hẹn của phiếu ${editing.ticket_code} sang ${saved?.start_at ? appointmentRange(saved) : 'giờ mới'}.`);
              await load();
            }} />
        </Modal>
      )}
      {cancelling && (
        <ConfirmDialog
          title={`Hủy lịch hẹn của phiếu ${cancelling.ticket_code}?`}
          message={`${appointmentRange(cancelling)} · ${appointmentTypeLabel[cancelling.appointment_type]}. Lịch chuyển sang ĐÃ HỦY, khung giờ được giải phóng.`}
          confirmLabel="Xác nhận hủy lịch" danger busy={cancelBusy} error={cancelError}
          onCancel={() => setCancelling(null)} onConfirm={confirmCancel}
        />
      )}
    </>
  );
}
