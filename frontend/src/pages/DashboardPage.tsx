import { Link, useLocation } from 'react-router-dom';
import { useMemo } from 'react';
import { formatDistanceToNow, parseISO } from 'date-fns';
import { useDashboard } from '../hooks/useDashboard';
import './DashboardPage.css';

function formatStorageSize(mb: number): string {
  if (mb < 1024) {
    return `${mb.toFixed(1)} MB`;
  }
  return `${(mb / 1024).toFixed(1)} GB`;
}

function formatDate(isoString: string): string {
  try {
    return new Date(isoString).toLocaleDateString(undefined, {
      month: 'short',
      day: 'numeric',
      year: 'numeric',
    });
  } catch {
    return 'Unknown date';
  }
}

function getExpiryStatusColor(daysRemaining: number): string {
  if (daysRemaining < 0) return 'status-expired';
  if (daysRemaining <= 30) return 'status-urgent';
  if (daysRemaining <= 90) return 'status-warning';
  return 'status-valid';
}

function getExpiryStatusLabel(daysRemaining: number): string {
  if (daysRemaining < 0) return 'Expired';
  if (daysRemaining === 0) return 'Expires today';
  if (daysRemaining === 1) return 'Expires tomorrow';
  return `${daysRemaining} days left`;
}

function getActivityIcon(action: string): string {
  if (action.includes('LOGIN')) return 'login';
  if (action.includes('DOCUMENT')) return 'description';
  if (action.includes('CONTACT') || action.includes('TRUSTED')) return 'group';
  if (action.includes('SHARE')) return 'share';
  if (action.includes('PASSWORD') || action.includes('SECURITY')) return 'security';
  if (action.includes('SETTINGS')) return 'settings';
  return 'history';
}

export function DashboardPage() {
  const location = useLocation();
  const { data, loading, error, refresh } = useDashboard();

  const storagePercentage = useMemo(() => {
    if (!data?.account_overview.storage_used_mb) return 0;
    const totalStorage = 10 * 1024; // 10 GB
    return Math.min((data.account_overview.storage_used_mb / totalStorage) * 100, 100);
  }, [data?.account_overview.storage_used_mb]);

  const lastLoginDisplay = useMemo(() => {
    if (!data?.account_overview.last_login) return 'Never';
    return formatDistanceToNow(parseISO(data.account_overview.last_login), { addSuffix: true });
  }, [data?.account_overview.last_login]);

  if (error) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-error-state">
          <span className="material-symbols-outlined">error_outline</span>
          <h2>Unable to load dashboard</h2>
          <p>{error}</p>
          <button type="button" className="button button-primary" onClick={refresh}>
            Try again
          </button>
        </div>
      </div>
    );
  }

  if (loading || !data) {
    return (
      <div className="dashboard-page">
        <div className="dashboard-loading-state">
          <div className="spinner" />
          <p>Loading your dashboard…</p>
        </div>
      </div>
    );
  }

  return (
    <div className="dashboard-page">
      <nav className="documents-sidebar">
        <div className="documents-logo">
          <span>VaultPass</span>
          <span>Secure Document Vault</span>
        </div>

        <div className="documents-sidebar-cta">
          <Link to="/documents" className="button button-primary">
            <span className="material-symbols-outlined">upload_file</span>
            Upload Document
          </Link>
        </div>

        <div className="documents-sidebar-links">
          <Link to="/" className={`documents-sidebar-link ${location.pathname === '/' || location.pathname === '/dashboard' ? 'documents-sidebar-link--active' : ''}`}>
            <span className="material-symbols-outlined">dashboard</span>
            <span>Dashboard</span>
          </Link>
          <Link to="/documents" className="documents-sidebar-link">
            <span className="material-symbols-outlined">description</span>
            <span>Documents</span>
          </Link>
          <Link to="/trusted-contacts" className="documents-sidebar-link">
            <span className="material-symbols-outlined">group</span>
            <span>Trusted Contacts</span>
          </Link>
          <Link to="/notifications" className="documents-sidebar-link">
            <span className="material-symbols-outlined">notifications</span>
            <span>Notifications</span>
          </Link>
          <button type="button" className="documents-sidebar-link documents-sidebar-link--disabled">
            <span className="material-symbols-outlined">settings</span>
            <span>Settings</span>
          </button>
        </div>

        <div className="documents-sidebar-footer">
          <div className="sidebar-account-preview">
            <div className="sidebar-avatar">
              <img
                src="https://images.unsplash.com/photo-1502685104226-ee32379fefbe?auto=format&fit=crop&w=64&q=80"
                alt="Account"
              />
            </div>
            <div>
              <p className="sidebar-account-label">Account</p>
              <p className="sidebar-account-date">Created {formatDate(data.account_overview.account_created)}</p>
            </div>
          </div>
        </div>
      </nav>

      <div className="documents-main">
        <header className="documents-topbar">
          <div className="documents-search">
            <span className="material-symbols-outlined">search</span>
            <input type="text" placeholder="Search…" disabled />
          </div>
          <div className="documents-topbar-actions">
            <button type="button" className="icon-button" onClick={refresh} title="Refresh dashboard">
              <span className="material-symbols-outlined">refresh</span>
            </button>
            <button type="button" className="icon-button" aria-label="Help">
              <span className="material-symbols-outlined">help_outline</span>
            </button>
            <div className="documents-profile">
              <img
                src="https://images.unsplash.com/photo-1502685104226-ee32379fefbe?auto=format&fit=crop&w=256&q=80"
                alt="User profile"
              />
            </div>
          </div>
        </header>

        <main className="documents-canvas">
          <section className="documents-headline">
            <div>
              <h1>Dashboard</h1>
              <p>Welcome back. Here's your VaultPass overview.</p>
            </div>
            <div className="dashboard-meta">
              <span>Last login: {lastLoginDisplay}</span>
            </div>
          </section>

          {/* Overview Cards */}
          <section className="dashboard-overview-cards">
            <div className="metric-card">
              <div className="metric-icon">
                <span className="material-symbols-outlined">description</span>
              </div>
              <div className="metric-content">
                <p className="metric-label">Documents</p>
                <h3 className="metric-value">{data.summary.total_documents}</h3>
                <p className="metric-sublabel">
                  {data.document_health.valid_documents} valid, {data.document_health.expired_documents} expired
                </p>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">
                <span className="material-symbols-outlined">share</span>
              </div>
              <div className="metric-content">
                <p className="metric-label">Active Shares</p>
                <h3 className="metric-value">{data.summary.active_shares}</h3>
                <p className="metric-sublabel">Shared documents</p>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">
                <span className="material-symbols-outlined">group</span>
              </div>
              <div className="metric-content">
                <p className="metric-label">Trusted Contacts</p>
                <h3 className="metric-value">{data.summary.trusted_contacts}</h3>
                <p className="metric-sublabel">Total contacts</p>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon">
                <span className="material-symbols-outlined">notifications</span>
              </div>
              <div className="metric-content">
                <p className="metric-label">Notifications</p>
                <h3 className="metric-value">{data.summary.unread_notifications}</h3>
                <p className="metric-sublabel">Unread alerts</p>
              </div>
            </div>
          </section>

          {/* Main Grid */}
          <div className="dashboard-grid">
            {/* Left Column */}
            <div className="dashboard-left-column">
              {/* Expiring Documents */}
              <section className="dashboard-card">
                <div className="card-header">
                  <h2>Expiring Documents</h2>
                  <Link to="/documents" className="card-action-link">
                    View All
                  </Link>
                </div>
                {data.expiring_documents.length === 0 ? (
                  <div className="empty-state">
                    <span className="material-symbols-outlined">check_circle</span>
                    <p>No documents expiring soon</p>
                  </div>
                ) : (
                  <div className="expiring-list">
                    {data.expiring_documents.map((doc) => (
                      <div key={doc.document_id} className="expiring-item">
                        <div className="expiring-info">
                          <h4>{doc.document_name}</h4>
                          <p className="expiring-category">{doc.category}</p>
                        </div>
                        <div className={`expiring-status ${getExpiryStatusColor(doc.days_remaining)}`}>
                          {getExpiryStatusLabel(doc.days_remaining)}
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>

              {/* Recent Activity */}
              <section className="dashboard-card">
                <div className="card-header">
                  <h2>Recent Activity</h2>
                </div>
                {data.recent_activity.length === 0 ? (
                  <div className="empty-state">
                    <span className="material-symbols-outlined">history</span>
                    <p>No recent activity</p>
                  </div>
                ) : (
                  <div className="activity-feed">
                    {data.recent_activity.map((activity, idx) => (
                      <div key={idx} className="activity-item">
                        <div className="activity-icon">
                          <span className="material-symbols-outlined">{getActivityIcon(activity.action)}</span>
                        </div>
                        <div className="activity-content">
                          <p className="activity-description">{activity.description}</p>
                          <p className="activity-time">
                            {formatDistanceToNow(parseISO(activity.created_at), { addSuffix: true })}
                          </p>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            </div>

            {/* Right Column */}
            <div className="dashboard-right-column">
              {/* Storage Usage */}
              <section className="dashboard-card">
                <div className="card-header">
                  <h2>Storage</h2>
                </div>
                <div className="storage-section">
                  <div className="storage-chart">
                    <div className="storage-gauge">
                      <svg viewBox="0 0 100 100" className="storage-arc">
                        <circle cx="50" cy="50" r="45" className="storage-bg" />
                        <circle
                          cx="50"
                          cy="50"
                          r="45"
                          className="storage-fill"
                          style={{
                            strokeDasharray: `${(storagePercentage / 100) * 282.7} 282.7`,
                          }}
                        />
                      </svg>
                      <div className="storage-label">
                        <span className="storage-percentage">{storagePercentage.toFixed(0)}%</span>
                      </div>
                    </div>
                  </div>
                  <div className="storage-info">
                    <p className="storage-used">
                      {formatStorageSize(data.account_overview.storage_used_mb)} used
                    </p>
                    <p className="storage-total">of 10 GB</p>
                  </div>
                </div>
              </section>

              {/* Document Categories */}
              {data.categories.length > 0 && (
                <section className="dashboard-card">
                  <div className="card-header">
                    <h2>Categories</h2>
                  </div>
                  <div className="category-list">
                    {data.categories.map((cat) => (
                      <div key={cat.category} className="category-item">
                        <span className="category-name">{cat.category}</span>
                        <span className="category-count">{cat.count}</span>
                      </div>
                    ))}
                  </div>
                </section>
              )}

              {/* Recent Notifications */}
              <section className="dashboard-card">
                <div className="card-header">
                  <h2>Recent Notifications</h2>
                  <Link to="/notifications" className="card-action-link">
                    View All
                  </Link>
                </div>
                {data.recent_notifications.length === 0 ? (
                  <div className="empty-state">
                    <span className="material-symbols-outlined">notifications</span>
                    <p>No recent notifications</p>
                  </div>
                ) : (
                  <div className="notification-list">
                    {data.recent_notifications.map((notif) => (
                      <div key={notif.id} className={`notification-item ${notif.is_read ? 'read' : 'unread'}`}>
                        <h4>{notif.title}</h4>
                        <p>{notif.message}</p>
                        <p className="notif-time">
                          {formatDistanceToNow(parseISO(notif.created_at), { addSuffix: true })}
                        </p>
                      </div>
                    ))}
                  </div>
                )}
              </section>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
