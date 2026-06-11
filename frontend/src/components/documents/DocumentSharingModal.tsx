import { useEffect, useState, FormEvent } from 'react';
import { toast } from 'sonner';
import {
  createInternalShare,
  createDocumentShare,
  AccessLevel,
  ACCESS_LEVEL_LABELS,
  ACCESS_LEVEL_DESCRIPTIONS,
} from '../../services/documentShareService';
import { fetchTrustedContacts } from '../../services/trustedContactsService';
import { DocumentModel } from '../../types/document';
import { TrustedContactModel } from '../../types/trustedContact';
import './DocumentSharingModal.css';

interface DocumentSharingModalProps {
  open: boolean;
  document: DocumentModel | null;
  onClose: () => void;
}

type ExpiryOption = 'never' | '7days' | '30days' | 'custom';
type ExternalExpiryOption = '24hours' | '7days' | '30days' | 'custom';

function getExpiryDate(option: ExpiryOption | ExternalExpiryOption): string | undefined {
  const now = new Date();
  if (option === '24hours') {
    now.setHours(now.getHours() + 24);
    return now.toISOString();
  }
  if (option === '7days') {
    now.setDate(now.getDate() + 7);
    return now.toISOString();
  }
  if (option === '30days') {
    now.setDate(now.getDate() + 30);
    return now.toISOString();
  }
  return undefined;
}

function ContactCard({
  contact,
  selected,
  onSelect,
}: {
  contact: TrustedContactModel;
  selected: boolean;
  onSelect: () => void;
}) {
  const initials = contact.full_name
    .split(' ')
    .filter(Boolean)
    .slice(0, 2)
    .map((w) => w[0].toUpperCase())
    .join('');

  return (
    <button
      type="button"
      className={`dsm-contact-card ${selected ? 'dsm-contact-card--selected' : ''}`}
      onClick={onSelect}
      aria-pressed={selected}
    >
      <div className="dsm-contact-avatar">{initials}</div>
      <div className="dsm-contact-info">
        <p className="dsm-contact-name">{contact.full_name}</p>
        <p className="dsm-contact-email">{contact.email}</p>
        <span className="dsm-contact-rel">{contact.relationship}</span>
      </div>
      {selected && (
        <span className="dsm-contact-check material-symbols-outlined">check_circle</span>
      )}
    </button>
  );
}

export function DocumentSharingModal({ open, document, onClose }: DocumentSharingModalProps) {
  // ── Internal share state ─────────────────────────────────────────────────
  const [contacts, setContacts] = useState<TrustedContactModel[]>([]);
  const [loadingContacts, setLoadingContacts] = useState(false);
  const [selectedContactId, setSelectedContactId] = useState('');
  const [accessLevel, setAccessLevel] = useState<AccessLevel>('view');
  const [internalExpiry, setInternalExpiry] = useState<ExpiryOption>('never');
  const [internalCustomDate, setInternalCustomDate] = useState('');
  const [internalSubmitting, setInternalSubmitting] = useState(false);
  const [internalError, setInternalError] = useState('');

  // ── External link state ──────────────────────────────────────────────────
  const [externalExpiry, setExternalExpiry] = useState<ExternalExpiryOption>('7days');
  const [externalCustomDate, setExternalCustomDate] = useState('');
  const [allowDownload, setAllowDownload] = useState(true);
  const [passwordProtect, setPasswordProtect] = useState(false);
  const [password, setPassword] = useState('');
  const [externalSubmitting, setExternalSubmitting] = useState(false);
  const [externalError, setExternalError] = useState('');
  const [generatedLink, setGeneratedLink] = useState('');
  const [linkCopied, setLinkCopied] = useState(false);

  // ── Tab state ─────────────────────────────────────────────────────────────
  const [activeTab, setActiveTab] = useState<'internal' | 'external'>('internal');

  // ── Load contacts on open ────────────────────────────────────────────────
  useEffect(() => {
    if (!open) return;
    // Reset all state
    setActiveTab('internal');
    setSelectedContactId('');
    setAccessLevel('view');
    setInternalExpiry('never');
    setInternalCustomDate('');
    setInternalError('');
    setExternalExpiry('7days');
    setExternalCustomDate('');
    setAllowDownload(true);
    setPasswordProtect(false);
    setPassword('');
    setExternalError('');
    setGeneratedLink('');
    setLinkCopied(false);

    setLoadingContacts(true);
    fetchTrustedContacts(1, 100)
      .then((res) => {
        setContacts(res.items);
        if (res.items.length > 0) setSelectedContactId(res.items[0].id);
      })
      .catch(() => setInternalError('Failed to load trusted contacts.'))
      .finally(() => setLoadingContacts(false));
  }, [open]);

  // ── Internal share submit ────────────────────────────────────────────────
  const handleInternalShare = async (e: FormEvent) => {
    e.preventDefault();
    if (!document || !selectedContactId) {
      setInternalError('Please select a trusted contact.');
      return;
    }

    setInternalSubmitting(true);
    setInternalError('');

    let expiresAt: string | undefined;
    if (internalExpiry === 'custom' && internalCustomDate) {
      expiresAt = new Date(internalCustomDate).toISOString();
    } else {
      expiresAt = getExpiryDate(internalExpiry);
    }

    const contactName = contacts.find((c) => c.id === selectedContactId)?.full_name ?? 'contact';

    try {
      await createInternalShare({
        document_id: document.id,
        contact_id: selectedContactId,
        access_level: accessLevel,
        expires_at: expiresAt,
      });
      toast.success(`Document shared successfully with ${contactName}.`);
      onClose();
    } catch (err: any) {
      setInternalError(err.response?.data?.detail || 'Unable to share document.');
    } finally {
      setInternalSubmitting(false);
    }
  };

  // ── External link submit ─────────────────────────────────────────────────
  const handleGenerateLink = async (e: FormEvent) => {
    e.preventDefault();
    if (!document) return;

    setExternalSubmitting(true);
    setExternalError('');
    setGeneratedLink('');

    let expiresAt: string | undefined;
    if (externalExpiry === 'custom' && externalCustomDate) {
      expiresAt = new Date(externalCustomDate).toISOString();
    } else {
      expiresAt = getExpiryDate(externalExpiry);
    }

    // Use first contact or empty string — external share requires a contact_id
    // We pick the first available contact; if none, the backend will handle gracefully
    const contactId = contacts.length > 0 ? contacts[0].id : selectedContactId;

    try {
      const share = await createDocumentShare({
        document_id: document.id,
        contact_id: contactId || selectedContactId,
        expires_at: expiresAt,
        allow_download: allowDownload,
        password: passwordProtect && password ? password : undefined,
      });
      const link = `${window.location.origin}/shared/${share.access_token}`;
      setGeneratedLink(link);
      toast.success('Secure share link generated!');
    } catch (err: any) {
      setExternalError(err.response?.data?.detail || 'Unable to generate link.');
    } finally {
      setExternalSubmitting(false);
    }
  };

  const handleCopyLink = () => {
    if (!generatedLink) return;
    navigator.clipboard.writeText(generatedLink);
    setLinkCopied(true);
    toast.success('Link copied successfully.');
    setTimeout(() => setLinkCopied(false), 2000);
  };

  if (!open || !document) return null;

  const accessLevels: AccessLevel[] = ['view', 'view_download', 'edit_metadata'];
  const internalExpiryOptions: { value: ExpiryOption; label: string }[] = [
    { value: 'never', label: 'Never Expires' },
    { value: '7days', label: '7 Days' },
    { value: '30days', label: '30 Days' },
    { value: 'custom', label: 'Custom Date' },
  ];
  const externalExpiryOptions: { value: ExternalExpiryOption; label: string }[] = [
    { value: '24hours', label: '24 Hours' },
    { value: '7days', label: '7 Days' },
    { value: '30days', label: '30 Days' },
    { value: 'custom', label: 'Custom Date' },
  ];

  return (
    <div className="dsm-overlay" onClick={onClose} role="dialog" aria-modal="true" aria-label="Share document">
      <div className="dsm-window" onClick={(e) => e.stopPropagation()}>
        {/* ── Header ──────────────────────────────────────────────────────── */}
        <div className="dsm-header">
          <div className="dsm-header-content">
            <div className="dsm-header-icon">
              <span className="material-symbols-outlined">share</span>
            </div>
            <div>
              <h2 className="dsm-title">Share Document</h2>
              <p className="dsm-subtitle">
                <strong>{document.title}</strong>
              </p>
            </div>
          </div>
          <button
            type="button"
            className="dsm-close"
            onClick={onClose}
            aria-label="Close sharing dialog"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <div className="dsm-body">
          {/* Tabs Navigation */}
          <div className="dsm-tabs">
            <button
              type="button"
              className={`dsm-tab-btn ${activeTab === 'internal' ? 'dsm-tab-btn--active' : ''}`}
              onClick={() => setActiveTab('internal')}
            >
              <span className="material-symbols-outlined">group</span>
              Share with Trusted Contact
            </button>
            <button
              type="button"
              className={`dsm-tab-btn ${activeTab === 'external' ? 'dsm-tab-btn--active' : ''}`}
              onClick={() => setActiveTab('external')}
            >
              <span className="material-symbols-outlined">link</span>
              Generate External Link
            </button>
          </div>

          {activeTab === 'internal' ? (
            /* ══ SECTION A — Internal Share ════════════════════════════════ */
            <section className="dsm-section">
              <div className="dsm-section-heading">
                <span className="material-symbols-outlined dsm-section-icon dsm-section-icon--internal">
                  group
                </span>
                <div>
                  <h3>Share with Trusted Contact</h3>
                  <p>Give access to another VaultPass user from your trusted contacts list.</p>
                </div>
              </div>

              {loadingContacts ? (
                <div className="dsm-loading">
                  <div className="dsm-spinner" />
                  <span>Loading contacts…</span>
                </div>
              ) : contacts.length === 0 ? (
                <div className="dsm-empty-contacts">
                  <span className="material-symbols-outlined">person_off</span>
                  <p>
                    No trusted contacts yet.{' '}
                    <a href="/trusted-contacts">Add a trusted contact</a> first.
                  </p>
                </div>
              ) : (
                <form onSubmit={handleInternalShare} className="dsm-form">
                  {/* Contact picker */}
                  <div className="dsm-field">
                    <label className="dsm-label">Select Contact</label>
                    <div className="dsm-contact-grid">
                      {contacts.map((c) => (
                        <ContactCard
                          key={c.id}
                          contact={c}
                          selected={selectedContactId === c.id}
                          onSelect={() => setSelectedContactId(c.id)}
                        />
                      ))}
                    </div>
                  </div>

                  {(() => {
                    const selContact = contacts.find((c) => c.id === selectedContactId);
                    if (selContact && !selContact.linked_user_id) {
                      return (
                        <div className="dsm-warning-alert" style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '12px',
                          background: '#fffbeb',
                          border: '1px solid #fef3c7',
                          color: '#b45309',
                          padding: '12px 16px',
                          borderRadius: '12px',
                          fontSize: '0.9rem',
                          lineHeight: '1.5',
                          marginBottom: '16px'
                        }}>
                          <span className="material-symbols-outlined" style={{ color: '#d97706', fontSize: '1.25rem' }}>warning</span>
                          <p style={{ margin: 0 }}>
                            This contact is not a registered VaultPass user. Only an external link will work unless they create an account.
                          </p>
                        </div>
                      );
                    }
                    return null;
                  })()}

                  {/* Permission selector */}
                  <div className="dsm-field">
                    <label className="dsm-label">Permission Level</label>
                    <div className="dsm-permission-list">
                      {accessLevels.map((level) => (
                        <label
                          key={level}
                          className={`dsm-permission-option ${accessLevel === level ? 'dsm-permission-option--active' : ''}`}
                        >
                          <input
                            type="radio"
                            name="access_level"
                            value={level}
                            checked={accessLevel === level}
                            onChange={() => setAccessLevel(level)}
                          />
                          <div className="dsm-permission-content">
                            <span className="dsm-permission-label">{ACCESS_LEVEL_LABELS[level]}</span>
                            <span className="dsm-permission-desc">{ACCESS_LEVEL_DESCRIPTIONS[level]}</span>
                          </div>
                        </label>
                      ))}
                    </div>
                  </div>

                  {/* Expiration */}
                  <div className="dsm-field">
                    <label className="dsm-label">Access Expiration</label>
                    <div className="dsm-chip-group">
                      {internalExpiryOptions.map((opt) => (
                        <button
                          key={opt.value}
                          type="button"
                          className={`dsm-chip ${internalExpiry === opt.value ? 'dsm-chip--active' : ''}`}
                          onClick={() => setInternalExpiry(opt.value)}
                        >
                          {opt.label}
                        </button>
                      ))}
                    </div>
                    {internalExpiry === 'custom' && (
                      <input
                        type="date"
                        className="dsm-date-input"
                        value={internalCustomDate}
                        onChange={(e) => setInternalCustomDate(e.target.value)}
                        min={new Date().toISOString().split('T')[0]}
                      />
                    )}
                  </div>

                  {internalError && <div className="dsm-error">{internalError}</div>}

                  <button
                    type="submit"
                    className="dsm-btn dsm-btn--internal"
                    disabled={internalSubmitting || !selectedContactId}
                  >
                    {internalSubmitting ? (
                      <>
                        <div className="dsm-btn-spinner" />
                        Sharing…
                      </>
                    ) : (
                      <>
                        <span className="material-symbols-outlined">send</span>
                        Share Internally
                      </>
                    )}
                  </button>
                </form>
              )}
            </section>
          ) : (
            /* ══ SECTION B — External Link ════════════════════════════════ */
            <section className="dsm-section">
              <div className="dsm-section-heading">
                <span className="material-symbols-outlined dsm-section-icon dsm-section-icon--external">
                  link
                </span>
                <div>
                  <h3>Generate External Link</h3>
                  <p>Create a secure shareable link for recipients who do not use VaultPass.</p>
                </div>
              </div>

              <form onSubmit={handleGenerateLink} className="dsm-form">
                {/* Link expiration */}
                <div className="dsm-field">
                  <label className="dsm-label">Link Expiration</label>
                  <div className="dsm-chip-group">
                    {externalExpiryOptions.map((opt) => (
                      <button
                        key={opt.value}
                        type="button"
                        className={`dsm-chip ${externalExpiry === opt.value ? 'dsm-chip--active' : ''}`}
                        onClick={() => setExternalExpiry(opt.value)}
                      >
                        {opt.label}
                      </button>
                    ))}
                  </div>
                  {externalExpiry === 'custom' && (
                    <input
                      type="date"
                      className="dsm-date-input"
                      value={externalCustomDate}
                      onChange={(e) => setExternalCustomDate(e.target.value)}
                      min={new Date().toISOString().split('T')[0]}
                    />
                  )}
                </div>

                {/* Options */}
                <div className="dsm-field dsm-field--row">
                  <label className="dsm-checkbox-label">
                    <input
                      type="checkbox"
                      checked={allowDownload}
                      onChange={(e) => setAllowDownload(e.target.checked)}
                    />
                    <span>Allow Download</span>
                  </label>
                  <label className="dsm-checkbox-label">
                    <input
                      type="checkbox"
                      checked={passwordProtect}
                      onChange={(e) => setPasswordProtect(e.target.checked)}
                    />
                    <span>Password Protect Link</span>
                  </label>
                </div>

                {passwordProtect && (
                  <div className="dsm-field">
                    <label className="dsm-label">Link Password</label>
                    <input
                      type="password"
                      className="dsm-text-input"
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="Enter a password for this link"
                    />
                  </div>
                )}

                {externalError && <div className="dsm-error">{externalError}</div>}

                {/* Generated link result */}
                {generatedLink && (
                  <div className="dsm-link-result">
                    <div className="dsm-link-result-url">
                      <span className="material-symbols-outlined">link</span>
                      <input type="text" readOnly value={generatedLink} className="dsm-link-input" />
                      <button
                        type="button"
                        className={`dsm-copy-btn ${linkCopied ? 'dsm-copy-btn--copied' : ''}`}
                        onClick={handleCopyLink}
                      >
                        <span className="material-symbols-outlined">
                          {linkCopied ? 'check' : 'content_copy'}
                        </span>
                        {linkCopied ? 'Copied!' : 'Copy'}
                      </button>
                    </div>
                    <p className="dsm-link-hint">
                      Share this link with your recipient. It will expire based on the settings above.
                    </p>
                  </div>
                )}

                <button
                  type="submit"
                  className="dsm-btn dsm-btn--external"
                  disabled={externalSubmitting}
                >
                  {externalSubmitting ? (
                    <>
                      <div className="dsm-btn-spinner" />
                      Generating…
                    </>
                  ) : (
                    <>
                      <span className="material-symbols-outlined">lock</span>
                      Generate Secure Link
                    </>
                  )}
                </button>
              </form>
            </section>
          )}
        </div>

        {/* ── Footer ──────────────────────────────────────────────────────── */}
        <div className="dsm-footer">
          <button type="button" className="dsm-btn dsm-btn--ghost" onClick={onClose}>
            Close
          </button>
        </div>
      </div>
    </div>
  );
}
