import { useEffect, useMemo, useRef, useState } from 'react';
import { DocumentModel, DOCUMENT_TYPE_ICONS, DOCUMENT_TYPE_LABELS } from '../../types/document';
import type { DocumentShareInfo } from '../../services/documentShareService';

interface DocumentRowProps {
  document: DocumentModel;
  onViewDetails: (document: DocumentModel) => void;
  onDownload: (document: DocumentModel) => void;
  onEdit: (document: DocumentModel) => void;
  onDelete: (document: DocumentModel) => void;
  onShare: (document: DocumentModel) => void;
  shareInfo?: DocumentShareInfo;
}

function getExpiryStatus(document: DocumentModel) {
  if (!document.expiry_date) {
    return { label: 'No Expiry', style: 'success' };
  }

  const expiry = new Date(document.expiry_date);
  const now = new Date();

  if (expiry < now) {
    return { label: `Expired ${expiry.toLocaleDateString()}`, style: 'expired' };
  }

  const diffDays = Math.ceil((expiry.getTime() - now.getTime()) / (1000 * 60 * 60 * 24));
  return { label: `Expires in ${diffDays} days`, style: 'warning' };
}

function formatFileSize(bytes: number) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }
  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function ShareBadges({ info }: { info: DocumentShareInfo }) {
  const { hasInternal, hasExternal, internalCount, externalCount } = info;

  if (!hasInternal && !hasExternal) return null;

  // Both sharing types
  if (hasInternal && hasExternal) {
    return (
      <>
        <span className="doc-share-badge doc-share-badge--internal" title={`${internalCount} internal share${internalCount !== 1 ? 's' : ''}`}>
          <span className="material-symbols-outlined">group</span>
          {internalCount}
        </span>
        <span className="doc-share-badge doc-share-badge--external" title={`${externalCount} external link${externalCount !== 1 ? 's' : ''}`}>
          <span className="material-symbols-outlined">link</span>
          Link
        </span>
      </>
    );
  }

  if (hasInternal) {
    return (
      <span className="doc-share-badge doc-share-badge--internal" title={`Shared with ${internalCount} contact${internalCount !== 1 ? 's' : ''}`}>
        <span className="material-symbols-outlined">group</span>
        {internalCount > 1 ? `${internalCount} contacts` : 'Internal'}
      </span>
    );
  }

  return (
    <span className="doc-share-badge doc-share-badge--external" title="External share link active">
      <span className="material-symbols-outlined">link</span>
      External
    </span>
  );
}

export function DocumentRow({ document, onViewDetails, onDownload, onEdit, onDelete, onShare, shareInfo }: DocumentRowProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const actionsRef = useRef<HTMLDivElement | null>(null);
  const expiry = useMemo(() => getExpiryStatus(document), [document]);

  useEffect(() => {
    if (!menuOpen) {
      return;
    }

    const handleClickOutside = (event: MouseEvent) => {
      if (actionsRef.current && !actionsRef.current.contains(event.target as Node)) {
        setMenuOpen(false);
      }
    };

    window.addEventListener('mousedown', handleClickOutside);
    return () => window.removeEventListener('mousedown', handleClickOutside);
  }, [menuOpen]);

  const uploadedAt = useMemo(
    () => new Date(document.uploaded_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }),
    [document.uploaded_at],
  );
  const fileSize = useMemo(() => formatFileSize(document.file_size), [document.file_size]);
  const isExpired = expiry.style === 'expired';

  return (
    <div className={`document-row ${isExpired ? 'document-row--expired' : ''} ${menuOpen ? 'document-row--menu-open' : ''}`}>
      <div className="document-row-left" onClick={() => onViewDetails(document)}>
        <div className="document-row-avatar">
          <span className="material-symbols-outlined">{DOCUMENT_TYPE_ICONS[document.document_type]}</span>
        </div>
        <div className="document-row-copy">
          <h3>{document.title}</h3>
          <div className="document-row-meta">
            <span>{uploadedAt}</span>
            <span className="document-row-separator" />
            <span>{fileSize}</span>
          </div>
        </div>
      </div>

      <div className="document-row-right">
        <div className="document-row-tags">
          <span className="document-row-type">{DOCUMENT_TYPE_LABELS[document.document_type]}</span>
          <span className={`document-row-expiry document-row-expiry--${expiry.style}`}>{expiry.label}</span>
          {shareInfo && <ShareBadges info={shareInfo} />}
        </div>
        <div className="document-row-actions" ref={actionsRef}>
          <button
            type="button"
            className="document-row-action-button"
            onClick={(event) => {
              event.stopPropagation();
              setMenuOpen((current) => !current);
            }}
            aria-haspopup="true"
            aria-expanded={menuOpen}
          >
            <span className="material-symbols-outlined">more_vert</span>
          </button>
          {menuOpen && (
            <div className="document-row-menu" role="menu">
              <button type="button" onClick={() => { setMenuOpen(false); onViewDetails(document); }}>
                <span className="material-symbols-outlined">info</span>
                View details
              </button>
              <button type="button" onClick={() => { setMenuOpen(false); onShare(document); }}>
                <span className="material-symbols-outlined">share</span>
                Share document
              </button>
              <button type="button" onClick={() => { setMenuOpen(false); onDownload(document); }}>
                <span className="material-symbols-outlined">download</span>
                Download
              </button>
              <button type="button" onClick={() => { setMenuOpen(false); onEdit(document); }}>
                <span className="material-symbols-outlined">edit</span>
                Edit details
              </button>
              <button type="button" className="document-row-menu-danger" onClick={() => { setMenuOpen(false); onDelete(document); }}>
                <span className="material-symbols-outlined">delete</span>
                Delete
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
