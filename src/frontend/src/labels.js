// Vietnamese display labels and formatting for codes returned by the API (one place for every page).
export const priorityLabel = { CAO: 'CAO', TRUNG_BINH: 'TRUNG BÌNH', THAP: 'THẤP' };
export const PRIORITIES = ['CAO', 'TRUNG_BINH', 'THAP'];

export const statusLabel = {
  MOI: 'MỚI', DA_PHAN_CONG: 'ĐÃ PHÂN CÔNG', DANG_XU_LY: 'ĐANG XỬ LÝ',
  CHO_LINH_KIEN: 'CHỜ LINH KIỆN', HOAN_TAT: 'HOÀN TẤT',
  DA_DONG: 'ĐÃ ĐÓNG', DA_HUY: 'ĐÃ HỦY',
};
export const IN_PROGRESS = ['DA_PHAN_CONG', 'DANG_XU_LY', 'CHO_LINH_KIEN'];
export const CLOSED = ['HOAN_TAT', 'DA_DONG', 'DA_HUY'];

export const categoryLabel = {
  MAN_HINH: 'Màn hình', PIN: 'Pin', SAC: 'Sạc', PHAN_MEM: 'Phần mềm', NUOC_VAO: 'Vào nước', KHAC: 'Khác',
};
export const CATEGORIES = Object.keys(categoryLabel);

// The code stays visible ("NHAN") next to the words: staff and the tests both read it.
export const appointmentTypeLabel = { GIAO: 'Giao máy (GIAO)', NHAN: 'Nhận máy (NHAN)' };
export const appointmentStatusLabel = { DA_HEN: 'ĐÃ HẸN', DA_HUY: 'ĐÃ HỦY' };

export const formatDateTime = (value) => new Date(value).toLocaleString('vi-VN');
export const formatTime = (value) =>
  new Date(value).toLocaleTimeString('vi-VN', { hour: '2-digit', minute: '2-digit' });
export const appointmentRange = (appointment) =>
  `${new Date(appointment.start_at).toLocaleString('vi-VN')}–${new Date(appointment.end_at).toLocaleTimeString('vi-VN')}`;

// Dates and times of the business are in Vietnam time (UTC+7) whatever the browser's zone is.
const VN_OFFSET_MS = 7 * 60 * 60 * 1000;
export function vnParts(value) {
  const shifted = new Date(new Date(value).getTime() + VN_OFFSET_MS).toISOString();
  return { date: shifted.slice(0, 10), time: shifted.slice(11, 16) };
}
export function vnToday() {
  return vnParts(new Date()).date;
}
export const toVnIso = (date, time) => new Date(`${date}T${time}:00+07:00`).toISOString();

export const isOverdue = (ticket) => !CLOSED.includes(ticket.status) && new Date(ticket.due_date) < new Date();
