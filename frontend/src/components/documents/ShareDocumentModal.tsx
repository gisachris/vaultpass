import { useEffect, useState, FormEvent } from 'react';
import { toast } from 'sonner';
import { createDocumentShare } from '../../services/documentShareService';
import { fetchTrustedContacts } from '../../services/trustedContactsService';
import { DocumentModel } from '../../types/document';
import { TrustedContactModel } from '../../types/trustedContact';

interface ShareDocumentModalProps {
  open: boolean;
  document: DocumentModel | null;
  onClose: () => void;
}

export function ShareDocumentModal({ open, document, onClose }: ShareDocumentModalProps) {
  const [contacts, setContacts] = useState<TrustedContactModel[]>([]);
  const [selectedContactId, setSelectedContactId] = useState('');
  const [expiresAt, setExpiresAt] = useState('');
  const [loadingContacts, setLoadingContacts] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');
  const [generatedLink, setGeneratedLink] = useState('');

  useEffect(() => {
    if (open) {
      setLoadingContacts(true);
      setError('');
      setGeneratedLink('');
      setSelectedContactId('');
      setExpiresAt('');
      
      fetchTrustedContacts(1, 100)
        .then((res) => {
          setContacts(res.items);
          if (res.items.length > 0) {
            setSelectedContactId(res.items[0].id);
          }
        })
        .catch(() => {
          setError('Failed to load trusted contacts.');
        })
        .finally(() => {
          setLoadingContacts(false);
        });
    }
  }, [open]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!document || !selectedContactId) {
      setError('Please select a trusted contact.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      const share = await createDocumentShare({
        document_id: document.id,
        contact_id: selectedContactId,
        expires_at: expiresAt ? new Date(expiresAt).toISOString() : undefined,
      });

      // Construct frontend link rather than utilizing hardcoded backend link
      const frontendLink = `${window.location.origin}/shared/${share.access_token}`;
      setGeneratedLink(frontendLink);
      toast.success('Secure share link generated successfully!');
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Unable to generate share link.');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCopyLink = () => {
    if (generatedLink) {
      navigator.clipboard.writeText(generatedLink);
      toast.success('Copied link to clipboard!');
    }
  };

  if (!open || !document) {
    return null;
  }

  return (
    <div className="documents-modal-overlay" onClick={onClose}>
      <div className="documents-modal-window" onClick={(event) => event.stopPropagation()}>
        <div className="documents-modal-header">
          <div>
            <h2>Share document</h2>
            <p>Generate a secure temporary or permanent access link for <strong>{document.title}</strong>.</p>
          </div>
          <button type="button" className="documents-modal-close" onClick={onClose} aria-label="Close share dialog">
            ×
          </button>
        </div>

        {generatedLink ? (
          <div className="documents-modal-body">
            <div className="documents-modal-row documents-modal-row--full">
              <label>Generated Share Link</label>
              <div style={{ display: 'flex', gap: '8px', marginTop: '4px' }}>
                <input
                  type="text"
                  readOnly
                  value={generatedLink}
                  style={{ flex: 1, padding: '10px', borderRadius: '8px', border: '1px solid #e2e8f0', background: '#f8fafc' }}
                />
                <button type="button" className="button button-primary" onClick={handleCopyLink}>
                  Copy
                </button>
              </div>
              <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '6px' }}>
                Provide this link to your trusted contact. They will be able to access the document metadata and download the file.
              </p>
            </div>
            <div className="documents-modal-actions" style={{ padding: '16px 0 0' }}>
              <button type="button" className="button button-secondary" onClick={onClose}>
                Done
              </button>
            </div>
          </div>
        ) : (
          <form className="documents-modal-body" onSubmit={handleSubmit}>
            {error && <div className="documents-modal-error">{error}</div>}

            {loadingContacts ? (
              <p>Loading trusted contacts...</p>
            ) : contacts.length === 0 ? (
              <div className="documents-modal-row documents-modal-row--full">
                <p style={{ color: '#475569' }}>
                  You do not have any trusted contacts yet. Please add a trusted contact first in the "Trusted Contacts" tab.
                </p>
                <div className="documents-modal-actions" style={{ padding: '16px 0 0' }}>
                  <button type="button" className="button button-secondary" onClick={onClose}>
                    Close
                  </button>
                </div>
              </div>
            ) : (
              <>
                <div className="documents-modal-row documents-modal-row--full">
                  <label htmlFor="share-contact">Select Trusted Contact</label>
                  <select
                    id="share-contact"
                    value={selectedContactId}
                    onChange={(event) => setSelectedContactId(event.target.value)}
                  >
                    {contacts.map((contact) => (
                      <option key={contact.id} value={contact.id}>
                        {contact.full_name} ({contact.relationship})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="documents-modal-row documents-modal-row--full">
                  <label htmlFor="share-expiry">Link Expiration (Optional)</label>
                  <input
                    id="share-expiry"
                    type="datetime-local"
                    value={expiresAt}
                    onChange={(event) => setExpiresAt(event.target.value)}
                  />
                  <p style={{ fontSize: '0.85rem', color: '#64748b', marginTop: '4px' }}>
                    Leave blank for a permanent share link.
                  </p>
                </div>

                <div className="documents-modal-actions">
                  <button type="button" className="button button-secondary" onClick={onClose} disabled={submitting}>
                    Cancel
                  </button>
                  <button type="submit" className="button button-primary" disabled={submitting}>
                    {submitting ? 'Generating…' : 'Generate Link'}
                  </button>
                </div>
              </>
            )}
          </form>
        )}
      </div>
    </div>
  );
}
