import { useMemo, useState } from 'react';
import { DocumentModel, DOCUMENT_TYPE_ICONS, DOCUMENT_TYPE_LABELS } from '../../types/document';

interface DocumentRowProps {
  document: DocumentModel;
  onViewDetails: (document: DocumentModel) => void;
  onDownload: (document: DocumentModel) => void;
  onEdit: (document: DocumentModel) => void;
  onDelete: (document: DocumentModel) => void;
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

export function DocumentRow({ document, onViewDetails, onDownload, onEdit, onDelete }: DocumentRowProps) {
  const [menuOpen, setMenuOpen] = useState(false);
  const expiry = useMemo(() => getExpiryStatus(document), [document]);
  const uploadedAt = useMemo(
    () => new Date(document.uploaded_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric', year: 'numeric' }),
    [document.uploaded_at],
  );
  const fileSize = useMemo(() => formatFileSize(document.file_size), [document.file_size]);
  const isExpired = expiry.style === 'expired';

  return (
    <div className={`document-row ${isExpired ? 'document-row--expired' : ''}`}>
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
        </div>
        <div className="document-row-actions">
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
                View details
              </button>
              <button type="button" onClick={() => { setMenuOpen(false); onDownload(document); }}>
                Download
              </button>
              <button type="button" onClick={() => { setMenuOpen(false); onEdit(document); }}>
                Edit details
              </button>
              <button type="button" onClick={() => { setMenuOpen(false); onDelete(document); }}>
                Delete
              </button>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
