import { useCallback, useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { listTickets } from '../api/tickets.api.js';
import AppHeader from '../components/AppHeader.jsx';
import DataState from '../components/DataState.jsx';

const priorities = ['CAO', 'TRUNG_BINH', 'THAP'];
const priorityLabel = { CAO: 'CAO', TRUNG_BINH: 'TRUNG BÌNH', THAP: 'THẤP' };

export default function PendingTicketsPage({ user, onLogout }) {
  const [items, setItems] = useState([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [category, setCategory] = useState('');
  const [priority, setPriority] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await listTickets({
        status: 'MOI',
        category_code: category,
        priority,
        page: String(page),
        page_size: '20',
      });
      setItems(result.items);
      setTotal(result.total);
    } catch (requestError) {
      setError(requestError);
    } finally {
      setLoading(false);
    }
  }, [category, priority, page]);

  useEffect(() => { load(); }, [load]);

  return (
    <>
      <AppHeader title="Phiếu chờ phân công" user={user} onLogout={onLogout} />
      <main className="page">
        <section className="filters panel">
          <label>Nhóm sự cố
            <select value={category} onChange={(event) => { setCategory(event.target.value); setPage(1); }}>
              <option value="">Tất cả</option>
              {['MAN_HINH', 'PIN', 'SAC', 'PHAN_MEM', 'NUOC_VAO', 'KHAC'].map((item) => <option key={item}>{item}</option>)}
            </select>
          </label>
          <label>Mức ưu tiên
            <select value={priority} onChange={(event) => { setPriority(event.target.value); setPage(1); }}>
              <option value="">Tất cả</option>
              {priorities.map((item) => <option key={item} value={item}>{priorityLabel[item]}</option>)}
            </select>
          </label>
        </section>
        <DataState loading={loading} error={error} isEmpty={!items.length} emptyMessage="Không có phiếu chờ phân công" onRetry={load}>
          <div className="panel table-wrap">
            <table>
              <thead><tr><th>Mã phiếu</th><th>Khách hàng</th><th>Số điện thoại</th><th>Nhóm sự cố</th><th>Mức ưu tiên</th><th>Hạn cam kết</th><th>Thao tác</th></tr></thead>
              <tbody>{items.map((ticket) => (
                <tr key={ticket.ticket_id}>
                  <td>{ticket.ticket_code}</td>
                  <td>{ticket.customer_name}</td>
                  <td>{ticket.customer_phone}</td>
                  <td>{ticket.category_code}</td>
                  <td>{priorityLabel[ticket.priority]}</td>
                  <td>{new Date(ticket.due_date).toLocaleString('vi-VN')}{new Date(ticket.due_date) < new Date() && <strong className="overdue"> QUÁ HẠN</strong>}</td>
                  <td><button className="button small" onClick={() => navigate(`/tickets/${ticket.ticket_id}/assign`)}>Phân công</button></td>
                </tr>
              ))}</tbody>
            </table>
            <footer className="pagination">
              <span>Tổng số phiếu: {total}</span>
              <button className="button secondary" disabled={page <= 1} onClick={() => setPage((value) => value - 1)}>Trước</button>
              <span>Trang {page} / {Math.max(1, Math.ceil(total / 20))}</span>
              <button className="button secondary" disabled={page >= Math.ceil(total / 20)} onClick={() => setPage((value) => value + 1)}>Sau</button>
            </footer>
          </div>
        </DataState>
      </main>
    </>
  );
}
