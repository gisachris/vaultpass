import { useEffect, useRef, useState } from 'react';
import { previewDocumentUrl, downloadDocumentUrl, triggerFileDownload } from '../../services/documentService';
import { DocumentModel } from '../../types/document';
import './DocumentPreviewModal.css';

interface DocumentPreviewModalProps {
  document?: DocumentModel | null;
  /** Optional: override the document_id to use (e.g. for shared documents) */
  documentId?: string;
  documentName?: string;
  mimeType?: string;
  allowDownload?: boolean;
  onClose: () => void;
}

type LoadState = 'loading' | 'loaded' | 'error';
type ErrorKind = 'forbidden' | 'not_found' | 'unavailable' | 'generic';

function getErrorMessage(kind: ErrorKind): string {
  switch (kind) {
    case 'forbidden':
      return 'You do not have permission to view this document.';
    case 'not_found':
      return 'This document could not be found.';
    case 'unavailable':
      return 'The preview service is currently unavailable. Please try again later.';
    default:
      return 'Unable to load the document preview.';
  }
}

function classifyError(status: number | undefined): ErrorKind {
  if (status === 403) return 'forbidden';
  if (status === 404) return 'not_found';
  if (status === 500 || status === 503) return 'unavailable';
  return 'generic';
}

function isImage(mime: string): boolean {
  return ['image/png', 'image/jpeg', 'image/jpg', 'image/webp', 'image/gif'].includes(mime.toLowerCase());
}

function isPdf(mime: string): boolean {
  return mime.toLowerCase() === 'application/pdf';
}

export function DocumentPreviewModal({
  document,
  documentId,
  documentName,
  mimeType,
  allowDownload = true,
  onClose,
}: DocumentPreviewModalProps) {
  const resolvedId = documentId ?? document?.id ?? '';
  const resolvedName = documentName ?? document?.file_name ?? 'document';
  const resolvedMime = mimeType ?? document?.mime_type ?? '';

  const [previewUrl, setPreviewUrl] = useState<string>('');
  const [loadState, setLoadState] = useState<LoadState>('loading');
  const [errorKind, setErrorKind] = useState<ErrorKind>('generic');
  const [downloading, setDownloading] = useState(false);

  const overlayRef = useRef<HTMLDivElement>(null);

  // Fetch signed preview URL
  useEffect(() => {
    if (!resolvedId) return;
    let cancelled = false;

    setLoadState('loading');
    setPreviewUrl('');

    previewDocumentUrl(resolvedId)
      .then((url) => {
        if (!cancelled) {
          setPreviewUrl(url);
          setLoadState('loaded');
        }
      })
      .catch((err) => {
        if (!cancelled) {
          setErrorKind(classifyError(err?.response?.status));
          setLoadState('error');
        }
      });

    return () => { cancelled = true; };
  }, [resolvedId]);

  // Close on Escape
  useEffect(() => {
    const handler = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [onClose]);

  const handleDownload = async () => {
    if (downloading) return;
    setDownloading(true);
    try {
      const url = await downloadDocumentUrl(resolvedId);
      triggerFileDownload(resolvedName, url);
    } catch {
      // error is handled by toast in parent or silently
    } finally {
      setDownloading(false);
    }
  };

  const handleOverlayClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === overlayRef.current) onClose();
  };

  const canPreview = loadState === 'loaded' && (isPdf(resolvedMime) || isImage(resolvedMime));
  const isUnsupported = loadState === 'loaded' && !isPdf(resolvedMime) && !isImage(resolvedMime);

  return (
    <div className="dpm-overlay" ref={overlayRef} onClick={handleOverlayClick} role="dialog" aria-modal="true" aria-label={`Preview: ${resolvedName}`}>
      <div className="dpm-sheet">
        {/* Header */}
        <div className="dpm-header">
          <div className="dpm-header-info">
            <span className="material-symbols-outlined dpm-header-icon">
              {isPdf(resolvedMime) ? 'picture_as_pdf' : isImage(resolvedMime) ? 'image' : 'description'}
            </span>
            <div>
              <p className="dpm-header-name" title={resolvedName}>{resolvedName}</p>
              <p className="dpm-header-mime">{resolvedMime || 'Document'}</p>
            </div>
          </div>
          <div className="dpm-header-actions">
            {allowDownload && loadState !== 'error' && (
              <button
                type="button"
                className="dpm-btn dpm-btn--download"
                onClick={handleDownload}
                disabled={downloading}
                aria-label="Download document"
              >
                <span className="material-symbols-outlined">{downloading ? 'hourglass_top' : 'download'}</span>
                {downloading ? 'Preparing…' : 'Download'}
              </button>
            )}
            <button type="button" className="dpm-btn dpm-btn--close" onClick={onClose} aria-label="Close preview">
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>
        </div>

        {/* Body */}
        <div className="dpm-body">
          {loadState === 'loading' && (
            <div className="dpm-state dpm-state--loading">
              <div className="dpm-skeleton dpm-skeleton--title" />
              <div className="dpm-skeleton dpm-skeleton--content" />
              <div className="dpm-skeleton dpm-skeleton--footer" />
              <p className="dpm-loading-label">Preparing secure preview…</p>
            </div>
          )}

          {loadState === 'error' && (
            <div className="dpm-state dpm-state--error">
              <span className="material-symbols-outlined dpm-state-icon">error_outline</span>
              <h3>Preview unavailable</h3>
              <p>{getErrorMessage(errorKind)}</p>
              <button type="button" className="dpm-btn dpm-btn--primary" onClick={onClose}>
                Close
              </button>
            </div>
          )}

          {isUnsupported && (
            <div className="dpm-state dpm-state--unsupported">
              <span className="material-symbols-outlined dpm-state-icon">file_present</span>
              <h3>Preview not supported</h3>
              <p>This file type cannot be previewed in your browser.</p>
              {allowDownload && (
                <button
                  type="button"
                  className="dpm-btn dpm-btn--primary"
                  onClick={handleDownload}
                  disabled={downloading}
                >
                  <span className="material-symbols-outlined">download</span>
                  {downloading ? 'Preparing…' : 'Download file'}
                </button>
              )}
            </div>
          )}

          {canPreview && isPdf(resolvedMime) && (
            <iframe
              className="dpm-viewer dpm-viewer--pdf"
              src={previewUrl}
              title={resolvedName}
              aria-label={`PDF preview of ${resolvedName}`}
            />
          )}

          {canPreview && isImage(resolvedMime) && (
            <div className="dpm-viewer dpm-viewer--image-wrapper">
              <img
                src={previewUrl}
                alt={resolvedName}
                className="dpm-viewer--image"
              />
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
