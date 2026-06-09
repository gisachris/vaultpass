import { Link, useLocation } from 'react-router-dom';
import './AppSidebar.css';

interface AppSidebarProps {
  /** extra slot rendered at top, e.g. Upload button */
  cta?: React.ReactNode;
}

const NAV_ITEMS = [
  { to: '/', label: 'Dashboard', icon: 'dashboard' },
  { to: '/documents', label: 'Documents', icon: 'description' },
  { to: '/trusted-contacts', label: 'Trusted Contacts', icon: 'group' },
  { to: '/shared-access', label: 'Shared Access', icon: 'share' },
  { to: '/received-documents', label: 'Received Documents', icon: 'inbox' },
  { to: '/notifications', label: 'Notifications', icon: 'notifications' },
  { to: '/settings', label: 'Settings', icon: 'settings' },
];

export function AppSidebar({ cta }: AppSidebarProps) {
  const location = useLocation();

  const isActive = (to: string) => {
    if (to === '/') return location.pathname === '/' || location.pathname === '/dashboard';
    return location.pathname === to;
  };

  return (
    <nav className="app-sidebar">
      <div className="app-sidebar__logo">
        <span className="app-sidebar__logo-brand">VaultPass</span>
        <span className="app-sidebar__logo-sub">Secure Document Vault</span>
      </div>

      {cta && <div className="app-sidebar__cta">{cta}</div>}

      <div className="app-sidebar__links">
        {NAV_ITEMS.map(({ to, label, icon }) => (
          <Link
            key={to}
            to={to}
            className={`app-sidebar__link ${isActive(to) ? 'app-sidebar__link--active' : ''}`}
          >
            <span className="material-symbols-outlined">{icon}</span>
            <span>{label}</span>
            {label === 'Received Documents' && (
              <span className="app-sidebar__badge-new">New</span>
            )}
          </Link>
        ))}
      </div>
    </nav>
  );
}
