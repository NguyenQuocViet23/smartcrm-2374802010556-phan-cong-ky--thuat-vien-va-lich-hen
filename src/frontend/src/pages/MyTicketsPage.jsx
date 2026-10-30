import { useCallback, useEffect, useState } from 'react';
import { getMyTickets } from '../api/technicians.api.js';
import { getTicket, getTicketAppointments, updateStatus } from '../api/tickets.api.js';
import AppHeader from '../components/AppHeader.jsx';
import AppointmentForm from '../components/AppointmentForm.jsx';
import DataState from '../components/DataState.jsx';

const statusLabel = {
  DA_PHAN_CONG: 'ĐÃ PHÂN CÔNG', DANG_XU_LY: 'ĐANG XỬ LÝ',
  CHO_LINH_KIEN: 'CHỜ LINH KIỆN', HOAN_TAT: 'HOÀN TẤT',
};
const nextStatus = {
  DA_PHAN_CONG: [['DANG_XU_LY', 'Bắt đầu sửa']],
  DANG_XU_LY: [['CHO_LINH_KIEN', 'Thiếu linh kiện'], ['HOAN_TAT', 'Hoàn tất']],
  CHO_LINH_KIEN: [['HOAN_TAT', 'Hoàn tất']],
};

export default function MyTicketsPage({ user, onLogout }) {
  const [tickets, setTickets] = useState([]);
  const [selected, setSelected] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [note, setNote] = useState('');
  const [actionError, setActionError] = useState(null);
  const [showAppointment, setShowAppointment] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await getMyTickets();
      setTickets(result);
      if (selected && !result.some((ticket) => ticket.ticket_id === selected.ticket_id)) {
        setSelected(null);
        setAppointments([]);
      }
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  }, [selected]);

  useEffect(() => { load(); }, [load]);

  async function selectTicket(ticket) {
    setSelected(await getTicket(ticket.ticket_id));
    setAppointments(await getTicketAppointments(ticket.ticket_id));
    setActionError(null);
  }

  async function changeStatus(status) {
    try {
      await updateStatus(selected.ticket_id, status, note);
      setNote('');
      await load();
      await selectTicket({ ticket_id: selected.ticket_id });
    } catch (requestError) {
      setActionError(requestError);
    }
  }

  async function reloadAppointments() {
    setAppointments(await getTicketAppointments(selected.ticket_id));
    setShowAppointment(false);
  }

  return (
    <>
      <AppHeader title="Phiếu của tôi" user={user} onLogout={onLogout} />
      <main className="page">
        <DataState loading={loading} error={error} isEmpty={!tickets.length} emptyMessage="Chưa có phiếu được giao" onRetry={load}>
          <section className="panel table-wrap">
            <table><thead><tr><th>Mã phiếu</th><th>Nhóm sự cố</th><th>Ưu tiên</th><th>Hạn cam kết</th><th>Trạng thái</th><th>SĐT khách</th></tr></thead>
              <tbody>{tickets.map((ticket) => <tr key={ticket.ticket_id} className={selected?.ticket_id === ticket.ticket_id ? 'selected' : ''} onClick={() => selectTicket(ticket)}>
                <td><button className="link-button" onClick={(event) => { event.stopPropagation(); selectTicket(ticket); }}>{ticket.ticket_code}</button></td><td>{ticket.category_code}</td><td>{ticket.priority}</td>
                <td>{new Date(ticket.due_date).toLocaleString('vi-VN')}{ticket.is_overdue && <strong className="overdue"> QUÁ HẠN</strong>}</td>
                <td>{statusLabel[ticket.status] || ticket.status}</td><td>{ticket.customer_phone}</td>
              </tr>)}</tbody>
            </table>
          </section>
          {selected && <section className="panel ticket-details">
            <h2>{selected.ticket_code}</h2>
            <div className="detail-grid">
              <span>Khách hàng</span><strong>{selected.customer_name}</strong>
              <span>Serial</span><strong>{selected.serial_no}</strong>
              <span>Mô tả lỗi</span><strong>{selected.issue_desc}</strong>
            </div>
            <label>Ghi chú (tối đa 255 ký tự)
              <input maxLength="255" value={note} onChange={(event) => setNote(event.target.value)} />
            </label>
            <div className="form-actions">
              {(nextStatus[selected.status] || []).map(([status, label]) => <button className="button" key={status} onClick={() => changeStatus(status)}>{label}</button>)}
              {selected.status !== 'HOAN_TAT' && <button className="button secondary" onClick={() => setShowAppointment((value) => !value)}>Đặt lịch hẹn</button>}
            </div>
            {actionError && <div className="notice error" role="alert">
              <strong>{actionError.code === 'INVALID_STATUS_TRANSITION' ? 'EX-8.1: ' : ''}</strong>
              {actionError.message}
            </div>}
            {showAppointment && <AppointmentForm ticketId={selected.ticket_id} onSaved={reloadAppointments} onCancel={() => setShowAppointment(false)} />}
            <h3>Lịch hẹn của phiếu</h3>
            <div className="table-wrap"><table><thead><tr><th>Giờ</th><th>Loại</th><th>Trạng thái</th></tr></thead><tbody>
              {appointments.map((appointment) => <tr key={appointment.appointment_id}><td>{new Date(appointment.start_at).toLocaleString('vi-VN')}–{new Date(appointment.end_at).toLocaleTimeString('vi-VN')}</td><td>{appointment.appointment_type}</td><td>{appointment.status === 'DA_HEN' ? 'ĐÃ HẸN' : 'ĐÃ HỦY'}</td></tr>)}
            </tbody></table></div>
          </section>}
        </DataState>
      </main>
    </>
  );
}
