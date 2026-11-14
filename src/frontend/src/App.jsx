import { useEffect, useState } from 'react';
import { Navigate, Route, Routes, useLocation } from 'react-router-dom';
import { getMe } from './api/auth.api.js';
import AppointmentsPage from './pages/AppointmentsPage.jsx';
import AssignTechnicianPage from './pages/AssignTechnicianPage.jsx';
import LoginPage from './pages/LoginPage.jsx';
import MyTicketsPage from './pages/MyTicketsPage.jsx';
import PendingTicketsPage from './pages/PendingTicketsPage.jsx';

const homeOf = (user) => (user ? (user.role === 'QUAN_LY' ? '/tickets' : '/my-tickets') : '/login');

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

  const manager = user?.role === 'QUAN_LY';
  const technician = user?.role === 'KY_THUAT_VIEN';
  const managerPage = (page) => (manager ? page : <Navigate to={homeOf(user)} replace />);

  return (
    <Routes>
      <Route path="/login" element={user ? <Navigate to={homeOf(user)} replace /> : <LoginPage onLogin={setUser} />} />
      <Route path="/tickets" element={managerPage(<PendingTicketsPage user={user} onLogout={logout} />)} />
      <Route path="/tickets/:id" element={managerPage(<AssignTechnicianPage user={user} onLogout={logout} />)} />
      <Route path="/tickets/:id/assign" element={managerPage(<AssignTechnicianPage user={user} onLogout={logout} />)} />
      <Route path="/my-tickets" element={technician ? <MyTicketsPage user={user} onLogout={logout} /> : <Navigate to={homeOf(user)} replace />} />
      <Route path="/appointments" element={user ? <AppointmentsPage user={user} onLogout={logout} /> : <Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to={homeOf(user)} replace />} />
    </Routes>
  );
}
