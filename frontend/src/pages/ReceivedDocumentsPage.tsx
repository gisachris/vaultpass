import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { formatDistanceToNow, parseISO, format } from 'date-fns';
import { toast } from 'sonner';
import { AppSidebar } from '../components/ui/AppSidebar';
import { UserProfileMenu } from '../components/profile/UserProfileMenu';
import { fetchReceivedShares, fetchReceivedShareDetail } from '../services/sharedDocumentsService';
import { ACCESS_LEVEL_LABELS } from '../services/documentShareService';
import type { ReceivedShare, ReceivedShareDetail } from '../types/receivedDocuments';
import './ReceivedDocumentsPage.css';

function formatDate(iso: string) {
  try {
    return format(parseISO(iso), 'dd MMM yyyy');
  } catch {
    return '—';
  }
}

function docTypeIcon(type: string) {
  const t = type?.toUpperCase() ?? '';
  if (t.includes('PASSPORT')) return 'travel_explore';
  if (t.includes('ID') || t.includes('NATIONAL')) return 'badge';
  if (t.includes('MEDICAL') || t.includes('HEALTH')) return 'health_and_safety';
  if (t.includes('WILL') || t.includes('LEGAL')) return 'gavel';
  if (t.includes('INSURANCE')) return 'security';
  return 'description';
}

export function ReceivedDocumentsPage() {
  const location = useLocation();
  const navigate = useNavigate();

  const [shares, setShares] = useState<ReceivedShare[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [selectedShare, setSelectedShare] = useState<ReceivedShareDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [modalOpen, setModalOpen] = useState(false);

  // If routed here from a notification with a share_id query param, open it automatically
  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const shareId = params.get('share_id');
    if (shareId && shares.length > 0) {
      openDetail(shareId);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [location.search, shares]);

  const loadShares = async () => {
    setLoading(true);
    setError('');
    try {
      const data = await fetchReceivedShares();
      setShares(data);
    } catch {
      setError('Failed to load received documents.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadShares();
  }, []);

  const openDetail = async (shareId: string) => {
    setDetailLoading(true);
    setModalOpen(true);
    try {
      const detail = await fetchReceivedShareDetail(shareId);
      setSelectedShare(detail);
    } catch {
      toast.error('Could not load document details.');
      setModalOpen(false);
    } finally {
      setDetailLoading(false);
    }
  };

  const closeModal = () => {
    setModalOpen(false);
    setSelectedShare(null);
    // Clear query param
    navigate('/received-documents', { replace: true });
  };

  return (
    <div className="received-layout">
      <AppSidebar />

      <div className="received-main">
        {/* Topbar */}
        <header className="received-topbar">
          <div>
            <h1 className="received-topbar__title">Received Documents</h1>
            <p className="received-topbar__sub">Documents shared with you by trusted contacts</p>
          </div>
          <UserProfileMenu variant="topbar" />
        </header>

        <main className="received-canvas">
          {loading ? (
            <div className="received-loading">
              <div className="spinner" />
              <p>Loading shared documents…</p>
            </div>
          ) : error ? (
            <div className="received-error">
              <span className="material-symbols-outlined">error_outline</span>
              <p>{error}</p>
              <button type="button" className="btn-retry" onClick={loadShares}>
                Try Again
              </button>
            </div>
          ) : shares.length === 0 ? (
            <div className="received-empty">
              <span className="material-symbols-outlined">inbox</span>
              <h2>No documents shared with you yet</h2>
              <p>When someone shares a document with you, it will appear here.</p>
            </div>
          ) : (
            <div className="received-grid">
              {shares.map((share) => {
                const expired = share.expires_at
                  ? new Date(share.expires_at) < new Date()
                  : false;
                const statusText = !share.is_active ? 'Revoked' : expired ? 'Expired' : 'Active';
                const statusClass = !share.is_active
                  ? 'badge--revoked'
                  : expired
                  ? 'badge--expired'
                  : 'badge--active';

                return (
                  <div
                    key={share.share_id}
                    className="received-card"
                    onClick={() => openDetail(share.share_id)}
                    role="button"
                    tabIndex={0}
                    onKeyDown={(e) => e.key === 'Enter' && openDetail(share.share_id)}
                  >
                    <div className="received-card__icon">
                      <span className="material-symbols-outlined">
                        {docTypeIcon(share.document_type)}
                      </span>
                    </div>

                    <div className="received-card__body">
                      <h3 className="received-card__title">{share.document_title}</h3>

                      <div className="received-card__meta">
                        <span className="received-card__meta-item">
                          <span className="material-symbols-outlined">person</span>
                          {share.owner_name}
                        </span>
                        <span className="received-card__meta-item">
                          <span className="material-symbols-outlined">calendar_today</span>
                          {formatDate(share.shared_at)}
                        </span>
                        {share.expires_at && (
                          <span className="received-card__meta-item">
                            <span className="material-symbols-outlined">schedule</span>
                            Expires {formatDate(share.expires_at)}
                          </span>
                        )}
                      </div>

                      <div className="received-card__footer">
                        <span className={`received-badge ${statusClass}`}>{statusText}</span>
                        <span className={`perm-badge perm-badge--${(share.access_level || 'view').replace('_', '-')}`}>
                          {ACCESS_LEVEL_LABELS[share.access_level || 'view']}
                        </span>
                        <span className="received-card__type">{share.document_type}</span>
                      </div>
                    </div>

                    <button
                      type="button"
                      className="received-card__view-btn"
                      onClick={(e) => {
                        e.stopPropagation();
                        openDetail(share.share_id);
                      }}
                    >
                      <span className="material-symbols-outlined">open_in_new</span>
                      View
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </main>
      </div>

      {/* ── Detail Modal ──────────────────────────────────────────────────── */}
      {modalOpen && (
        <div className="modal-overlay" onClick={closeModal}>
          <div
            className="modal-sheet"
            onClick={(e) => e.stopPropagation()}
            role="dialog"
            aria-modal="true"
            aria-label="Document details"
          >
            <button type="button" className="modal-close" onClick={closeModal} aria-label="Close">
              <span className="material-symbols-outlined">close</span>
            </button>

            {detailLoading || !selectedShare ? (
              <div className="modal-loading">
                <div className="spinner" />
                <p>Loading details…</p>
              </div>
            ) : (
              <>
                <div className="modal-header">
                  <div className="modal-doc-icon">
                    <span className="material-symbols-outlined">
                      {docTypeIcon(selectedShare.document_type)}
                    </span>
                  </div>
                  <div>
                    <h2 className="modal-title">{selectedShare.document_title}</h2>
                    <span className="modal-type-badge">{selectedShare.document_type}</span>
                  </div>
                </div>

                <div className="modal-body">
                  <div className="modal-grid">
                    <div className="modal-field">
                      <label>Shared By</label>
                      <p>{selectedShare.owner_name}</p>
                    </div>
                    <div className="modal-field">
                      <label>Date Shared</label>
                      <p>{formatDate(selectedShare.shared_at)}</p>
                    </div>
                    <div className="modal-field">
                      <label>Expiry Date</label>
                      <p>
                        {selectedShare.expires_at
                          ? formatDate(selectedShare.expires_at)
                          : 'Never'}
                      </p>
                    </div>
                    <div className="modal-field">
                      <label>Last Accessed</label>
                      <p>
                        {selectedShare.last_accessed_at
                          ? formatDistanceToNow(parseISO(selectedShare.last_accessed_at), {
                              addSuffix: true,
                            })
                          : 'Not yet accessed'}
                      </p>
                    </div>
                     <div className="modal-field">
                      <label>Status</label>
                      <p className={selectedShare.is_active ? 'text-green' : 'text-red'}>
                        {selectedShare.is_active ? 'Active' : 'Revoked'}
                      </p>
                    </div>
                    <div className="modal-field">
                      <label>Permission Level</label>
                      <p>
                        <span className={`perm-badge perm-badge--${(selectedShare.access_level || 'view').replace('_', '-')}`}>
                          {ACCESS_LEVEL_LABELS[selectedShare.access_level || 'view']}
                        </span>
                      </p>
                    </div>
                  </div>
                </div>

                <div className="modal-actions">
                  <button
                    type="button"
                    className="modal-btn modal-btn--primary"
                    onClick={() =>
                      toast.info('Download requires a secure session link from the document owner.')
                    }
                  >
                    <span className="material-symbols-outlined">download</span>
                    Download
                  </button>
                  <button
                    type="button"
                    className="modal-btn modal-btn--secondary"
                    onClick={closeModal}
                  >
                    Close
                  </button>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
