import { useState } from 'react';
import { createTicket, updateTicket } from '../api/tickets.api.js';
import { CATEGORIES, PRIORITIES, categoryLabel, priorityLabel, toVnIso, vnParts } from '../labels.js';

// Error code from the API -> the field it concerns.
const FIELD_OF_CODE = {
  INVALID_PHONE: 'customer_phone', INVALID_CATEGORY: 'category_code', INVALID_PRIORITY: 'priority',
  INVALID_DUE_DATE: 'due_date', INVALID_DATETIME: 'due_date',
};

function defaultDue() {
  const due = new Date(Date.now() + 3 * 24 * 60 * 60 * 1000);
  return { date: vnParts(due).date, time: '17:00' };
}

// Create a ticket (no `ticket`) or correct one that is still MOI (`ticket` given).
export default function TicketForm({ ticket, onSaved, onClose }) {
  const editing = Boolean(ticket);
  const due = editing ? vnParts(ticket.due_date) : defaultDue();
  const [form, setForm] = useState({
    customer_name: ticket?.customer_name || '',
    customer_phone: ticket?.customer_phone || '',
    serial_no: ticket?.serial_no || '',
    issue_desc: ticket?.issue_desc || '',
    category_code: ticket?.category_code || 'MAN_HINH',
    priority: ticket?.priority || 'TRUNG_BINH',
    due_date: due.date,
    due_time: due.time,
  });
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const set = (name) => (event) => setForm((value) => ({ ...value, [name]: event.target.value }));
  const badFields = new Set([
    ...(error?.body?.fields || []).map((field) => (typeof field === 'string' ? field : String(field.field).replace(/^body\./, ''))),
    FIELD_OF_CODE[error?.code],
  ].filter(Boolean));
  const invalid = (name) => (badFields.has(name) ? 'invalid' : undefined);

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError(null);
    const body = {
      customer_name: form.customer_name,
      customer_phone: form.customer_phone,
      serial_no: form.serial_no,
      issue_desc: form.issue_desc,
      category_code: form.category_code,
      priority: form.priority,
      due_date: toVnIso(form.due_date, form.due_time),
    };
    try {
      const saved = editing ? await updateTicket(ticket.ticket_id, body) : await createTicket(body);
      await onSaved(saved);
    } catch (requestError) {
      setError(requestError);
    } finally {
      setBusy(false);
    }
  }

  return (
    <form className="form-grid" onSubmit={submit} noValidate={false}>
      <label>Khách hàng
        <input className={invalid('customer_name')} maxLength="120" value={form.customer_name} onChange={set('customer_name')} required />
      </label>
      <label>Số điện thoại
        <input className={invalid('customer_phone')} maxLength="20" inputMode="tel" placeholder="0912 345 678"
          value={form.customer_phone} onChange={set('customer_phone')} required />
      </label>
      <label>Serial máy
        <input className={invalid('serial_no')} maxLength="50" value={form.serial_no} onChange={set('serial_no')} required />
      </label>
      <label>Nhóm sự cố
        <select className={invalid('category_code')} value={form.category_code} onChange={set('category_code')}>
          {CATEGORIES.map((code) => <option key={code} value={code}>{categoryLabel[code]}</option>)}
        </select>
      </label>
      <label className="wide">Mô tả lỗi
        <textarea className={invalid('issue_desc')} maxLength="2000" rows="3" value={form.issue_desc} onChange={set('issue_desc')} required />
      </label>
      <label>Mức ưu tiên
        <select className={invalid('priority')} value={form.priority} onChange={set('priority')}>
          {PRIORITIES.map((code) => <option key={code} value={code}>{priorityLabel[code]}</option>)}
        </select>
      </label>
      <div className="inline-fields">
        <label>Hạn cam kết (ngày)
          <input className={invalid('due_date')} type="date" value={form.due_date} onChange={set('due_date')} required />
        </label>
        <label>Giờ
          <input className={invalid('due_date')} type="time" value={form.due_time} onChange={set('due_time')} required />
        </label>
      </div>
      {error && <div className="notice error wide">{error.message}</div>}
      <div className="form-actions wide">
        <button className="button secondary" type="button" onClick={onClose} disabled={busy}>Đóng</button>
        <button className="button" type="submit" disabled={busy}>{busy ? 'Đang lưu…' : editing ? 'Lưu thay đổi' : 'Tạo phiếu'}</button>
      </div>
    </form>
  );
}
