import { ChangeEvent, FormEvent, useMemo, useState, useEffect } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { toast } from 'sonner';
import { createTrustedContact, deleteTrustedContact, updateTrustedContact } from '../services/trustedContactsService';
import { sendTrustedContactNotificationEmail } from '../services/trustedContactEmailService';
import { useTrustedContacts } from '../hooks/useTrustedContacts';
import { useAuth } from '../context/AuthContext';
import { TrustedContactCreatePayload, TrustedContactModel } from '../types/trustedContact';
import { api } from '../lib/api';
import { AppSidebar } from '../components/ui/AppSidebar';
import { UserProfileMenu } from '../components/profile/UserProfileMenu';
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
  const { user } = useAuth();
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
    email: '',
    phone_number: '',
    relationship: '',
    notes: '',
  });

  const [editOpen, setEditOpen] = useState(false);
  const [selectedContact, setSelectedContact] = useState<TrustedContactModel | null>(null);
  const [activeMenuId, setActiveMenuId] = useState<string | null>(null);
  const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState('');
  const [pendingDelete, setPendingDelete] = useState<TrustedContactModel | null>(null);
  const [showInviteConfirmation, setShowInviteConfirmation] = useState(false);
  const [editForm, setEditForm] = useState<TrustedContactCreatePayload & { full_name: string }>({
    full_name: '',
    email: '',
    phone_number: '',
    relationship: '',
    notes: '',
  });

  useEffect(() => {
    if (!activeMenuId) {
      return;
    }

    const handleClickOutside = () => {
      setActiveMenuId(null);
    };

    window.addEventListener('mousedown', handleClickOutside);
    return () => window.removeEventListener('mousedown', handleClickOutside);
  }, [activeMenuId]);

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

  const createTrustedContactDirectly = async () => {
    setSubmitting(true);
    setInvitationError('');
    try {
      const result = await createTrustedContact({
        email: form.email.trim(),
        phone_number: form.phone_number ? form.phone_number.trim() : undefined,
        relationship: form.relationship.trim(),
        notes: form.notes ? form.notes.trim() : undefined,
      });
      toast.success('Trusted contact added successfully.');
      setInviteOpen(false);
      setShowInviteConfirmation(false);

      const createdContact = result.data;
      toast.promise(
        sendTrustedContactNotificationEmail({
          toEmail: createdContact.email,
          toName: createdContact.full_name,
          ownerName: user?.full_name || 'Someone',
          isRegisteredUser: Boolean(createdContact.is_registered_user),
        }),
        {
          loading: 'Sending notification email...',
          success: 'Notification email sent to your trusted contact.',
          error: 'Failed to send notification email.',
        }
      );

      setForm({ email: '', phone_number: '', relationship: '', notes: '' });
      await refresh();
    } catch (err: any) {
      setInvitationError(err.response?.data?.detail || 'Unable to add trusted contact.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleConfirmInvite = async () => {
    toast.success(`Invitation email sent to ${form.email.trim()}!`);
    await createTrustedContactDirectly();
  };

  const handleInviteSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setInvitationError('');

    if (!form.email.trim() || !form.relationship.trim()) {
      setInvitationError('Email and relationship are required.');
      return;
    }

    setSubmitting(true);

    try {
      await createTrustedContactDirectly();
    } catch (err: any) {
      setInvitationError(err.response?.data?.detail || 'Unable to add contact.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleEditClick = (contact: TrustedContactModel) => {
    setSelectedContact(contact);
    setEditForm({
      full_name: contact.full_name,
      email: contact.email,
      phone_number: contact.phone_number || '',
      relationship: contact.relationship,
      notes: contact.notes || '',
    });
    setEditOpen(true);
    setActiveMenuId(null);
  };

  const handleEditInputChange = (event: ChangeEvent<HTMLInputElement | HTMLTextAreaElement>) => {
    const { name, value } = event.target;
    setEditForm((current) => ({
      ...current,
      [name]: value,
    }));
  };

  const handleEditSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedContact) return;

    setSubmitting(true);
    try {
      await updateTrustedContact(selectedContact.id, {
        full_name: editForm.full_name.trim(),
        email: editForm.email.trim(),
        phone_number: editForm.phone_number ? editForm.phone_number.trim() : undefined,
        relationship: editForm.relationship.trim(),
        notes: editForm.notes ? editForm.notes.trim() : undefined,
      });
      toast.success('Trusted contact updated successfully.');
      setEditOpen(false);
      setSelectedContact(null);
      await refresh();
    } catch (err: any) {
      toast.error(err.response?.data?.detail || 'Unable to update contact.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleDeleteClick = (contact: TrustedContactModel) => {
    setPendingDelete(contact);
    setDeleteError('');
    setConfirmDeleteOpen(true);
    setActiveMenuId(null);
  };

  const confirmDeleteContact = async () => {
    if (!pendingDelete) return;

    setDeleting(true);
    setDeleteError('');
    try {
      await deleteTrustedContact(pendingDelete.id);
      toast.success('Trusted contact deleted successfully.');
      setConfirmDeleteOpen(false);
      setPendingDelete(null);
      await refresh();
    } catch (err: any) {
      setDeleteError(err.response?.data?.detail || 'Unable to delete contact.');
    } finally {
      setDeleting(false);
    }
  };

  return (
    <div className="trusted-contacts-page">
      <AppSidebar />

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
            <UserProfileMenu variant="topbar" />
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
                      <div className="contact-card-actions">
                        <button
                          type="button"
                          className="contact-card-action-button"
                          onClick={(event) => {
                            event.stopPropagation();
                            setActiveMenuId((current) => (current === contact.id ? null : contact.id));
                          }}
                          aria-label="Contact options"
                        >
                          <span className="material-symbols-outlined">more_vert</span>
                        </button>
                        {activeMenuId === contact.id && (
                          <div className="contact-card-menu" role="menu">
                            <button type="button" onClick={() => handleEditClick(contact)}>
                              Edit details
                            </button>
                            <button type="button" onClick={() => handleDeleteClick(contact)}>
                              Delete contact
                            </button>
                          </div>
                        )}
                      </div>
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
                  {submitting ? 'Verifying…' : 'Invite contact'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {showInviteConfirmation && (
        <div className="documents-modal-overlay" onClick={() => setShowInviteConfirmation(false)}>
          <div className="documents-modal-window" onClick={(event) => event.stopPropagation()}>
            <div className="documents-modal-header">
              <div>
                <h2>User not found on platform</h2>
                <p>Send an invitation to join VaultPass.</p>
              </div>
              <button type="button" className="documents-modal-close" onClick={() => setShowInviteConfirmation(false)} aria-label="Close confirmation dialog">
                ×
              </button>
            </div>

            <div className="documents-modal-body">
              <p>
                The email <strong>{form.email}</strong> is not currently registered on VaultPass.
              </p>
              <p>
                Would you like to send an invitation email to sign up? They will receive an invitation to access your shared documents once they register.
              </p>
            </div>

            <div className="documents-modal-actions">
              <button type="button" className="button button-secondary" onClick={() => setShowInviteConfirmation(false)} disabled={submitting}>
                Cancel
              </button>
              <button type="button" className="button button-primary" onClick={handleConfirmInvite} disabled={submitting}>
                {submitting ? 'Sending…' : 'Send Invite & Add Contact'}
              </button>
            </div>
          </div>
        </div>
      )}

      {editOpen && selectedContact && (
        <div className="documents-modal-overlay" onClick={() => { setEditOpen(false); setSelectedContact(null); }}>
          <div className="documents-modal-window" onClick={(event) => event.stopPropagation()}>
            <div className="documents-modal-header">
              <div>
                <h2>Edit trusted contact</h2>
                <p>Update contact information and details.</p>
              </div>
              <button type="button" className="documents-modal-close" onClick={() => { setEditOpen(false); setSelectedContact(null); }} aria-label="Close edit dialog">
                ×
              </button>
            </div>

            <form className="documents-modal-body" onSubmit={handleEditSubmit}>
              <div className="documents-modal-row documents-modal-row--full">
                <label htmlFor="edit-trusted-full_name">Full name</label>
                <input
                  id="edit-trusted-full_name"
                  name="full_name"
                  value={editForm.full_name}
                  onChange={handleEditInputChange}
                  placeholder="Example: Jane Doe"
                  required
                />
              </div>

              <div className="documents-modal-row documents-modal-row--full">
                <label htmlFor="edit-trusted-email">Email address</label>
                <input
                  id="edit-trusted-email"
                  name="email"
                  type="email"
                  value={editForm.email}
                  onChange={handleEditInputChange}
                  placeholder="name@company.com"
                  required
                />
              </div>

              <div className="documents-modal-row documents-modal-row--full">
                <label htmlFor="edit-trusted-relationship">Relationship</label>
                <input
                  id="edit-trusted-relationship"
                  name="relationship"
                  value={editForm.relationship}
                  onChange={handleEditInputChange}
                  placeholder="Spouse, Lawyer, Friend"
                  required
                />
              </div>

              <div className="documents-modal-row documents-modal-row--full">
                <label htmlFor="edit-trusted-phone_number">Phone number</label>
                <input
                  id="edit-trusted-phone_number"
                  name="phone_number"
                  value={editForm.phone_number}
                  onChange={handleEditInputChange}
                  placeholder="Optional"
                />
              </div>

              <div className="documents-modal-row documents-modal-row--full">
                <label htmlFor="edit-trusted-notes">Notes</label>
                <textarea
                  id="edit-trusted-notes"
                  name="notes"
                  rows={4}
                  value={editForm.notes}
                  onChange={handleEditInputChange}
                  placeholder="Optional details for this contact"
                />
              </div>

              <div className="documents-modal-actions">
                <button type="button" className="button button-secondary" onClick={() => { setEditOpen(false); setSelectedContact(null); }} disabled={submitting}>
                  Cancel
                </button>
                <button type="submit" className="button button-primary" disabled={submitting}>
                  {submitting ? 'Saving…' : 'Save changes'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {confirmDeleteOpen && pendingDelete && (
        <div className="documents-modal-overlay" onClick={() => { setConfirmDeleteOpen(false); setPendingDelete(null); }}>
          <div className="documents-modal-window" onClick={(event) => event.stopPropagation()}>
            <div className="documents-modal-header">
              <div>
                <h2>Delete trusted contact</h2>
                <p>Confirm before removing this contact from your list.</p>
              </div>
              <button type="button" className="documents-modal-close" onClick={() => { setConfirmDeleteOpen(false); setPendingDelete(null); }} aria-label="Close delete confirmation dialog">
                ×
              </button>
            </div>

            <div className="documents-modal-body">
              <p>
                Are you sure you want to delete <strong>{pendingDelete.full_name}</strong>? This will also revoke any active document shares with them.
              </p>
              {deleteError && <div className="documents-modal-error">{deleteError}</div>}
            </div>

            <div className="documents-modal-actions">
              <button type="button" className="button button-secondary" onClick={() => { setConfirmDeleteOpen(false); setPendingDelete(null); }} disabled={deleting}>
                Cancel
              </button>
              <button type="button" className="button button-primary" onClick={confirmDeleteContact} disabled={deleting}>
                {deleting ? 'Deleting…' : 'Delete contact'}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
