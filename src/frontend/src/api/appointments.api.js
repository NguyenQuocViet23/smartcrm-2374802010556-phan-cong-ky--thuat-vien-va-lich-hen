// API contract: POST /api/appointments accepts ticket_id, appointment_type, start_at, end_at, and note; conflict responses include conflicts and free_slots.
// GET /api/appointments is scoped by the backend: a manager gets the center's appointments, a technician only their own.
import { request } from './client.js';

export const createAppointment = (appointment) =>
  request('/api/appointments', {
    method: 'POST',
    body: JSON.stringify(appointment),
  });

export const listAppointments = (params = {}) =>
  request(`/api/appointments?${new URLSearchParams(params).toString()}`);

// Every appointment the user may see (a center has a few hundred at most), newest start first.
export async function listAllAppointments(params = {}) {
  const items = [];
  for (let page = 1; page <= 20; page += 1) {
    const result = await listAppointments({ ...params, page: String(page), page_size: '100' });
    items.push(...result.items);
    if (items.length >= result.total || !result.items.length) break;
  }
  return items;
}

export const updateAppointment = (appointmentId, appointment) =>
  request(`/api/appointments/${appointmentId}`, {
    method: 'PUT',
    body: JSON.stringify(appointment),
  });

// Soft cancel: status DA_HUY, the slot becomes free again.
export const cancelAppointment = (appointmentId) =>
  request(`/api/appointments/${appointmentId}`, { method: 'DELETE' });
