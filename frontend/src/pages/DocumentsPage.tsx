import { DragEvent, FormEvent, useRef, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { toast } from 'sonner';
import { deleteDocument, downloadDocumentUrl, updateDocument } from '../services/documentService';
import { useDocuments } from '../hooks/useDocuments';
import { DocumentModel, DOCUMENT_CATEGORY_BUTTONS } from '../types/document';
import { DocumentRow } from '../components/documents/DocumentRow';
import { UploadDocumentModal } from '../components/documents/UploadDocumentModal';
import { DocumentDetailsModal } from '../components/documents/DocumentDetailsModal';
import { EditDocumentModal } from '../components/documents/EditDocumentModal';
import './DocumentsPage.css';

export function DocumentsPage() {
  const navigate = useNavigate();
  const fileInputRef = useRef<HTMLInputElement | null>(null);
  const [selectedFile, setSelectedFile] = useState<File | null>(null);
  const [selectedDocument, setSelectedDocument] = useState<DocumentModel | null>(null);
  const [detailsOpen, setDetailsOpen] = useState(false);
  const [editOpen, setEditOpen] = useState(false);
  const [uploadOpen, setUploadOpen] = useState(false);
  const [confirmDeleteOpen, setConfirmDeleteOpen] = useState(false);
  const [deleting, setDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState('');
  const [pendingDelete, setPendingDelete] = useState<DocumentModel | null>(null);
  const [dragActive, setDragActive] = useState(false);

  const {
    visibleDocuments,
    total,
    page,
    pageCount,
    searchInput,
    category,
    sortNewestFirst,
    loading,
    error,
    errorStatus,
    setPage,
    setSearchInput,
    setCategory,
    toggleSortDirection,
    refresh,
  } = useDocuments();

  const handleOpenFilePicker = () => {
    fileInputRef.current?.click();
  };

  const handleFileSelected = (file: File | null) => {
    if (!file) {
      return;
    }
    setSelectedFile(file);
    setUploadOpen(true);
  };

  const handleFileInputChange = (event: FormEvent<HTMLInputElement>) => {
    const file = event.currentTarget.files?.[0] ?? null;
    handleFileSelected(file);
    event.currentTarget.value = '';
  };

  const handleDragOver = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragActive(true);
  };

  const handleDragLeave = () => {
    setDragActive(false);
  };

  const handleDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragActive(false);
    const file = event.dataTransfer.files?.[0] ?? null;
    handleFileSelected(file);
  };

  const handleUploadSuccess = async () => {
    setUploadOpen(false);
    setSelectedFile(null);
    await refresh();
    toast.success('Document uploaded successfully.');
  };

  const handleViewDetails = (document: DocumentModel) => {
    setSelectedDocument(document);
    setDetailsOpen(true);
  };

  const handleEditDocument = (document: DocumentModel) => {
    setSelectedDocument(document);
    setEditOpen(true);
  };

  const handleDownloadDocument = async (document: DocumentModel) => {
    try {
      const url = await downloadDocumentUrl(document.id);
      window.open(url, '_blank');
    } catch (err) {
      toast.error('Failed to prepare document download.');
      if ((err as any)?.response?.status === 401) {
        navigate('/login');
      }
    }
  };

  const requestDeleteDocument = (document: DocumentModel) => {
    setPendingDelete(document);
    setDeleteError('');
    setConfirmDeleteOpen(true);
  };

  const cancelDeleteDocument = () => {
    setConfirmDeleteOpen(false);
    setPendingDelete(null);
    setDeleteError('');
  };

  const confirmDeleteDocument = async () => {
    if (!pendingDelete) {
      return;
    }

    setDeleting(true);
    setDeleteError('');

    try {
      await deleteDocument(pendingDelete.id);
      await refresh();
      toast.success('Document deleted successfully.');
      setPendingDelete(null);
      setConfirmDeleteOpen(false);
      setSelectedDocument(null);
      setDetailsOpen(false);
      setEditOpen(false);
    } catch (err) {
      setDeleteError('Unable to delete document.');
      if ((err as any)?.response?.status === 401) {
        navigate('/login');
      }
    } finally {
      setDeleting(false);
    }
  };

  const handleUpdateDocument = async (documentId: string, payload: { title: string; document_type: string; description?: string; expiry_date?: string }) => {
    try {
      if (!selectedDocument) {
        return;
      }
      await updateDocument(documentId, {
        title: payload.title,
        document_type: payload.document_type as any,
        description: payload.description,
        expiry_date: payload.expiry_date,
      });
      await refresh();
      toast.success('Document updated successfully.');
      setEditOpen(false);
      setDetailsOpen(false);
      setSelectedDocument(null);
    } catch (err) {
      toast.error('Unable to update document.');
      if ((err as any)?.response?.status === 401) {
        navigate('/login');
      }
    }
  };

  const activeCount = visibleDocuments.length;
  const showEmptyState = !loading && activeCount === 0;

  return (
    <div className="documents-page">
      <nav className="documents-sidebar">
        <div className="documents-logo">
          <span>VaultPass</span>
          <span>Secure Document Vault</span>
        </div>

        <div className="documents-sidebar-cta">
          <button type="button" className="button button-primary" onClick={handleOpenFilePicker}>
            <span className="material-symbols-outlined">upload_file</span>
            Upload Document
          </button>
        </div>

        <div className="documents-sidebar-links">
          <Link to="/" className="documents-sidebar-link">
            <span className="material-symbols-outlined">dashboard</span>
            <span>Dashboard</span>
          </Link>
          <Link to="/documents" className="documents-sidebar-link documents-sidebar-link--active">
            <span className="material-symbols-outlined">description</span>
            <span>Documents</span>
          </Link>
          <Link to="/trusted-contacts" className="documents-sidebar-link">
            <span className="material-symbols-outlined">group</span>
            <span>Trusted Contacts</span>
          </Link>
          <button type="button" className="documents-sidebar-link documents-sidebar-link--disabled">
            <span className="material-symbols-outlined">share</span>
            <span>Shared Access</span>
          </button>
        </div>

        <div className="documents-sidebar-footer">
          <button type="button" className="documents-sidebar-link documents-sidebar-link--disabled">
            <span className="material-symbols-outlined">notifications</span>
            <span>Notifications</span>
          </button>
          <button type="button" className="documents-sidebar-link documents-sidebar-link--disabled">
            <span className="material-symbols-outlined">settings</span>
            <span>Settings</span>
          </button>
        </div>
      </nav>

      <div className="documents-main">
        <header className="documents-topbar">
          <div className="documents-search">
            <span className="material-symbols-outlined">search</span>
            <input
              type="text"
              value={searchInput}
              onChange={(event) => setSearchInput(event.target.value)}
              placeholder="Search VaultPass..."
              aria-label="Search documents"
            />
          </div>
          <div className="documents-topbar-actions">
            <button type="button" className="icon-button" aria-label="Help">
              <span className="material-symbols-outlined">help_outline</span>
            </button>
            <div className="documents-profile">
              <img
                src="https://images.unsplash.com/photo-1502685104226-ee32379fefbe?auto=format&fit=crop&w=256&q=80"
                alt="User profile"
              />
            </div>
          </div>
        </header>

        <main className="documents-canvas">
          <section className="documents-headline">
            <div>
              <h1>My Documents</h1>
              <p>Manage, organize, and securely store your essential records.</p>
            </div>
          </section>

          <section
            className={`documents-dropzone ${dragActive ? 'documents-dropzone--active' : ''}`}
            onClick={handleOpenFilePicker}
            onDragOver={handleDragOver}
            onDragLeave={handleDragLeave}
            onDrop={handleDrop}
          >
            <div className="documents-dropzone-icon">
              <span className="material-symbols-outlined">cloud_upload</span>
            </div>
            <div className="documents-dropzone-copy">
              <span>Drag & drop files here</span>
              <span>or click to browse from your computer (PDF, JPEG, PNG)</span>
            </div>
            <input
              ref={fileInputRef}
              type="file"
              accept="application/pdf,image/png,image/jpeg"
              hidden
              onChange={handleFileInputChange}
            />
          </section>

          <section className="documents-filter-bar">
            <div className="documents-filter-options">
              {DOCUMENT_CATEGORY_BUTTONS.map((filter) => (
                <button
                  key={filter.key}
                  type="button"
                  className={`documents-filter-button ${category === filter.key ? 'documents-filter-button--active' : ''}`}
                  onClick={() => setCategory(filter.key)}
                >
                  {filter.label}
                </button>
              ))}
            </div>
            <div className="documents-filter-actions">
              <button type="button" className="documents-filter-action" onClick={toggleSortDirection}>
                <span className="material-symbols-outlined">sort</span>
                Sort by Date
              </button>
              <button
                type="button"
                className="documents-filter-action"
                onClick={() => toast('More filters are coming soon.')}
              >
                <span className="material-symbols-outlined">filter_list</span>
                More Filters
              </button>
            </div>
          </section>

          {error && (
            <div className="documents-error">
              {errorStatus === 401
                ? 'Session expired. Redirecting to login…'
                : error || 'Unable to load your documents.'}
            </div>
          )}

          <section className="documents-list-wrapper">
            {loading ? (
              <div className="documents-skeleton-list">
                {[1, 2, 3].map((index) => (
                  <div key={index} className="documents-skeleton-row">
                    <div className="documents-skeleton-icon" />
                    <div className="documents-skeleton-copy">
                      <div className="documents-skeleton-line documents-skeleton-line--short" />
                      <div className="documents-skeleton-line documents-skeleton-line--tiny" />
                    </div>
                    <div className="documents-skeleton-actions" />
                  </div>
                ))}
              </div>
            ) : showEmptyState ? (
              <div className="documents-empty-state">
                <h2>No documents available</h2>
                <p>Upload a file or change your search to find stored documents.</p>
              </div>
            ) : (
              visibleDocuments.map((document) => (
                <DocumentRow
                  key={document.id}
                  document={document}
                  onViewDetails={handleViewDetails}
                  onDownload={handleDownloadDocument}
                  onEdit={handleEditDocument}
                  onDelete={requestDeleteDocument}
                />
              ))
            )}
          </section>

          <section className="documents-pagination">
            <div className="documents-pagination-summary">
              Showing {activeCount} of {total} documents
            </div>
            <div className="documents-pagination-actions">
              <button
                type="button"
                className="button button-secondary"
                disabled={page === 1}
                onClick={() => setPage(page - 1)}
              >
                Previous
              </button>
              <button
                type="button"
                className="button button-secondary"
                disabled={page >= pageCount}
                onClick={() => setPage(page + 1)}
              >
                Next
              </button>
            </div>
          </section>
        </main>
      </div>

      <UploadDocumentModal
        open={uploadOpen}
        file={selectedFile}
        onClose={() => {
          setUploadOpen(false);
          setSelectedFile(null);
        }}
        onUploadSuccess={handleUploadSuccess}
      />

      <DocumentDetailsModal
        open={detailsOpen}
        document={selectedDocument}
        onClose={() => setDetailsOpen(false)}
        onDownload={() => selectedDocument && handleDownloadDocument(selectedDocument)}
        onEdit={() => {
          if (selectedDocument) {
            handleEditDocument(selectedDocument);
          }
        }}
        onDelete={() => {
          if (selectedDocument) {
            requestDeleteDocument(selectedDocument);
          }
        }}
      />

      {confirmDeleteOpen && pendingDelete && (
        <div className="documents-modal-overlay" onClick={cancelDeleteDocument}>
          <div className="documents-modal-window" onClick={(event) => event.stopPropagation()}>
            <div className="documents-modal-header">
              <div>
                <h2>Delete document</h2>
                <p>Confirm before removing this document from your vault.</p>
              </div>
              <button type="button" className="documents-modal-close" onClick={cancelDeleteDocument} aria-label="Close delete confirmation dialog">
                ×
              </button>
            </div>

            <div className="documents-modal-body">
              <div className="documents-modal-row documents-modal-row--full">
                <p>
                  Are you sure you want to delete <strong>{pendingDelete.title}</strong>? This action cannot be undone.
                </p>
              </div>
              {deleteError && <div className="documents-modal-error">{deleteError}</div>}
            </div>

            <div className="documents-modal-actions">
              <button type="button" className="button button-secondary" onClick={cancelDeleteDocument} disabled={deleting}>
                Cancel
              </button>
              <button type="button" className="button button-primary" onClick={confirmDeleteDocument} disabled={deleting}>
                {deleting ? 'Deleting…' : 'Delete document'}
              </button>
            </div>
          </div>
        </div>
      )}

      <EditDocumentModal
        open={editOpen}
        document={selectedDocument}
        onClose={() => setEditOpen(false)}
        onSave={(payload) => {
          if (selectedDocument) {
            return handleUpdateDocument(selectedDocument.id, payload);
          }
          return Promise.resolve();
        }}
      />
    </div>
  );
}
