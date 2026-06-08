import { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { fetchPublicSharedDocument, PublicSharedDocument } from '../services/documentShareService';
import { DOCUMENT_TYPE_LABELS, DOCUMENT_TYPE_ICONS, DocumentType } from '../types/document';
import './SharedDocumentView.css';

export function SharedDocumentView() {
  const { token } = useParams<{ token: string }>();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [doc, setDoc] = useState<PublicSharedDocument | null>(null);

  useEffect(() => {
    async function loadSharedDoc() {
      if (!token) {
        setError('Invalid secure link.');
        setLoading(false);
        return;
      }
      try {
        const data = await fetchPublicSharedDocument(token);
        setDoc(data);
      } catch (err: any) {
        setError(err.response?.data?.detail || 'This shared link is inactive, expired, or invalid.');
      } finally {
        setLoading(false);
      }
    }
    loadSharedDoc();
  }, [token]);

  const handleDownload = () => {
    if (doc?.download_url) {
      window.open(doc.download_url, '_blank');
    }
  };

  return (
    <div className="shared-view-container">
      <div className="shared-view-card">
        <div className="shared-view-branding">
          <span className="material-symbols-outlined branding-icon">lock</span>
          <h1>VaultPass</h1>
          <p>Secure Shared Document Access</p>
        </div>

        {loading ? (
          <div className="shared-view-loading">
            <div className="spinner" />
            <p>Retrieving secure shared access...</p>
          </div>
        ) : error ? (
          <div className="shared-view-error">
            <span className="material-symbols-outlined error-icon">warning</span>
            <h2>Access Denied</h2>
            <p>{error}</p>
          </div>
        ) : doc ? (
          <div className="shared-view-content">
            <div className="shared-view-document-avatar">
              <span className="material-symbols-outlined">
                {DOCUMENT_TYPE_ICONS[doc.document_type as DocumentType] || 'description'}
              </span>
            </div>

            <div className="shared-view-details">
              <h2>{doc.title}</h2>
              <span className="shared-view-badge">
                {DOCUMENT_TYPE_LABELS[doc.document_type as DocumentType] || doc.document_type}
              </span>
              
              <div className="shared-view-meta-info">
                {doc.expiry_date && (
                  <p>
                    <strong>Expires:</strong> {new Date(doc.expiry_date).toLocaleDateString()}
                  </p>
                )}
                <p>
                  <strong>Shared on:</strong> {new Date(doc.created_at).toLocaleDateString()}
                </p>
              </div>
            </div>

            <button type="button" className="button button-primary shared-view-download-btn" onClick={handleDownload}>
              <span className="material-symbols-outlined">download</span>
              Download Document
            </button>
          </div>
        ) : null}

        <footer className="shared-view-footer">
          <p>This is a secure connection. Shared documents are encrypted and expire automatically.</p>
        </footer>
      </div>
    </div>
  );
}
