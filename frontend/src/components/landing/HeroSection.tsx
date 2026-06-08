export function HeroSection() {
  return (
    <section className="hero-section" id="demo">
      <div className="landing-container hero-grid">
        <div className="hero-copy reveal stagger-1">
          <p className="eyebrow">Secure Your Legacy.</p>
          <h1>
            Secure Your Legacy.
            <br />
            <span>Share With Those You Trust.</span>
          </h1>
          <p className="hero-text">
            A meticulously designed, quiet space to organize, encrypt, and delegate access to your most
            critical life documents. Engineered for confidence, built for peace of mind.
          </p>
          <div className="hero-actions">
            <a className="button button-primary hero-button" href="/signup">
              Create Your Vault
            </a>
            <a className="button button-secondary hero-button" href="#demo">
              <span className="material-symbols-outlined icon">play_circle</span>
              View Walkthrough
            </a>
          </div>
        </div>

        <div className="hero-visual reveal stagger-2" aria-hidden="true">
          <div className="hero-card">
            <div className="hero-card-header">
              <div className="avatar-circle">
                <span className="material-symbols-outlined">folder_shared</span>
              </div>
              <div>
                <h3>Estate Planning Trust</h3>
                <p>3 Documents • Shared with 2 Delegates</p>
              </div>
            </div>
            <div className="hero-card-list">
              <div className="hero-item">
                <div className="hero-item-copy">
                  <span className="material-symbols-outlined">description</span>
                  <span>Last_Will_Testament.pdf</span>
                </div>
                <span className="material-symbols-outlined status-icon">verified</span>
              </div>
              <div className="hero-item">
                <div className="hero-item-copy">
                  <span className="material-symbols-outlined">shield</span>
                  <span>Insurance_Policies.pdf</span>
                </div>
                <span className="material-symbols-outlined status-icon">verified</span>
              </div>
            </div>
          </div>
          <div className="hero-glow" />
        </div>
      </div>
    </section>
  );
}
