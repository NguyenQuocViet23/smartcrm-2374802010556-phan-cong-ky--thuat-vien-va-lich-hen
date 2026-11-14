import Modal from './Modal.jsx';

// Confirmation for actions that cannot be undone from the screen (cancel a ticket or an appointment,
// finish a ticket). The cancel button says "Quay lại" so it never clashes with "Hủy …" buttons.
export default function ConfirmDialog({
  title, message, confirmLabel = 'Xác nhận', danger = false, busy = false, error = null,
  onConfirm, onCancel, children,
}) {
  return (
    <Modal title={title} onClose={onCancel}>
      {message && <p>{message}</p>}
      {children}
      {error && <div className="notice error">{error.message || String(error)}</div>}
      <div className="form-actions">
        <button className="button secondary" type="button" onClick={onCancel} disabled={busy}>Quay lại</button>
        <button className={`button ${danger ? 'danger' : ''}`} type="button" onClick={onConfirm} disabled={busy}>
          {busy ? 'Đang xử lý…' : confirmLabel}
        </button>
      </div>
    </Modal>
  );
}
