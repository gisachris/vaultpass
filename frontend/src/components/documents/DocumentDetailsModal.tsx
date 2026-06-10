import { useEffect, useState } from 'react';
import { toast } from 'sonner';
import { DocumentModel, DOCUMENT_TYPE_LABELS } from '../../types/document';
import {
  fetchSharesForDocument,
  revokeDocumentShare,
  DocumentShareModel,
  ACCESS_LEVEL_LABELS,
} from '../../services/documentShareService';

interface DocumentDetailsModalProps {
  open: boolean;
  document: DocumentModel | null;
  onClose: () => void;
  onEdit: () => void;
  onDownload: () => void;
  onDelete: () => void;
  onShareRefresh?: () => void;
}

function formatDate(value: string | null | undefined) {
  if (!value) {
    return 'Not provided';
  }
  return new Date(value).toLocaleDateString(undefined, {
    month: 'short',
    day: 'numeric',
    year: 'numeric',
  });
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function ShareStatusBadge({ share }: { share: DocumentShareModel }) {
  const expired = share.expires_at ? new Date(share.expires_at) < new Date() : false;
  if (!share.is_active) return <span className="ddm-status-badge ddm-status-badge--revoked">Revoked</span>;
  if (expired) return <span className="ddm-status-badge ddm-status-badge--expired">Expired</span>;
  return <span className="ddm-status-badge ddm-status-badge--active">Active</span>;
}

export function DocumentDetailsModal({
  open,
  document,
  onClose,
  onEdit,
  onDownload,
  onDelete,
  onShareRefresh,
}: DocumentDetailsModalProps) {
  const [shares, setShares] = useState<DocumentShareModel[]>([]);
  const [sharesLoading, setSharesLoading] = useState(false);
  const [revokingId, setRevokingId] = useState<string | null>(null);

  useEffect(() => {
    if (!open || !document) return;
    setSharesLoading(true);
    fetchSharesForDocument(document.id)
      .then(setShares)
      .catch(() => setShares([]))
      .finally(() => setSharesLoading(false));
  }, [open, document]);

  const handleRevoke = async (shareId: string) => {
    setRevokingId(shareId);
    try {
      await revokeDocumentShare(shareId);
      toast.success('Share access revoked.');
      setShares((prev) =>
        prev.map((s) => (s.id === shareId ? { ...s, is_active: false } : s)),
      );
      onShareRefresh?.();
    } catch {
      toast.error('Failed to revoke share.');
    } finally {
      setRevokingId(null);
    }
  };

  if (!open || !document) {
    return null;
  }

  const internalShares = shares.filter((s) => s.recipient_user_id);
  const externalShares = shares.filter((s) => !s.recipient_user_id);

  return (
    <div className="documents-modal-overlay" onClick={onClose}>
      <div className="documents-modal-window" onClick={(event) => event.stopPropagation()}>
        <div className="documents-modal-header">
          <div>
            <h2>{document.title}</h2>
            <p>Document details and actions</p>
          </div>
          <button type="button" className="documents-modal-close" onClick={onClose} aria-label="Close details dialog">
            ×
          </button>
        </div>

        <div className="documents-modal-body">
          {/* ── Core details ─────────────────────────────────────────── */}
          <div className="documents-modal-row">
            <span>Type</span>
            <strong>{DOCUMENT_TYPE_LABELS[document.document_type]}</strong>
          </div>
          <div className="documents-modal-row">
            <span>Uploaded</span>
            <strong>{formatDate(document.uploaded_at)}</strong>
          </div>
          <div className="documents-modal-row">
            <span>File name</span>
            <strong>{document.file_name}</strong>
          </div>
          <div className="documents-modal-row">
            <span>File size</span>
            <strong>{formatFileSize(document.file_size)}</strong>
          </div>
          <div className="documents-modal-row">
            <span>Expiry date</span>
            <strong>{document.expiry_date ? formatDate(document.expiry_date) : 'No expiry set'}</strong>
          </div>
          <div className="documents-modal-row documents-modal-row--full">
            <span>Description</span>
            <p>{document.description || 'No description available.'}</p>
          </div>

          {/* ── Sharing Information ──────────────────────────────────── */}
          <div className="ddm-sharing-section">
            <div className="ddm-sharing-title">
              <span className="material-symbols-outlined">share</span>
              Sharing Information
            </div>

            {sharesLoading ? (
              <div className="ddm-shares-loading">
                <div className="ddm-spinner" />
                <span>Loading share info…</span>
              </div>
            ) : shares.length === 0 ? (
              <p className="ddm-no-shares">This document has not been shared yet.</p>
            ) : (
              <>
                {/* Internal shares */}
                {internalShares.length > 0 && (
                  <div className="ddm-share-group">
                    <p className="ddm-share-group-label">
                      <span className="material-symbols-outlined">group</span>
                      Internal Shares ({internalShares.length})
                    </p>
                    <div className="ddm-share-list">
                      {internalShares.map((share) => (
                        <div key={share.id} className="ddm-share-row">
                          <div className="ddm-share-meta">
                            <p className="ddm-share-name">{share.contact_name ?? 'Trusted Contact'}</p>
                            <div className="ddm-share-tags">
                              <span className="ddm-perm-badge">
                                {share.access_level
                                  ? ACCESS_LEVEL_LABELS[share.access_level]
                                  : 'View Only'}
                              </span>
                              <span className="ddm-expiry-text">
                                {share.expires_at
                                  ? `Expires ${formatDate(share.expires_at)}`
                                  : 'Never expires'}
                              </span>
                            </div>
                          </div>
                          <div className="ddm-share-actions">
                            <ShareStatusBadge share={share} />
                            {share.is_active && (
                              <button
                                type="button"
                                className="ddm-revoke-btn"
                                onClick={() => handleRevoke(share.id)}
                                disabled={revokingId === share.id}
                              >
                                {revokingId === share.id ? 'Revoking…' : 'Revoke'}
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {/* External links */}
                {externalShares.length > 0 && (
                  <div className="ddm-share-group">
                    <p className="ddm-share-group-label">
                      <span className="material-symbols-outlined">link</span>
                      External Links ({externalShares.length})
                    </p>
                    <div className="ddm-share-list">
                      {externalShares.map((share) => (
                        <div key={share.id} className="ddm-share-row">
                          <div className="ddm-share-meta">
                            <p className="ddm-share-name">
                              {share.contact_name
                                ? `Shared via ${share.contact_name}`
                                : 'External link'}
                            </p>
                            <div className="ddm-share-tags">
                              <span className="ddm-expiry-text">
                                Created {formatDate(share.created_at)}
                              </span>
                              <span className="ddm-expiry-text">
                                {share.expires_at
                                  ? `Expires ${formatDate(share.expires_at)}`
                                  : 'Never expires'}
                              </span>
                            </div>
                          </div>
                          <div className="ddm-share-actions">
                            <ShareStatusBadge share={share} />
                            {share.is_active && (
                              <button
                                type="button"
                                className="ddm-revoke-btn"
                                onClick={() => handleRevoke(share.id)}
                                disabled={revokingId === share.id}
                              >
                                {revokingId === share.id ? 'Revoking…' : 'Revoke'}
                              </button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </>
            )}
          </div>
        </div>

        <div className="documents-modal-actions">
          <button type="button" className="button button-secondary" onClick={onDownload}>
            Download
          </button>
          <button type="button" className="button button-primary" onClick={onEdit}>
            Edit document
          </button>
          <button type="button" className="button button-secondary" onClick={onDelete}>
            Delete
          </button>
        </div>
      </div>
    </div>
  );
}
