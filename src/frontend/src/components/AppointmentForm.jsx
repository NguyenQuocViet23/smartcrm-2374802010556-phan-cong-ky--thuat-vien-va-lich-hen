import { useState } from 'react';
import { createAppointment, updateAppointment } from '../api/appointments.api.js';
import { formatDateTime, formatTime, toVnIso, vnParts } from '../labels.js';

const DURATIONS = [30, 60, 90, 120];
const DAY_END = 18 * 60; // working hours end at 18:00 (UTC+7)

// Next working day (Monday–Saturday) in Vietnam time.
function nextWorkingDay() {
  const date = new Date(`${vnParts(new Date()).date}T00:00:00Z`);
  date.setUTCDate(date.getUTCDate() + 1);
  while (date.getUTCDay() === 0) date.setUTCDate(date.getUTCDate() + 1);
  return date.toISOString().slice(0, 10);
}

const toMinutes = (hhmm) => { const [h, m] = hhmm.split(':').map(Number); return h * 60 + m; };
const toHhmm = (total) => `${String(Math.floor(total / 60)).padStart(2, '0')}:${String(total % 60).padStart(2, '0')}`;

// Book a slot for a ticket, or (with `appointment`) move an existing one.
export default function AppointmentForm({ ticketId, appointment, onSaved, onCancel }) {
  const editing = Boolean(appointment);
  const initialStart = editing ? vnParts(appointment.start_at) : null;
  const initialDuration = editing
    ? Math.round((new Date(appointment.end_at) - new Date(appointment.start_at)) / 60000)
    : 30;
  const [appointmentType, setAppointmentType] = useState(appointment?.appointment_type || 'GIAO');
  const [date, setDate] = useState(initialStart ? initialStart.date : nextWorkingDay);
  const [start, setStart] = useState(initialStart ? initialStart.time : '09:00');
  const [duration, setDuration] = useState(DURATIONS.includes(initialDuration) ? initialDuration : 30);
  const [note, setNote] = useState(appointment?.note || '');
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);
  // The appointment returned by the API once it is saved; a retry then only reloads.
  const [saved, setSaved] = useState(null);

  const end = toHhmm(toMinutes(start || '00:00') + Number(duration));
  const latestStart = toHhmm(DAY_END - Number(duration));
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
      let result = saved;
      if (!result) {
        const body = {
          appointment_type: appointmentType,
          start_at: toVnIso(date, start),
          end_at: toVnIso(date, end),
          note: note.trim() || null,
        };
        result = editing
          ? await updateAppointment(appointment.appointment_id, body)
          : await createAppointment({ ticket_id: ticketId, ...body });
        setSaved(result);
      }
      await onSaved(result);
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
      <h3>{editing ? 'Đổi giờ lịch hẹn' : 'Đặt lịch hẹn giao/nhận thiết bị'}</h3>
      <label>Loại
        <select value={appointmentType} onChange={(event) => setAppointmentType(event.target.value)}>
          <option value="GIAO">Giao máy cho khách (GIAO)</option>
          <option value="NHAN">Nhận máy từ khách (NHAN)</option>
        </select>
      </label>
      <label>Ngày
        <input type="date" value={date} onChange={(event) => setDate(event.target.value)} required />
      </label>
      <label>Giờ bắt đầu
        <input type="time" min="08:00" max={latestStart} step="1800" value={start} onChange={(event) => setStart(event.target.value)} required />
      </label>
      <label>Thời lượng
        <select value={duration} onChange={(event) => setDuration(Number(event.target.value))}>
          {DURATIONS.map((minutes) => <option key={minutes} value={minutes}>{minutes} phút</option>)}
        </select>
      </label>
      <label>Giờ kết thúc
        <input type="time" value={end} readOnly />
      </label>
      <p className="hint">Thứ Hai–Thứ Bảy, 08:00–18:00. Lịch liền kề (10:00 sau 09:00–10:00) được phép.</p>
      <label className="wide">Ghi chú
        <input maxLength="255" value={note} onChange={(event) => setNote(event.target.value)} />
      </label>
      {error && (
        <div className="notice error wide" role="alert">
          <strong>{errorCode}:</strong> {error.message}
          {error.code === 'NETWORK_ERROR' && <button type="button" className="button secondary" disabled={busy} onClick={saveAppointment}>Thử lại</button>}
          {saved && error.code !== 'NETWORK_ERROR' && <button type="button" className="button secondary" disabled={busy} onClick={saveAppointment}>Tải lại lịch hẹn</button>}
          {error.body?.conflicts?.map((item) => (
            <div key={item.appointment_id}>Trùng: {formatDateTime(item.start_at)}–{formatTime(item.end_at)} · {item.ticket_code}</div>
          ))}
          {error.body?.free_slots?.length > 0 && (
            <div className="free-slots">
              Khung trống gần nhất:{' '}
              {error.body.free_slots.slice(0, 4).map((slot) => (
                <button type="button" className="link-button" key={slot.start_at} onClick={() => { setDate(slot.start_at.slice(0, 10)); setStart(slot.start_at.slice(11, 16)); }}>
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
