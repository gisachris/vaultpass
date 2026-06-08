import { FormEvent, useEffect, useState } from 'react';
import { DocumentType, DocumentUploadPayload, DOCUMENT_TYPE_LABELS } from '../../types/document';
import { uploadDocument } from '../../services/documentService';

interface UploadDocumentModalProps {
  open: boolean;
  file: File | null;
  onClose: () => void;
  onUploadSuccess: () => void;
}

export function UploadDocumentModal({ open, file, onClose, onUploadSuccess }: UploadDocumentModalProps) {
  const [title, setTitle] = useState('');
  const [documentType, setDocumentType] = useState<DocumentType>('PASSPORT');
  const [description, setDescription] = useState('');
  const [expiryDate, setExpiryDate] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState('');

  useEffect(() => {
    if (!open) {
      setTitle('');
      setDocumentType('PASSPORT');
      setDescription('');
      setExpiryDate('');
      setError('');
    }
    if (file) {
      setTitle(file.name.replace(/\.[^/.]+$/, ''));
    }
  }, [open, file]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!file) {
      setError('Please select a document file first.');
      return;
    }
    if (!title.trim()) {
      setError('Please add a title for the document.');
      return;
    }

    setSubmitting(true);
    setError('');

    try {
      await uploadDocument({
        file,
        title: title.trim(),
        document_type: documentType,
        description: description.trim() || undefined,
        expiry_date: expiryDate || undefined,
      });
      onUploadSuccess();
    } catch (err) {
      setError('Unable to upload document. Please try again.');
    } finally {
      setSubmitting(false);
    }
  };

  if (!open) {
    return null;
  }

  return (
    <div className="documents-modal-overlay" onClick={onClose}>
      <div className="documents-modal-window" onClick={(event) => event.stopPropagation()}>
        <div className="documents-modal-header">
          <div>
            <h2>Upload document</h2>
            <p>Complete the upload form and secure the file to your vault.</p>
          </div>
          <button type="button" className="documents-modal-close" onClick={onClose} aria-label="Close upload dialog">
            ×
          </button>
        </div>

        <form className="documents-modal-body" onSubmit={handleSubmit}>
          <div className="documents-modal-row documents-modal-row--full">
            <label htmlFor="upload-title">Title</label>
            <input
              id="upload-title"
              type="text"
              value={title}
              onChange={(event) => setTitle(event.target.value)}
              placeholder="Document title"
            />
          </div>

          <div className="documents-modal-row documents-modal-row--half">
            <label htmlFor="upload-type">Document type</label>
            <select
              id="upload-type"
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
            <label htmlFor="upload-expiry">Expiry date</label>
            <input
              id="upload-expiry"
              type="date"
              value={expiryDate}
              onChange={(event) => setExpiryDate(event.target.value)}
            />
          </div>

          <div className="documents-modal-row documents-modal-row--full">
            <label htmlFor="upload-description">Description</label>
            <textarea
              id="upload-description"
              rows={4}
              value={description}
              onChange={(event) => setDescription(event.target.value)}
              placeholder="Optional notes for future reference"
            />
          </div>

          {file && (
            <div className="documents-upload-file-summary">
              <span>{file.name}</span>
              <span>{Math.max(1, Math.round(file.size / 1024))} KB</span>
            </div>
          )}

          {error && <div className="documents-modal-error">{error}</div>}

          <div className="documents-modal-actions">
            <button type="submit" className="button button-primary" disabled={submitting}>
              {submitting ? 'Uploading…' : 'Upload document'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
