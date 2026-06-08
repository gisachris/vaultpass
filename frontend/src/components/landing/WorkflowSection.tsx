const workflowSteps = [
  {
    icon: 'upload_file',
    title: '1. Upload & Encrypt',
    description:
      'Securely scan or upload your essential documents. They are encrypted instantly on your device before being stored in your private vault.',
  },
  {
    icon: 'category',
    title: '2. Organize by Intent',
    description:
      'Categorize files not just by type, but by purpose. Tag documents for executors, medical proxies, or family members.',
  },
  {
    icon: 'handshake',
    title: '3. Share with Trust',
    description:
      'Assign delegates to specific categories. They receive secure access links, verified through multi-factor authentication when required.',
  },
];

export function WorkflowSection() {
  return (
    <section className="workflow-section" id="workflow">
      <div className="landing-container">
        <div className="section-header reveal">
          <h2>A Quiet, Intentional Workflow</h2>
          <p>
            Securing your legacy shouldn't feel like a chore. Our process is designed to be deliberate, guiding you through the steps without anxiety.
          </p>
        </div>

        <div className="workflow-grid">
          {workflowSteps.map((step, index) => (
            <div key={step.title} className={`workflow-step reveal stagger-${index + 1}`}>
              <div className="workflow-icon-shell">
                <span className="material-symbols-outlined">{step.icon}</span>
              </div>
              <h3>{step.title}</h3>
              <p>{step.description}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}
