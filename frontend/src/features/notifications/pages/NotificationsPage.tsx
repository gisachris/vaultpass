import { Link } from 'react-router-dom';
import { useMemo, useState } from 'react';
import { toast } from 'sonner';
import { NotificationCard } from '../components/NotificationCard';
import { NotificationEmptyState } from '../components/NotificationEmptyState';
import { NotificationFilters } from '../components/NotificationFilters';
import { NotificationPagination } from '../components/NotificationPagination';
import { NotificationPreferences } from '../components/NotificationPreferences';
import { useNotifications } from '../hooks/useNotifications';
import { fetchNotificationDetails } from '../api/notificationApi';
import { Notification } from '../types/notification.types';
import '../components/NotificationCard.css';
import '../components/NotificationFilters.css';
import '../components/NotificationPreferences.css';
import './NotificationsPage.css';

function formatDate(value: string) {
  return new Date(value).toLocaleString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  });
}

export function NotificationsPage() {
  const {
    notifications,
    page,
    pages,
    limit,
    unreadCount,
    filter,
    typeFilter,
    sorting,
    loading,
    actionLoading,
    error,
    setPage,
    setFilter,
    setTypeFilter,
    setSorting,
    refresh,
    markAllRead,
    markRead,
    markUnread,
    deleteNotification,
    deleteAll,
  } = useNotifications();

  const [detailsOpen, setDetailsOpen] = useState(false);
  const [selectedNotification, setSelectedNotification] = useState<Notification | null>(null);
  const [detailsLoading, setDetailsLoading] = useState(false);
  const [showDeleteAllConfirm, setShowDeleteAllConfirm] = useState(false);
  const [pendingDeleteId, setPendingDeleteId] = useState<string | null>(null);

  const hasNotifications = notifications.length > 0;

  const handleViewDetails = async (notificationId: string) => {
    setDetailsLoading(true);
    try {
      const notification = await fetchNotificationDetails(notificationId);
      setSelectedNotification(notification);
      setDetailsOpen(true);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Unable to load notification details.');
    } finally {
      setDetailsLoading(false);
    }
  };

  const handleDelete = async (notificationId: string) => {
    setPendingDeleteId(notificationId);
  };

  const confirmDelete = async () => {
    if (!pendingDeleteId) {
      return;
    }
    try {
      await deleteNotification(pendingDeleteId);
      toast.success('Notification deleted.');
      setPendingDeleteId(null);
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Unable to delete notification.');
    }
  };

  const handleDeleteAll = async () => {
    setShowDeleteAllConfirm(false);
    try {
      await deleteAll();
      toast.success('All notifications cleared.');
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Unable to clear notifications.');
    }
  };

  const headerBadge = useMemo(() => {
    if (unreadCount === 0) return null;
    return <span className="notification-header-badge">{unreadCount}</span>;
  }, [unreadCount]);

  return (
    <div className="notifications-page">
      <aside className="notifications-sidebar">
        <div className="notifications-sidebar__brand">
          <h1>VaultPass</h1>
          <p>Secure Document Vault</p>
        </div>

        <div className="notifications-sidebar__links">
          <Link className="notifications-sidebar__link" to="/dashboard">
            <span className="material-symbols-outlined">dashboard</span>
            Dashboard
          </Link>
          <Link className="notifications-sidebar__link" to="/documents">
            <span className="material-symbols-outlined">description</span>
            Documents
          </Link>
          <Link className="notifications-sidebar__link" to="/trusted-contacts">
            <span className="material-symbols-outlined">group</span>
            Trusted Contacts
          </Link>
          <Link to="/notifications" className="notifications-sidebar__link notifications-sidebar__link--active">
            <span className="material-symbols-outlined">notifications</span>
            Notifications
            {headerBadge}
          </Link>
          <button type="button" className="notifications-sidebar__link notifications-sidebar__link--disabled">
            <span className="material-symbols-outlined">settings</span>
            Settings
          </button>
        </div>
      </aside>

      <div className="notifications-main">
        <header className="notifications-topbar">
          <div className="notifications-topbar__search">
            <span className="material-symbols-outlined">search</span>
            <input placeholder="Search notifications..." disabled />
          </div>
          <div className="notifications-topbar__meta">
            <button type="button" className="icon-button" disabled>
              <span className="material-symbols-outlined">help_outline</span>
            </button>
            <div className="notifications-avatar">
              <img
                src="https://images.unsplash.com/photo-1502685104226-ee32379fefbe?auto=format&fit=crop&w=256&q=80"
                alt="User profile"
              />
            </div>
          </div>
        </header>

        <main className="notifications-canvas">
          <section className="notifications-hero">
            <div>
              <h1>Notifications</h1>
              <p>Review recent alerts and account activity.</p>
            </div>
            <button type="button" className="button button-primary" onClick={markAllRead} disabled={loading || actionLoading}>
              Mark all as read
            </button>
          </section>

          <div className="notifications-grid">
            <div className="notifications-list-panel">
              <NotificationFilters
                filter={filter}
                typeFilter={typeFilter}
                sorting={sorting}
                unreadCount={unreadCount}
                onFilterChange={setFilter}
                onTypeFilterChange={setTypeFilter}
                onSortingChange={setSorting}
                onClearAll={() => setShowDeleteAllConfirm(true)}
              />

              <section className="notifications-list">
                {loading ? (
                  <div className="notifications-skeleton">
                    {[1, 2, 3].map((item) => (
                      <div key={item} className="notification-card notification-card--skeleton">
                        <div className="notification-card__icon-container" />
                        <div className="notification-card__content">
                          <div className="notification-card__header">
                            <div className="notification-card__title notification-card__title--skeleton" />
                            <div className="notification-card__time notification-card__time--skeleton" />
                          </div>
                          <div className="notification-card__message notification-card__message--skeleton" />
                          <div className="notification-card__actions">
                            <div className="notification-card__button notification-card__button--skeleton" />
                            <div className="notification-card__button notification-card__button--skeleton" />
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                ) : error ? (
                  <div className="notifications-error">
                    {error}
                  </div>
                ) : !hasNotifications ? (
                  <NotificationEmptyState />
                ) : (
                  <div className="notifications-list-items">
                    {notifications.map((notification) => (
                      <NotificationCard
                        key={notification.id}
                        notification={notification}
                        onViewDetails={handleViewDetails}
                        onMarkRead={markRead}
                        onMarkUnread={markUnread}
                        onDismiss={notification.is_read ? markUnread : markRead}
                        onDelete={handleDelete}
                      />
                    ))}
                  </div>
                )}

                <NotificationPagination
                  page={page}
                  pages={pages}
                  onPrevious={() => setPage(Math.max(1, page - 1))}
                  onNext={() => setPage(Math.min(pages, page + 1))}
                  loading={loading}
                />
              </section>
            </div>

            <aside className="notifications-sidepanel">
              <NotificationPreferences />
            </aside>
          </div>
        </main>

        {detailsOpen && selectedNotification && (
          <div className="notification-details-modal" onClick={() => setDetailsOpen(false)}>
            <div className="notification-details-modal__window" onClick={(event) => event.stopPropagation()}>
              <div className="notification-details-modal__header">
                <div>
                  <h2>{selectedNotification.title}</h2>
                  <p>{selectedNotification.type} notification details</p>
                </div>
                <button type="button" className="documents-modal-close" onClick={() => setDetailsOpen(false)}>
                  ×
                </button>
              </div>

              <div className="notification-details-modal__body">
                <div>
                  <h3>Message</h3>
                  <p>{selectedNotification.message}</p>
                </div>
                <div>
                  <h3>Type</h3>
                  <p>{selectedNotification.type}</p>
                </div>
                <div>
                  <h3>Created</h3>
                  <p>{formatDate(selectedNotification.created_at)}</p>
                </div>
                {selectedNotification.updated_at && (
                  <div>
                    <h3>Updated</h3>
                    <p>{formatDate(selectedNotification.updated_at)}</p>
                  </div>
                )}
                {selectedNotification.related_document_id && (
                  <div>
                    <h3>Related document</h3>
                    <p>{selectedNotification.related_document_id}</p>
                  </div>
                )}
                {selectedNotification.related_contact_id && (
                  <div>
                    <h3>Related contact</h3>
                    <p>{selectedNotification.related_contact_id}</p>
                  </div>
                )}
                {selectedNotification.related_share_id && (
                  <div>
                    <h3>Related share</h3>
                    <p>{selectedNotification.related_share_id}</p>
                  </div>
                )}
              </div>
            </div>
          </div>
        )}

        {pendingDeleteId && (
          <div className="notification-delete-modal" onClick={() => setPendingDeleteId(null)}>
            <div className="notification-delete-modal__window" onClick={(event) => event.stopPropagation()}>
              <div className="notification-delete-modal__header">
                <h2>Delete notification</h2>
                <button type="button" className="documents-modal-close" onClick={() => setPendingDeleteId(null)}>
                  ×
                </button>
              </div>
              <div className="notification-delete-modal__body">
                <p>Are you sure you want to delete this notification? This cannot be undone.</p>
              </div>
              <div className="notification-delete-modal__actions">
                <button type="button" className="button button-secondary" onClick={() => setPendingDeleteId(null)}>
                  Cancel
                </button>
                <button type="button" className="button button-primary" onClick={confirmDelete} disabled={actionLoading}>
                  Delete
                </button>
              </div>
            </div>
          </div>
        )}

        {showDeleteAllConfirm && (
          <div className="notification-delete-modal" onClick={() => setShowDeleteAllConfirm(false)}>
            <div className="notification-delete-modal__window" onClick={(event) => event.stopPropagation()}>
              <div className="notification-delete-modal__header">
                <h2>Clear all notifications</h2>
                <button type="button" className="documents-modal-close" onClick={() => setShowDeleteAllConfirm(false)}>
                  ×
                </button>
              </div>
              <div className="notification-delete-modal__body">
                <p>Are you sure you want to clear all notifications? This action cannot be undone.</p>
              </div>
              <div className="notification-delete-modal__actions">
                <button type="button" className="button button-secondary" onClick={() => setShowDeleteAllConfirm(false)}>
                  Cancel
                </button>
                <button type="button" className="button button-primary" onClick={handleDeleteAll} disabled={actionLoading}>
                  Clear all
                </button>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
