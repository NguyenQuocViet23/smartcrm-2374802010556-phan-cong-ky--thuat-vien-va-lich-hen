import { appointmentStatusLabel, statusLabel } from '../labels.js';

// Coloured status chip; the text is exactly the existing label (e.g. "ĐÃ PHÂN CÔNG").
export default function StatusBadge({ status, kind = 'ticket' }) {
  const label = kind === 'appointment' ? appointmentStatusLabel[status] : statusLabel[status];
  return <span className={`badge badge-${status}`}>{label || status}</span>;
}
