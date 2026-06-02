import { useState } from 'react';
import './Dashboard.css';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:3000';

interface Document {
  id: string;
  name: string;
  category: string;
  status: 'secure' | 'review_needed';
  size: string;
  icon: string;
  iconBg: string;
}

interface Contact {
  id: string;
  name: string;
  role: string;
  avatar?: string;
  initials?: string;
}

interface ActivityItem {
  id: string;
  actor: string;
  action: string;
  details?: string;
  timestamp: string;
  type: 'upload' | 'view' | 'system';
}

const mockDocuments: Document[] = [
  {
    id: '1',
    name: '2023_Tax_Return_Final.pdf',
    category: 'Financial',
    status: 'secure',
    size: '2.4 MB',
    icon: 'picture_as_pdf',
    iconBg: 'error-container',
  },
  {
    id: '2',
    name: 'Estate_Planning_Will_v2.docx',
    category: 'Legal',
    status: 'review_needed',
    size: '1.1 MB',
    icon: 'description',
    iconBg: 'primary-fixed',
  },
  {
    id: '3',
    name: 'Passports_Scans_Family.jpg',
    category: 'Identification',
    status: 'secure',
    size: '4.5 MB',
    icon: 'image',
    iconBg: 'surface-container',
  },
];

const mockContacts: Contact[] = [
  {
    id: '1',
    name: 'Michael Chen',
    role: 'Financial Advisor',
    avatar: 'https://lh3.googleusercontent.com/aida-public/AB6AXuAz9Ub0x9DLgELDWQqQ9lOtsKJTyjqX4N9AyiN51BWjgbrvG1P4gXY_H2xKqY7mLMqGuEXIownVbU1yqFRglUZSOqSCCqN05g56uhVlpIEdQbyxvmc8B7UlZtIGVr-9WqLrXK3zHreIA9QVEj2wuM8YJsy0NAxuT2WgupsErq2IcAE0jGG7wnDqspbuuIIOU_A9jrQ3BGnfCptbRKF5_XHp3Z1NsDWsxpPoh5fa_IKq-MtqY54QP5OkZoSea88uduFGIpdzKt3TY4TD',
  },
  {
    id: '2',
    name: 'Elena Jenkins',
    role: 'Spouse (Full Access)',
    initials: 'EJ',
  },
];

const mockActivity: ActivityItem[] = [
  {
    id: '1',
    actor: 'You',
    action: 'uploaded a new document.',
    details: '2023_Tax_Return_Final.pdf',
    timestamp: '2 HOURS AGO',
    type: 'upload',
  },
  {
    id: '2',
    actor: 'Michael Chen',
    action: 'viewed Estate Planning file.',
    timestamp: 'YESTERDAY',
    type: 'view',
  },
  {
    id: '3',
    actor: '',
    action: 'System security scan completed.',
    timestamp: 'OCT 24, 2023',
    type: 'system',
  },
];

export function DashboardPage() {
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleQuickAction = (action: string) => {
    console.log(`Quick action: ${action}`);
    // Navigate to respective page or open modal
  };

  const handleDocumentClick = (docId: string) => {
    console.log(`Viewing document: ${docId}`);
    // Open document viewer or navigate
  };

  const handleContactAction = (contactId: string, action: string) => {
    console.log(`Contact ${contactId} action: ${action}`);
    // Handle contact actions (edit, remove, etc.)
  };

  const handleNavigation = (path: string) => {
    console.log(`Navigating to: ${path}`);
    // Use React Router navigation here
  };

  return (
    <div className="dashboard-shell">
      {/* Sidebar Navigation */}
      <nav className={`dashboard-sidebar ${isSidebarOpen ? 'open' : ''}`}>
        {/* Brand Header */}
        <div className="sidebar-brand">
          <div className="brand-icon">V</div>
          <div>
            <h1 className="brand-name">VaultPass</h1>
            <p className="brand-tagline">Secure Document Vault</p>
          </div>
        </div>

        {/* Navigation Links */}
        <div className="sidebar-nav">
          <a className="nav-item active" href="#dashboard">
            <span className="material-symbols-outlined nav-icon">dashboard</span>
            <span className="nav-label">Dashboard</span>
          </a>
          <a className="nav-item" href="#documents">
            <span className="material-symbols-outlined nav-icon">description</span>
            <span className="nav-label">Documents</span>
          </a>
          <a className="nav-item" href="#contacts">
            <span className="material-symbols-outlined nav-icon">group</span>
            <span className="nav-label">Trusted Contacts</span>
          </a>
          <a className="nav-item" href="#shared">
            <span className="material-symbols-outlined nav-icon">share</span>
            <span className="nav-label">Shared Access</span>
          </a>
          <a className="nav-item" href="#notifications">
            <span className="material-symbols-outlined nav-icon">notifications</span>
            <span className="nav-label">Notifications</span>
          </a>
          <a className="nav-item" href="#settings">
            <span className="material-symbols-outlined nav-icon">settings</span>
            <span className="nav-label">Settings</span>
          </a>
        </div>

        {/* CTA Button */}
        <div className="sidebar-cta">
          <button
            className="upload-button"
            onClick={() => handleQuickAction('upload')}
            type="button"
          >
            <span className="material-symbols-outlined">upload</span>
            <span className="cta-label">Upload Document</span>
          </button>
        </div>
      </nav>

      {/* Main Content Wrapper */}
      <div className="dashboard-main-wrapper">
        {/* Top App Bar */}
        <header className="dashboard-header">
          <button
            className="mobile-menu-toggle"
            onClick={() => setIsSidebarOpen(!isSidebarOpen)}
            type="button"
          >
            <span className="material-symbols-outlined">menu</span>
          </button>

          <div className="mobile-brand">VaultPass</div>

          <div className="header-spacer" />

          <div className="header-actions">
            <button className="header-action-btn" type="button">
              <span className="material-symbols-outlined">help_outline</span>
            </button>
            <button className="header-action-btn" type="button">
              <span className="material-symbols-outlined">account_circle</span>
            </button>
          </div>
        </header>

        {/* Main Content */}
        <main className="dashboard-content">
          {/* Welcome Header */}
          <div className="welcome-section">
            <h2 className="welcome-title">Good evening, Sarah.</h2>
            <p className="welcome-subtitle">Your vault is secure and organized.</p>
          </div>

          {/* Bento Grid */}
          <div className="dashboard-grid">
            {/* Quick Actions */}
            <div className="grid-quick-actions">
              {/* Action Card 1 */}
              <div
                className="action-card"
                onClick={() => handleQuickAction('upload')}
                role="button"
                tabIndex={0}
              >
                <div className="action-card-decorative" />
                <div className="action-card-content">
                  <div className="action-icon upload-icon">
                    <span className="material-symbols-outlined">upload_file</span>
                  </div>
                  <div>
                    <h3 className="action-title">Upload Document</h3>
                    <p className="action-description">Securely store a new file in your vault.</p>
                  </div>
                </div>
                <span className="material-symbols-outlined action-arrow">arrow_forward</span>
              </div>

              {/* Action Card 2 */}
              <div
                className="action-card"
                onClick={() => handleQuickAction('add-contact')}
                role="button"
                tabIndex={0}
              >
                <div className="action-card-decorative" />
                <div className="action-card-content">
                  <div className="action-icon contact-icon">
                    <span className="material-symbols-outlined">person_add</span>
                  </div>
                  <div>
                    <h3 className="action-title">Add Trusted Contact</h3>
                    <p className="action-description">Grant selective access to a family member or advisor.</p>
                  </div>
                </div>
                <span className="material-symbols-outlined action-arrow">arrow_forward</span>
              </div>
            </div>

            {/* Recent Documents Panel */}
            <div className="documents-panel">
              <div className="panel-header">
                <h3 className="panel-title">Recent Documents</h3>
                <button className="view-all-btn" type="button">
                  View All
                </button>
              </div>

              <div className="documents-table">
                {/* Table Header */}
                <div className="table-header">
                  <div className="th-name">Name</div>
                  <div className="th-category">Category</div>
                  <div className="th-status">Status</div>
                  <div className="th-size">Size</div>
                </div>

                {/* Table Body */}
                <div className="table-body">
                  {mockDocuments.map((doc) => (
                    <div
                      key={doc.id}
                      className="table-row"
                      onClick={() => handleDocumentClick(doc.id)}
                      role="button"
                      tabIndex={0}
                    >
                      <div className="td-name">
                        <div className={`doc-icon ${doc.iconBg}`}>
                          <span className="material-symbols-outlined">{doc.icon}</span>
                        </div>
                        <div>
                          <p className="doc-name">{doc.name}</p>
                          <p className="doc-category-mobile">{doc.category}</p>
                        </div>
                      </div>
                      <div className="td-category">
                        <span className="category-badge">{doc.category}</span>
                      </div>
                      <div className="td-status">
                        <div className="status-indicator">
                          <div className={`status-dot ${doc.status}`} />
                          <span className="status-text">
                            {doc.status === 'secure' ? 'Secure' : 'Review Needed'}
                          </span>
                        </div>
                      </div>
                      <div className="td-size">{doc.size}</div>
                    </div>
                  ))}
                </div>
              </div>
            </div>

            {/* Right Column */}
            <div className="right-column">
              {/* Trusted Contacts Panel */}
              <div className="contacts-panel">
                <div className="panel-header">
                  <h3 className="panel-title">Trusted Contacts</h3>
                  <button className="add-contact-btn" type="button">
                    <span className="material-symbols-outlined">add</span>
                  </button>
                </div>

                <div className="contacts-list">
                  {mockContacts.map((contact) => (
                    <div key={contact.id} className="contact-item">
                      <div className="contact-left">
                        {contact.avatar ? (
                          <img alt={contact.name} className="contact-avatar" src={contact.avatar} />
                        ) : (
                          <div className="contact-avatar-initials">{contact.initials}</div>
                        )}
                        <div>
                          <p className="contact-name">{contact.name}</p>
                          <p className="contact-role">{contact.role}</p>
                        </div>
                      </div>
                      <button
                        className="contact-menu-btn"
                        onClick={() => handleContactAction(contact.id, 'menu')}
                        type="button"
                      >
                        <span className="material-symbols-outlined">more_vert</span>
                      </button>
                    </div>
                  ))}
                </div>
              </div>

              {/* Recent Activity Panel */}
              <div className="activity-panel">
                <div className="panel-header">
                  <h3 className="panel-title">Recent Activity</h3>
                </div>

                <div className="activity-timeline">
                  {mockActivity.map((item) => (
                    <div key={item.id} className="activity-item">
                      <div className={`timeline-dot ${item.type}`} />
                      <div className="activity-content">
                        <p className="activity-text">
                          {item.actor && <span className="activity-actor">{item.actor}</span>}
                          {' '}
                          {item.action}
                        </p>
                        {item.details && <p className="activity-details">{item.details}</p>}
                        <span className="activity-timestamp">{item.timestamp}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </main>
      </div>
    </div>
  );
}
