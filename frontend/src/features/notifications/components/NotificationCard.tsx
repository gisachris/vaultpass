import { useMemo, useState } from 'react';
import { formatDistanceToNowStrict, parseISO } from 'date-fns';
import { Notification } from '../types/notification.types';
import { NotificationMenu } from './NotificationMenu';

interface NotificationCardProps {
  notification: Notification;
  onViewDetails: (notificationId: string) => void;
  onMarkRead: (notificationId: string) => void;
  onMarkUnread: (notificationId: string) => void;
  onDismiss: (notificationId: string) => void;
  onDelete: (notificationId: string) => void;
}

const typeMap: Record<Notification['type'], { icon: string; colorClass: string }> = {
  WARNING: { icon: 'warning', colorClass: 'notification-icon--warning' },
  ERROR: { icon: 'error', colorClass: 'notification-icon--error' },
  SUCCESS: { icon: 'check_circle', colorClass: 'notification-icon--success' },
  INFO: { icon: 'info', colorClass: 'notification-icon--info' },
};

export function NotificationCard({
  notification,
  onViewDetails,
  onMarkRead,
  onMarkUnread,
  onDismiss,
  onDelete,
}: NotificationCardProps) {
  const [menuOpen, setMenuOpen] = useState(false);

  const relativeTime = useMemo(() => {
    return formatDistanceToNowStrict(parseISO(notification.created_at), {
      addSuffix: true,
      roundingMethod: 'floor',
    });
  }, [notification.created_at]);

  const typeItem = typeMap[notification.type];

  return (
    <article className={`notification-card ${notification.is_read ? '' : 'notification-card--unread'}`}>
      <div className="notification-card__icon-container">
        <span className={`material-symbols-outlined notification-card__icon ${typeItem.colorClass}`}>
          {typeItem.icon}
        </span>
      </div>

      <div className="notification-card__content">
        <div className="notification-card__header">
          <button type="button" className="notification-card__title" onClick={() => onViewDetails(notification.id)}>
            {notification.title}
          </button>
          <span className="notification-card__time">{relativeTime}</span>
        </div>
        <p className="notification-card__message">{notification.message}</p>
        <div className="notification-card__actions">
          <button
            type="button"
            className="button button-primary notification-card__action-button"
            onClick={() => onViewDetails(notification.id)}
          >
            View details
          </button>
          <button
            type="button"
            className="button button-secondary notification-card__action-button"
            onClick={() => onDismiss(notification.id)}
          >
            {notification.is_read ? 'Mark unread' : 'Mark read'}
          </button>
        </div>
      </div>

      <div className="notification-card__menu">
        <button
          type="button"
          className="notification-card__menu-button"
          onClick={() => setMenuOpen((current) => !current)}
          aria-haspopup="true"
          aria-expanded={menuOpen}
        >
          <span className="material-symbols-outlined">more_vert</span>
        </button>
        <NotificationMenu
          open={menuOpen}
          onClose={() => setMenuOpen(false)}
          isRead={notification.is_read}
          onViewDetails={() => {
            setMenuOpen(false);
            onViewDetails(notification.id);
          }}
          onMarkRead={() => {
            setMenuOpen(false);
            onMarkRead(notification.id);
          }}
          onMarkUnread={() => {
            setMenuOpen(false);
            onMarkUnread(notification.id);
          }}
          onDelete={() => {
            setMenuOpen(false);
            onDelete(notification.id);
          }}
        />
      </div>
    </article>
  );
}
