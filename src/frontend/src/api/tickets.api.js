// API contract: snake_case fields from /api/tickets, /api/tickets/{id}, assignment, status, technician-suggestions, and appointments endpoints.
import { request } from './client.js';

const queryString = (params) => new URLSearchParams(params).toString();

export const listTickets = (params = {}) =>
  request(`/api/tickets?${queryString(params)}`);

export const getTicket = (ticketId) => request(`/api/tickets/${ticketId}`);

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
