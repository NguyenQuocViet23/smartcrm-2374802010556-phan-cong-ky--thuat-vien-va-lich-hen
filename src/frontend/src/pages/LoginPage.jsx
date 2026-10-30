import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { getMe, login } from '../api/auth.api.js';

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const navigate = useNavigate();

  async function submit(event) {
    event.preventDefault();
    setBusy(true);
    setError('');
    try {
      const result = await login({ username, password });
      localStorage.setItem('access_token', result.access_token);
      const user = await getMe();
      onLogin(user);
      navigate(user.role === 'QUAN_LY' ? '/tickets' : '/my-tickets', { replace: true });
    } catch (requestError) {
      localStorage.removeItem('access_token');
      setError(requestError.message || 'Sai tên đăng nhập hoặc mật khẩu');
    } finally {
      setBusy(false);
    }
  }

  return (
    <main className="login-page">
      <form className="login-card" onSubmit={submit}>
        <h1>Smart CRM</h1>
        <p>Mekong Mobile · Đăng nhập</p>
        <label>Tên đăng nhập
          <input autoComplete="username" value={username} onChange={(event) => setUsername(event.target.value)} required />
        </label>
        <label>Mật khẩu
          <input type="password" autoComplete="current-password" value={password} onChange={(event) => setPassword(event.target.value)} required />
        </label>
        {error && <div className="notice error" role="alert">{error}</div>}
        <button className="button" type="submit" disabled={busy}>{busy ? 'Đang đăng nhập…' : 'Đăng nhập'}</button>
      </form>
    </main>
  );
}
