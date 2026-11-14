// API contract: snake_case fields from /api/tickets, /api/tickets/{id}, assignment, status, technician-suggestions, and appointments endpoints.
import { request } from './client.js';

const queryString = (params) => new URLSearchParams(params).toString();

export const listTickets = (params = {}) =>
  request(`/api/tickets?${queryString(params)}`);

// Number of tickets of the manager's center in one status (only the total is read).
export const countTickets = (status) =>
  listTickets({ status, page: '1', page_size: '1' }).then((result) => result.total);

export const getTicket = (ticketId) => request(`/api/tickets/${ticketId}`);

export const createTicket = (ticket) =>
  request('/api/tickets', { method: 'POST', body: JSON.stringify(ticket) });

export const updateTicket = (ticketId, ticket) =>
  request(`/api/tickets/${ticketId}`, { method: 'PUT', body: JSON.stringify(ticket) });

// Soft delete: a MOI ticket becomes DA_HUY (QT-13).
export const cancelTicket = (ticketId, reason = '') =>
  request(`/api/tickets/${ticketId}${reason.trim() ? `?${queryString({ reason: reason.trim() })}` : ''}`, {
    method: 'DELETE',
  });

export const getTicketAppointments = (ticketId) =>
  request(`/api/tickets/${ticketId}/appointments`);

export const getSuggestions = (ticketId) =>
  request(`/api/tickets/${ticketId}/technician-suggestions`);

export const assignTicket = (ticketId, technicianId) =>
  request(`/api/tickets/${ticketId}/assignment`, {
    method: 'POST',
    body: JSON.stringify({ technician_id: technicianId }),
  });

export const changeAssignment = (ticketId, technicianId, reason) =>
  request(`/api/tickets/${ticketId}/assignment`, {
    method: 'PUT',
    body: JSON.stringify({ technician_id: technicianId, reason }),
  });

export const updateStatus = (ticketId, toStatus, note = '') =>
  request(`/api/tickets/${ticketId}/status`, {
    method: 'PATCH',
    body: JSON.stringify({ to_status: toStatus, note }),
  });
