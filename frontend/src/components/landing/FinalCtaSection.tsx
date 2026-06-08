export function FinalCtaSection() {
  return (
    <section className="final-cta-section">
      <div className="landing-container final-cta-copy reveal">
        <span className="material-symbols-outlined final-cta-icon" aria-hidden="true">assured_workload</span>
        <h2>Preparedness is a Virtue.</h2>
        <p>
          Take the first step towards ensuring your legacy is organized, protected, and accessible to those who matter most.
          Begin building your Vault today.
        </p>
        <a className="button button-primary final-cta-button" href="/signup">
          Create Your Account
          <span className="material-symbols-outlined arrow-icon" aria-hidden="true">
            arrow_forward
          </span>
        </a>
        <p className="final-cta-note">No credit card required for the foundational tier.</p>
      </div>
    </section>
  );
}
