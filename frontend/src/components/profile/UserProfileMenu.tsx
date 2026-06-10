import { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import './UserProfileMenu.css';

function getInitials(fullName?: string | null): string {
  if (!fullName) return '';
  const parts = fullName.trim().split(/\s+/);
  if (parts.length === 1) return parts[0][0].toUpperCase();
  return (parts[0][0] + parts[parts.length - 1][0]).toUpperCase();
}

interface UserProfileMenuProps {
  variant?: 'topbar' | 'sidebar';
}

export function UserProfileMenu({ variant = 'topbar' }: UserProfileMenuProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [open, setOpen] = useState(false);
  const menuRef = useRef<HTMLDivElement>(null);

  // Close on outside click
  useEffect(() => {
    function handleClick(e: MouseEvent) {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setOpen(false);
      }
    }
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  const handleLogout = () => {
    logout();
    setOpen(false);
    navigate('/login', { replace: true });
  };

  const handleSettings = () => {
    setOpen(false);
    navigate('/settings');
  };

  const initials = getInitials(user?.full_name);

  return (
    <div className={`upm-wrapper upm-wrapper--${variant}`} ref={menuRef}>
      {/* Avatar trigger */}
      <button
        type="button"
        className="upm-avatar-btn"
        onClick={() => setOpen((o) => !o)}
        aria-label="Open profile menu"
        aria-expanded={open}
      >
        {user?.profile_image ? (
          <img src={user.profile_image} alt="Profile" className="upm-avatar-img" />
        ) : initials ? (
          <span className="upm-avatar-initials">{initials}</span>
        ) : (
          <span className="upm-avatar-icon material-symbols-outlined">person</span>
        )}
      </button>

      {/* Dropdown */}
      {open && (
        <div className={`upm-dropdown upm-dropdown--${variant}`} role="menu">
          {/* Profile info card */}
          <div className="upm-profile-card">
            <div className="upm-profile-avatar">
              {user?.profile_image ? (
                <img src={user.profile_image} alt="Profile" />
              ) : initials ? (
                <span className="upm-profile-initials">{initials}</span>
              ) : (
                <span className="material-symbols-outlined upm-profile-icon">person</span>
              )}
            </div>
            <div className="upm-profile-info">
              <p className="upm-profile-name">{user?.full_name || 'User'}</p>
              <p className="upm-profile-email">{user?.email}</p>
              <span className="upm-profile-role">{user?.role || 'Member'}</span>
            </div>
          </div>

          <div className="upm-divider" />

          {/* Actions */}
          <button
            type="button"
            className="upm-menu-item"
            onClick={handleSettings}
            role="menuitem"
          >
            <span className="material-symbols-outlined">settings</span>
            Settings
          </button>

          <div className="upm-divider" />

          <button
            type="button"
            className="upm-menu-item upm-menu-item--danger"
            onClick={handleLogout}
            role="menuitem"
          >
            <span className="material-symbols-outlined">logout</span>
            Sign out
          </button>
        </div>
      )}
    </div>
  );
}
