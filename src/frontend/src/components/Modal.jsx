import { useEffect, useId } from 'react';

// Accessible dialog: Escape closes it, focus stays inside the page behind a dimmed backdrop.
export default function Modal({ title, onClose, children, wide = false }) {
  const titleId = useId();
  useEffect(() => {
    const onKey = (event) => { if (event.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [onClose]);

  return (
    <div className="modal-backdrop" onMouseDown={(event) => { if (event.target === event.currentTarget) onClose(); }}>
      <div className={`modal ${wide ? 'wide' : ''}`} role="dialog" aria-modal="true" aria-labelledby={titleId}>
        <h3 id={titleId}>{title}</h3>
        {children}
      </div>
    </div>
  );
}
