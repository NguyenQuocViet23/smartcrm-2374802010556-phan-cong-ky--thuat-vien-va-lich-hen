// API contract: POST /api/auth/login {username, password}; GET /api/auth/me returns role, center_id, technician_id, full_name, employee_id.
import { request } from './client.js';

export const login = (credentials) =>
  request('/api/auth/login', {
    method: 'POST',
    body: JSON.stringify(credentials),
    skipAuthRedirect: true,
  });

export const getMe = () => request('/api/auth/me');
