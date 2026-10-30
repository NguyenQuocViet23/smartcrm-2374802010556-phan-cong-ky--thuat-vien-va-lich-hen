import { useCallback, useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { assignTicket, changeAssignment, getSuggestions, getTicket } from '../api/tickets.api.js';
import AppHeader from '../components/AppHeader.jsx';
import AppointmentForm from '../components/AppointmentForm.jsx';
import DataState from '../components/DataState.jsx';

const statusLabel = {
  MOI: 'MỚI', DA_PHAN_CONG: 'ĐÃ PHÂN CÔNG', DANG_XU_LY: 'ĐANG XỬ LÝ',
  CHO_LINH_KIEN: 'CHỜ LINH KIỆN', HOAN_TAT: 'HOÀN TẤT',
  DA_DONG: 'ĐÃ ĐÓNG', DA_HUY: 'ĐÃ HỦY',
};

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

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [details, choices] = await Promise.all([getTicket(id), getSuggestions(id)]);
      setTicket(details);
      setSuggestions(choices.suggestions);
      setSelectedId(String(choices.suggestions[0]?.technician_id || ''));
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => { load(); }, [load]);

  async function saveAssignment() {
    setBusy(true);
    setActionError(null);
    try {
      if (ticket.technician_id == null) {
        await assignTicket(id, Number(selectedId));
      } else {
        await changeAssignment(id, Number(selectedId), reason);
      }
      setReason('');
      await load();
    } catch (requestError) {
      setActionError(requestError);
    } finally {
      setBusy(false);
    }
  }

  const selected = suggestions.find((item) => String(item.technician_id) === selectedId);
  const firstSuggested = suggestions[0];
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

  return (
    <>
      <AppHeader title={ticket?.technician_id ? 'Đổi kỹ thuật viên' : 'Phân công kỹ thuật viên'} user={user} onLogout={onLogout} />
      <main className="page">
        <DataState loading={loading} error={error} onRetry={load}>
          {ticket && <>
            <section className="panel ticket-details">
              <h2>{ticket.ticket_code}</h2>
              <div className="detail-grid">
                <span>Khách hàng</span><strong>{ticket.customer_name}</strong>
                <span>Số điện thoại</span><strong>{ticket.customer_phone}</strong>
                <span>Serial</span><strong>{ticket.serial_no}</strong>
                <span>Mô tả lỗi</span><strong>{ticket.issue_desc}</strong>
                <span>Nhóm sự cố</span><strong>{ticket.category_code}</strong>
                <span>Mức ưu tiên</span><strong>{ticket.priority}</strong>
                <span>Hạn cam kết</span><strong>{new Date(ticket.due_date).toLocaleString('vi-VN')}</strong>
                <span>Trạng thái</span><strong>{statusLabel[ticket.status]}</strong>
                {ticket.technician && <><span>Kỹ thuật viên hiện tại</span><strong>{ticket.technician.technician_code} · {ticket.technician.full_name}</strong></>}
              </div>
            </section>
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
              {ticket.status === 'HOAN_TAT' && <div className="notice error">EX-5.3: Không thể đổi kỹ thuật viên khi phiếu đã hoàn tất.</div>}
              {actionError && <div className="notice error" role="alert">
                <strong>{errorLabel}:</strong> {actionError.code === 'NETWORK_ERROR' ? 'Chưa lưu được (mất kết nối).' : actionError.message}
                {actionError.code === 'NETWORK_ERROR' && <button className="button secondary" disabled={busy} onClick={saveAssignment}>Thử lại</button>}
              </div>}
              {selected && firstSuggested && selected.technician_id !== firstSuggested.technician_id && selected.workload > firstSuggested.workload && (
                <div className="notice warning">EX-4a: Kỹ thuật viên đã chọn đang giữ nhiều hơn người đầu danh sách {selected.workload - firstSuggested.workload} phiếu.</div>
              )}
              <div className="form-actions">
                <button className="button" disabled={busy || !selectedId || ticket.status === 'HOAN_TAT' || (ticket.technician_id != null && !reason.trim())} onClick={saveAssignment}>
                  {ticket.technician_id == null ? 'Xác nhận phân công' : 'Lưu đổi kỹ thuật viên'}
                </button>
                {ticket.technician_id != null && <button className="button secondary" onClick={() => setShowAppointment((value) => !value)}>Đặt lịch hẹn</button>}
                <button className="button secondary" onClick={() => navigate('/tickets')}>Hủy</button>
              </div>
            </section>
            {showAppointment && <AppointmentForm ticketId={Number(id)} onSaved={async () => { setShowAppointment(false); }} onCancel={() => setShowAppointment(false)} />}
            <section className="panel table-wrap">
              <h3>Lịch sử trạng thái</h3>
              <table><thead><tr><th>Thời điểm</th><th>Sự kiện</th><th>Từ → Đến</th><th>Kỹ thuật viên cũ → mới</th><th>Ghi chú</th></tr></thead>
                <tbody>{ticket.status_history.map((event) => <tr key={event.log_id}>
                  <td>{new Date(event.changed_at).toLocaleString('vi-VN')}</td><td>{event.event_type}</td><td>{event.from_status ? `${statusLabel[event.from_status]} → ` : ''}{statusLabel[event.to_status]}</td>
                  <td>{event.from_technician_code || '—'} → {event.to_technician_code || '—'}</td><td>{event.note || ''}</td>
                </tr>)}</tbody>
              </table>
            </section>
          </>}
        </DataState>
      </main>
    </>
  );
}
