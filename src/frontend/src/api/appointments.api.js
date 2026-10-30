// API contract: POST /api/appointments accepts ticket_id, appointment_type, start_at, end_at, and note; conflict responses include conflicts and free_slots.
import { request } from './client.js';

export const createAppointment = (appointment) =>
  request('/api/appointments', {
    method: 'POST',
    body: JSON.stringify(appointment),
  });
