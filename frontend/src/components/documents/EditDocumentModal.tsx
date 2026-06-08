import { FormEvent, useEffect, useState } from 'react';
import { DocumentModel, DocumentType, DOCUMENT_TYPE_LABELS } from '../../types/document';

interface EditDocumentModalProps {
  open: boolean;
  document: DocumentModel | null;
  onClose: () => void;
  onSave: (payload: { title: string; document_type: string; description?: string; expiry_date?: string }) => Promise<void>;
}

export function EditDocumentModal({ open, document, onClose, onSave }: EditDocumentModalProps) {
  const [title, setTitle] = useState('');
  const [documentType, setDocumentType] = useState<DocumentType>('PASSPORT');
  const [description, setDescription] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!document || !open) {
      setTitle('');
      setDocumentType('PASSPORT');
      setDescription('');
      setExpiryDate('');
      setError('');
      return;
    }

    setTitle(document.title);
    setDocumentType(document.document_type);
    setDescription(document.description ?? '');
    setExpiryDate(document.expiry_date ? document.expiry_date.slice(0, 10) : '');
    setError('');
  }, [document, open]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!document) {
      return;
    }
    if (!title.trim()) {
      setError('Please provide a title.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await onSave({
        title: title.trim(),
        document_type: documentType,
        description: description.trim() || undefined,
        expiry_date: expiryDate || undefined,
      });
      onClose();
    } catch (err) {
      setError('Unable to save changes at this time.');
    } finally {
      setSubmitting(false);
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
            <h2>Edit document</h2>
            <p>Update title, category, expiry date, and description.</p>
          </div>
          <button type="button" className="documents-modal-close" onClick={onClose} aria-label="Close edit dialog">
            ×
          </button>
        </div>

        <form className="documents-modal-body" onSubmit={handleSubmit}>
          <div className="documents-modal-row documents-modal-row--full">
            <label htmlFor="edit-title">Title</label>
            <input
              id="edit-title"
              type="text"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Document title"
            />
          </div>

          <div className="documents-modal-row documents-modal-row--half">
            <label htmlFor="edit-type">Document type</label>
            <select
              id="edit-type"
              value={documentType}
              onChange={(event) => setDocumentType(event.target.value as DocumentType)}
            >
              {Object.entries(DOCUMENT_TYPE_LABELS).map(([key, label]) => (
                <option key={key} value={key}>
                  {label}
                </option>
              ))}
            </select>
          </div>

          <div className="documents-modal-row documents-modal-row--half">
            <label htmlFor="edit-expiry">Expiry date</label>
            <input
              id="edit-expiry"
              type="date"
              value={expiryDate}
              onChange={(event) => setExpiryDate(event.target.value)}
            />
          </div>

          <div className="documents-modal-row documents-modal-row--full">
            <label htmlFor="edit-description">Description</label>
            <textarea
              id="edit-description"
              rows={4}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Optional notes for future reference"
            />
          </div>

          {error && <div className="documents-modal-error">{error}</div>}

          <div className="documents-modal-actions">
            <button type="submit" className="button button-primary" disabled={submitting}>
              {submitting ? 'Saving…' : 'Save changes'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
