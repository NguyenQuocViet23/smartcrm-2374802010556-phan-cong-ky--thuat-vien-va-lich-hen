// API contract: GET /api/technicians/me/tickets returns technician-scoped ticket fields in snake_case.
import { request } from './client.js';

export const getMyTickets = () => request('/api/technicians/me/tickets');
