type Feature = {
  title: string;
  description: string;
  icon: string;
  badgeTitle?: string;
  badgeDescription?: string;
  badgeIcon?: string;
  detailItems?: string[];
};

const features: Feature[] = [
  {
    title: 'Zero-Knowledge Encryption',
    description:
      'Your documents are encrypted before they ever leave your device. We cannot read your files, meaning your legacy is mathematically secured against unauthorized access.',
    icon: 'lock',
    badgeTitle: 'AES-256 Bit Security',
    badgeDescription: 'Enterprise-grade protection',
    badgeIcon: 'enhanced_encryption',
  },
  {
    title: 'Structured Clarity',
    description:
      'Abandon chaotic folder structures. VaultPass uses intelligent metadata and predefined semantic categories to keep your life organized.',
    icon: 'account_tree',
    detailItems: ['Medical Directives', 'Financial Records'],
  },
];

export function FeaturesSection() {
  return (
    <section className="features-section" id="features">
      <div id="security" className="section-anchor" />
      <div className="landing-container">
        <div className="section-header reveal">
          <h2>Architecture of Trust</h2>
          <p>
            Every feature is designed with a singular focus: protecting what matters most while ensuring seamless access when it's needed.
          </p>
        </div>

        <div className="features-grid">
          <article className="feature-card reveal stagger-1 highlight-card">
            <div className="feature-icon-shell">
              <span className="material-symbols-outlined feature-icon">{features[0].icon}</span>
            </div>
            <h3>{features[0].title}</h3>
            <p>{features[0].description}</p>
            <div className="feature-summary-card">
              <div className="feature-summary-copy">
                <span className="material-symbols-outlined summary-icon">{features[0].badgeIcon}</span>
                <div>
                  <p>{features[0].badgeTitle}</p>
                  <p>{features[0].badgeDescription}</p>
                </div>
              </div>
              <span className="status-dot" aria-hidden="true" />
            </div>
          </article>

          <article className="feature-card reveal stagger-2">
            <div className="feature-icon-shell muted">
              <span className="material-symbols-outlined feature-icon">{features[1].icon}</span>
            </div>
            <h3>{features[1].title}</h3>
            <p>{features[1].description}</p>
            <div className="feature-badges">
              {features[1].detailItems?.map((item) => (
                <div key={item} className="detail-badge">
                  <span className="material-symbols-outlined detail-icon">health_and_safety</span>
                  <span>{item}</span>
                </div>
              ))}
            </div>
          </article>

          <article className="feature-large-card reveal stagger-3">
            <div className="feature-hero-overlay" aria-hidden="true" />
            <div className="feature-large-copy">
              <div className="feature-icon-shell light">
                <span className="material-symbols-outlined feature-icon">vpn_key</span>
              </div>
              <h3>Granular Delegation</h3>
              <p>
                Grant specific individuals access to specific documents. Set time-delays, require multi-party consensus for sensitive files,
                and revoke access instantly. Complete control over who sees what, and when.
              </p>
            </div>
            <div className="access-card">
              <div className="access-row">
                <span>Trustee Access Request</span>
                <span className="status-pill">Pending</span>
              </div>
              <div className="access-profile">
                <div className="profile-avatar">
                  <span className="material-symbols-outlined">person</span>
                </div>
                <div>
                  <p>Sarah Jenkins</p>
                  <p>Attorney</p>
                </div>
              </div>
              <button className="button button-primary access-button" type="button">
                Approve Access
              </button>
            </div>
          </article>
        </div>
      </div>
    </section>
  );
}
