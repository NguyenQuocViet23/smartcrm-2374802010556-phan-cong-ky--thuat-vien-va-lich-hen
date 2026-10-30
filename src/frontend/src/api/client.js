const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export class ApiError extends Error {
  constructor(status, body) {
    super(body?.message || 'Không thể kết nối máy chủ.');
    this.status = status;
    this.code = body?.error || 'REQUEST_FAILED';
    this.body = body;
  }
}

export async function request(path, options = {}) {
  const token = localStorage.getItem('access_token');
  const headers = new Headers(options.headers || {});
  if (token) headers.set('Authorization', `Bearer ${token}`);
  if (options.body && !headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json');
  }

  let response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, { ...options, headers });
  } catch (error) {
    throw new ApiError(0, { error: 'NETWORK_ERROR', message: 'Không thể kết nối máy chủ. Vui lòng thử lại.' });
  }

  const body = response.status === 204 ? null : await response.json().catch(() => null);
  if (response.status === 401 && !options.skipAuthRedirect) {
    localStorage.removeItem('access_token');
    window.location.assign('/login');
  }
  if (!response.ok) throw new ApiError(response.status, body);
  return body;
}
