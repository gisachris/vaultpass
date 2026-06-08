import { useEffect, useRef } from 'react';

interface NotificationMenuProps {
  open: boolean;
  onClose: () => void;
  onMarkRead: () => void;
  onMarkUnread: () => void;
  onViewDetails: () => void;
  onDelete: () => void;
  isRead: boolean;
}

export function NotificationMenu({
  open,
  onClose,
  onMarkRead,
  onMarkUnread,
  onViewDetails,
  onDelete,
  isRead,
}: NotificationMenuProps) {
  const menuRef = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) {
      return;
    }

    const handleClickOutside = (event: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(event.target as Node)) {
        onClose();
      }
    };

    window.addEventListener('mousedown', handleClickOutside);
    return () => window.removeEventListener('mousedown', handleClickOutside);
  }, [open, onClose]);

  if (!open) {
    return null;
  }

  return (
    <div className="notification-menu" ref={menuRef} role="menu">
      <button type="button" onClick={onViewDetails}>
        View details
      </button>
      {isRead ? (
        <button type="button" onClick={onMarkUnread}>
          Mark unread
        </button>
      ) : (
        <button type="button" onClick={onMarkRead}>
          Mark read
        </button>
      )}
      <button type="button" onClick={onDelete} className="notification-menu__danger">
        Delete
      </button>
    </div>
  );
}
