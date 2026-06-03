import { DocumentModel, DOCUMENT_TYPE_LABELS } from '../../types/document';

interface DocumentDetailsModalProps {
  open: boolean;
  document: DocumentModel | null;
  onClose: () => void;
  onEdit: () => void;
  onDownload: () => void;
  onDelete: () => void;
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

export function DocumentDetailsModal({ open, document, onClose, onEdit, onDownload, onDelete }: DocumentDetailsModalProps) {
  if (!open || !document) {
    return null;
  }

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
