import { useState } from 'react';
import { createAppointment } from '../api/appointments.api.js';

function suggestedDate() {
  const date = new Date();
  date.setDate(date.getDate() + 30);
  while (date.getDay() === 0) date.setDate(date.getDate() + 1);
  return date.toISOString().slice(0, 10);
}

export default function AppointmentForm({ ticketId, onSaved, onCancel }) {
  const [appointmentType, setAppointmentType] = useState('GIAO');
  const [date, setDate] = useState(suggestedDate);
  const [start, setStart] = useState('09:00');
  const [note, setNote] = useState('');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  const [created, setCreated] = useState(false);

  const end = (() => {
    const [hours, minutes] = start.split(':').map(Number);
    const total = hours * 60 + minutes + 30;
    return `${String(Math.floor(total / 60)).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`;
  })();
  const errorCode = error?.code === 'APPOINTMENT_OVERLAP'
    ? 'EX-6.4'
    : error?.code === 'TICKET_NOT_ASSIGNED'
      ? 'EX-6.5'
      : error?.code === 'NETWORK_ERROR'
        ? 'EX-6.6'
        : 'EX-6.3';

  async function saveAppointment() {
    setBusy(true);
    setError(null);
    try {
      if (!created) {
        const startAt = new Date(`${date}T${start}:00+07:00`).toISOString();
        const endAt = new Date(`${date}T${end}:00+07:00`).toISOString();
        await createAppointment({
          ticket_id: ticketId,
          appointment_type: appointmentType,
          start_at: startAt,
          end_at: endAt,
          note: note.trim() || null,
        });
        setCreated(true);
      }
      await onSaved();
    } catch (requestError) {
      setError(requestError);
    } finally {
      setBusy(false);
    }
  }

  function submit(event) {
    event.preventDefault();
    saveAppointment();
  }

  return (
    <form className="panel form-grid" onSubmit={submit}>
      <h3>Đặt lịch hẹn giao/nhận thiết bị</h3>
      <label>Loại
        <select value={appointmentType} onChange={(event) => setAppointmentType(event.target.value)}>
          <option value="GIAO">GIAO</option>
          <option value="NHAN">NHẬN</option>
        </select>
      </label>
      <label>Ngày
        <input type="date" value={date} onChange={(event) => setDate(event.target.value)} required />
      </label>
      <label>Giờ bắt đầu
        <input type="time" min="08:00" max="17:30" step="1800" value={start} onChange={(event) => setStart(event.target.value)} required />
      </label>
      <label>Giờ kết thúc
        <input type="time" value={end} readOnly />
      </label>
      <label className="wide">Ghi chú
        <input maxLength="255" value={note} onChange={(event) => setNote(event.target.value)} />
      </label>
      {error && (
        <div className="notice error wide" role="alert">
          <strong>{errorCode}:</strong> {error.message}
          {error.code === 'NETWORK_ERROR' && <button type="button" className="button secondary" disabled={busy} onClick={saveAppointment}>Thử lại</button>}
          {created && error.code !== 'NETWORK_ERROR' && <button type="button" className="button secondary" disabled={busy} onClick={saveAppointment}>Tải lại lịch hẹn</button>}
          {error.body?.conflicts?.map((item) => (
            <div key={item.appointment_id}>{item.start_at}–{item.end_at} · {item.ticket_code}</div>
          ))}
          {error.body?.free_slots?.length > 0 && (
            <div className="free-slots">
              Khung trống gần nhất:{' '}
              {error.body.free_slots.slice(0, 4).map((slot) => (
                <button type="button" className="link-button" key={slot.start_at} onClick={() => setStart(slot.start_at.slice(11, 16))}>
                  {slot.start_at.slice(11, 16)}–{slot.end_at.slice(11, 16)}
                </button>
              ))}
            </div>
          )}
        </div>
      )}
      <div className="form-actions wide">
        <button className="button" type="submit" disabled={busy}>Lưu lịch hẹn</button>
        {onCancel && <button className="button secondary" type="button" onClick={onCancel}>Hủy</button>}
      </div>
    </form>
  );
}
