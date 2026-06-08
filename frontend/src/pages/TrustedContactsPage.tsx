import { ChangeEvent, FormEvent, useMemo, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { toast } from 'sonner';
import { createTrustedContact } from '../services/trustedContactsService';
import { useTrustedContacts } from '../hooks/useTrustedContacts';
import { TrustedContactCreatePayload } from '../types/trustedContact';
import './TrustedContactsPage.css';

function formatDate(dateString: string) {
  return new Date(dateString).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function getInitials(name: string) {
  return name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((segment) => segment[0].toUpperCase())
    .join('');
}

export function TrustedContactsPage() {
  const location = useLocation();
  const {
    contacts,
    page,
    total,
    searchInput,
    loading,
    error,
    pageCount,
    setPage,
    setSearchInput,
    refresh,
  } = useTrustedContacts();

  const [inviteOpen, setInviteOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [invitationError, setInvitationError] = useState('');
  const [form, setForm] = useState<TrustedContactCreatePayload>({
    full_name: '',
    email: '',
    phone_number: '',
    relationship: '',
    notes: '',
  });

  const recentCount = useMemo(() => {
    const now = Date.now();
    const thirtyDays = 1000 * 60 * 60 * 24 * 30;
    return contacts.filter((contact) => now - new Date(contact.created_at).getTime() <= thirtyDays).length;
  }, [contacts]);

  const handleInputChange = (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    setForm((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleInviteSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setInvitationError('');

    if (!form.full_name.trim() || !form.email.trim() || !form.relationship.trim()) {
      setInvitationError('Full name, email, and relationship are required.');
      return;
    }

    setSubmitting(true);

    try {
      await createTrustedContact({
        full_name: form.full_name.trim(),
        email: form.email.trim(),
        phone_number: form.phone_number ? form.phone_number.trim() : undefined,
        relationship: form.relationship.trim(),
        notes: form.notes ? form.notes.trim() : undefined,
      });
      toast.success('Trusted contact added successfully.');
      setInviteOpen(false);
      setForm({ full_name: '', email: '', phone_number: '', relationship: '', notes: '' });
      await refresh();
    } catch (err: any) {
      setInvitationError(err.response?.data?.detail || 'Unable to add trusted contact.');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="trusted-contacts-page">
      <aside className="trusted-sidebar">
        <div className="trusted-sidebar-branding">
          <h1>VaultPass</h1>
          <p>Secure Document Vault</p>
        </div>

        <nav className="trusted-sidebar-nav">
          <Link to="/dashboard" className={`trusted-sidebar-link ${location.pathname === '/dashboard' ? 'trusted-sidebar-link--active' : ''}`}>
            <span className="material-symbols-outlined">dashboard</span>
            Dashboard
          </Link>
          <Link to="/documents" className={`trusted-sidebar-link ${location.pathname === '/documents' ? 'trusted-sidebar-link--active' : ''}`}>
            <span className="material-symbols-outlined">description</span>
            Documents
          </Link>
          <Link to="/trusted-contacts" className={`trusted-sidebar-link ${location.pathname === '/trusted-contacts' ? 'trusted-sidebar-link--active' : ''}`}>
            <span className="material-symbols-outlined">group</span>
            Trusted Contacts
          </Link>
          <button type="button" className="trusted-sidebar-link trusted-sidebar-link--primary">
            <span className="material-symbols-outlined">share</span>
            Shared Access
          </button>
          <Link
            to="/notifications"
            className={`trusted-sidebar-link ${location.pathname === '/notifications' ? 'trusted-sidebar-link--active' : ''}`}
          >
            <span className="material-symbols-outlined">notifications</span>
            Notifications
          </Link>
          <button type="button" className="trusted-sidebar-link trusted-sidebar-link--disabled">
            <span className="material-symbols-outlined">settings</span>
            Settings
          </button>
        </nav>

        <div className="trusted-sidebar-footer">
          <button type="button" className="trusted-sidebar-button" onClick={() => setInviteOpen(true)}>
            <span className="material-symbols-outlined">upload</span>
            Upload Document
          </button>
        </div>
      </aside>

      <div className="trusted-main-content">
        <header className="trusted-topbar">
          <div className="trusted-search-wrapper">
            <span className="material-symbols-outlined">search</span>
            <input
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Search contacts..."
              aria-label="Search contacts"
            />
          </div>
          <div className="trusted-topbar-actions">
            <button type="button" className="icon-button" aria-label="Help">
              <span className="material-symbols-outlined">help_outline</span>
            </button>
            <div className="trusted-avatar">
              <img
                src="https://images.unsplash.com/photo-1502685104226-ee32379fefbe?auto=format&fit=crop&w=256&q=80"
                alt="User profile"
              />
            </div>
          </div>
        </header>

        <main className="trusted-canvas">
          <section className="trusted-hero">
            <div>
              <h1>Trusted Contacts</h1>
              <p>Manage the people you trust with your most important records.</p>
            </div>
            <button type="button" className="button button-primary" onClick={() => setInviteOpen(true)}>
              <span className="material-symbols-outlined">person_add</span>
              Invite Contact
            </button>
          </section>

          <div className="trusted-grid">
            <section className="trusted-summary-card">
              <div className="trusted-summary-header">
                <h2>Contact activity</h2>
                <span>{contacts.length} Contacts</span>
              </div>
              <div className="trusted-summary-copy">
                <p>
                  Keep track of your trusted circle and quickly add new people who can access your vault when needed.
                </p>
              </div>
              <div className="trusted-summary-stats">
                <div>
                  <span>{contacts.length}</span>
                  <p>Total contacts</p>
                </div>
                <div>
                  <span>{recentCount}</span>
                  <p>Added in last 30 days</p>
                </div>
              </div>
            </section>

            <section className="trusted-contacts-list">
              {loading ? (
                <div className="trusted-empty-state">
                  <p>Loading trusted contacts…</p>
                </div>
              ) : error ? (
                <div className="trusted-empty-state trusted-empty-state--error">
                  <p>{error}</p>
                </div>
              ) : contacts.length === 0 ? (
                <div className="trusted-empty-state">
                  <h2>No trusted contacts yet</h2>
                  <p>Invite a contact to start building your trusted network.</p>
                </div>
              ) : (
                <div className="trusted-contact-cards">
                  {contacts.map((contact) => (
                    <article className="trusted-contact-card" key={contact.id}>
                      <div className="trusted-contact-meta">
                        <div className="trusted-contact-avatar">{getInitials(contact.full_name)}</div>
                        <div>
                          <div className="trusted-contact-name-row">
                            <h3>{contact.full_name}</h3>
                            <span className="trusted-contact-badge">{contact.relationship}</span>
                          </div>
                          <p>{contact.email}</p>
                          <p>{contact.phone_number || 'No phone number'}</p>
                        </div>
                      </div>
                      <div className="trusted-contact-footer">
                        <div>
                          <p className="trusted-contact-stat-value">
                            {formatDate(contact.created_at)}
                          </p>
                          <p className="trusted-contact-stat-label">Added</p>
                        </div>
                      </div>
                    </article>
                  ))}
                </div>
              )}

              {!loading && contacts.length > 0 && (
                <div className="trusted-pagination">
                  <button type="button" className="button button-secondary" disabled={page === 1} onClick={() => setPage(page - 1)}>
                    Previous
                  </button>
                  <button type="button" className="button button-secondary" disabled={page >= pageCount} onClick={() => setPage(page + 1)}>
                    Next
                  </button>
                </div>
              )}
            </section>
          </div>
        </main>
      </div>

      {inviteOpen && (
        <div className="documents-modal-overlay" onClick={() => setInviteOpen(false)}>
          <div className="documents-modal-window" onClick={(event) => event.stopPropagation()}>
            <div className="documents-modal-header">
              <div>
                <h2>Invite trusted contact</h2>
                <p>Send secure access to a trusted person and keep your vault protected.</p>
              </div>
              <button type="button" className="documents-modal-close" onClick={() => setInviteOpen(false)} aria-label="Close invite modal">
                ×
              </button>
            </div>

            <form className="documents-modal-body" onSubmit={handleInviteSubmit}>
              <div className="documents-modal-row documents-modal-row--full">
                <label htmlFor="trusted-full_name">Full name</label>
                <input
                  id="trusted-full_name"
                  name="full_name"
                  value={form.full_name}
                  onChange={handleInputChange}
                  placeholder="Example: Jane Doe"
                  required
                />
              </div>

              <div className="documents-modal-row documents-modal-row--full">
                <label htmlFor="trusted-email">Email address</label>
                <input
                  id="trusted-email"
                  name="email"
                  type="email"
                  value={form.email}
                  onChange={handleInputChange}
                  placeholder="name@company.com"
                  required
                />
              </div>

              <div className="documents-modal-row documents-modal-row--full">
                <label htmlFor="trusted-relationship">Relationship</label>
                <input
                  id="trusted-relationship"
                  name="relationship"
                  value={form.relationship}
                  onChange={handleInputChange}
                  placeholder="Spouse, Lawyer, Friend"
                  required
                />
              </div>

              <div className="documents-modal-row documents-modal-row--full">
                <label htmlFor="trusted-phone_number">Phone number</label>
                <input
                  id="trusted-phone_number"
                  name="phone_number"
                  value={form.phone_number}
                  onChange={handleInputChange}
                  placeholder="Optional"
                />
              </div>

              <div className="documents-modal-row documents-modal-row--full">
                <label htmlFor="trusted-notes">Notes</label>
                <textarea
                  id="trusted-notes"
                  name="notes"
                  rows={4}
                  value={form.notes}
                  onChange={handleInputChange}
                  placeholder="Optional details for this contact"
                />
              </div>

              {invitationError && <div className="documents-modal-error">{invitationError}</div>}

              <div className="documents-modal-actions">
                <button type="button" className="button button-secondary" onClick={() => setInviteOpen(false)} disabled={submitting}>
                  Cancel
                </button>
                <button type="submit" className="button button-primary" disabled={submitting}>
                  {submitting ? 'Inviting…' : 'Invite contact'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
