import { NavLink } from 'react-router-dom';

const LINKS = {
  QUAN_LY: [['/tickets', 'Phiếu'], ['/appointments', 'Lịch hẹn']],
  KY_THUAT_VIEN: [['/my-tickets', 'Phiếu của tôi'], ['/appointments', 'Lịch hẹn của tôi']],
};

export default function AppHeader({ title, user, onLogout }) {
  return (
    <header className="app-header">
      <div className="brand">
        <strong>Smart CRM · Mekong Mobile</strong>
        <span>{title}</span>
      </div>
      <nav className="main-nav" aria-label="Điều hướng chính">
        {(LINKS[user?.role] || []).map(([to, label]) => (
          <NavLink key={to} to={to} className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>{label}</NavLink>
        ))}
      </nav>
      <div className="header-user">
        <span>{user?.role === 'QUAN_LY' ? `Trung tâm: ${user.center_name}` : user?.full_name}</span>
        <button className="button secondary" type="button" onClick={onLogout}>Đăng xuất</button>
      </div>
    </header>
  );
}
