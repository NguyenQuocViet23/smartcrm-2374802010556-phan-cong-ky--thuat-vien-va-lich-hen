import { useEffect, useState } from 'react';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { getMe } from './api/auth.api.js';
import AssignTechnicianPage from './pages/AssignTechnicianPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import MyTicketsPage from './pages/MyTicketsPage.jsx';
import PendingTicketsPage from './pages/PendingTicketsPage.jsx';

export default function App() {
  const [user, setUser] = useState(null);
  const [checking, setChecking] = useState(Boolean(localStorage.getItem('access_token')));
  const location = useLocation();

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) return;
    getMe()
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setChecking(false));
  }, [location.pathname]);

  function logout() {
    localStorage.removeItem('access_token');
    setUser(null);
    window.location.assign('/login');
  }

  if (checking) return <div className="state-card" data-testid="state-loading">Đang tải dữ liệu…</div>;

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to={user.role === 'QUAN_LY' ? '/tickets' : '/my-tickets'} replace /> : <LoginPage onLogin={setUser} />} />
      <Route path="/tickets" element={user?.role === 'QUAN_LY' ? <PendingTicketsPage user={user} onLogout={logout} /> : <Navigate to={user ? '/my-tickets' : '/login'} replace />} />
      <Route path="/tickets/:id/assign" element={user?.role === 'QUAN_LY' ? <AssignTechnicianPage user={user} onLogout={logout} /> : <Navigate to={user ? '/my-tickets' : '/login'} replace />} />
      <Route path="/my-tickets" element={user?.role === 'KY_THUAT_VIEN' ? <MyTicketsPage user={user} onLogout={logout} /> : <Navigate to={user ? '/tickets' : '/login'} replace />} />
      <Route path="*" element={<Navigate to={user ? (user.role === 'QUAN_LY' ? '/tickets' : '/my-tickets') : '/login'} replace />} />
    </Routes>
  );
}
