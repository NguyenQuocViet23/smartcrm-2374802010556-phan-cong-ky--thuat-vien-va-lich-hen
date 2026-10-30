export default function DataState({
  loading,
  error,
  isEmpty,
  emptyMessage,
  onRetry,
  children,
}) {
  if (loading) {
    return <div className="state-card" data-testid="state-loading">Đang tải dữ liệu…</div>;
  }
  if (error) {
    const forbiddenCopy =
      error.status === 403
        ? error.body?.message || 'Bạn không có quyền xem dữ liệu này.'
        : error.message || 'Không thể tải dữ liệu.';
    return (
      <div className={`state-card error ${error.status === 403 ? 'forbidden' : ''}`} data-testid="state-error" role="alert">
        <p>{forbiddenCopy}</p>
        <button type="button" data-testid="retry-button" onClick={onRetry}>Thử lại</button>
      </div>
    );
  }
  if (isEmpty) {
    return <div className="state-card" data-testid="state-empty">{emptyMessage}</div>;
  }
  return children;
}
