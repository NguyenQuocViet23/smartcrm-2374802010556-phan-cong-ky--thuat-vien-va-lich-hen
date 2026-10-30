export default function AppHeader({ title, user, onLogout }) {
  return (
    <header className="app-header">
      <div>
        <strong>Smart CRM · Mekong Mobile</strong>
        <span>{title}</span>
      </div>
      <div className="header-user">
        <span>{user?.role === 'QUAN_LY' ? `Trung tâm: ${user.center_name}` : user?.full_name}</span>
        <button className="button secondary" type="button" onClick={onLogout}>Đăng xuất</button>
      </div>
    </header>
  );
}
