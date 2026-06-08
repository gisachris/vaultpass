import { Link } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { toast } from 'sonner';

export function LandingHeader() {
  const { user, logout } = useAuth();

  const handleLogout = () => {
    logout();
    toast.success('Signed out successfully.');
  };

  return (
    <header className="landing-header">
      <div className="landing-container">
        <div className="brand-row">
          <span className="material-symbols-outlined brand-icon" aria-hidden="true">shield_lock</span>
          <span className="brand-title">VaultPass</span>
        </div>

        <nav className="landing-nav" aria-label="Primary navigation">
          <a href="#features">Features</a>
          <a href="#workflow">How it Works</a>
          <a href="#security">Security</a>
        </nav>

        <div className="header-actions">
          {user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <span className="user-greeting" style={{ color: '#1b2e3b', fontSize: '0.9rem' }}>
                Hello, <strong style={{ color: '#1b2e3b' }}>{user.full_name}</strong>
              </span>
              <button
                className="button button-secondary"
                onClick={handleLogout}
                style={{
                  background: 'rgba(255, 255, 255, 0.05)',
                  border: '1px solid rgba(255, 255, 255, 0.1)',
                  color: '#1b2e3b',
                  padding: '0.5rem 1rem',
                  borderRadius: '6px',
                  cursor: 'pointer',
                  fontSize: '0.85rem',
                  transition: 'all 0.2s'
                }}
              >
                Sign Out
              </button>
            </div>
          ) : (
            <>
              <Link className="text-link" to="/login">
                Log In
              </Link>
              <Link className="button button-primary no-underline" to="/signup">
                Get Started
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
