export function LandingHeader() {
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
          <a className="text-link" href="/login">
            Log In
          </a>
          <a className="button button-primary no-underline" href="/signup">
            Get Started
          </a>
        </div>
      </div>
    </header>
  );
}
