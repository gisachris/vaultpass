export function LandingFooter() {
  return (
    <footer className="landing-footer">
      <div className="landing-container footer-grid">
        <div className="brand-row footer-brand">
          <span className="material-symbols-outlined brand-icon" aria-hidden="true">shield_lock</span>
          <span className="brand-title">VaultPass</span>
        </div>
        <div className="footer-links">
          <a href="#">Privacy Policy</a>
          <a href="#">Terms of Service</a>
          <a href="#">Security Architecture</a>
          <a href="#">Contact</a>
        </div>
        <p className="footer-copy">© 2024 VaultPass Systems. All rights reserved.</p>
      </div>
    </footer>
  );
}
