import { useState, useEffect } from 'react';
import { FamilyRelationship, getRelativeRelationshipLabel } from '../types';
import { fetchGuardianDocuments } from '../api/familyService';
import { DocumentModel } from '../../../types/document';
import { downloadDocumentUrl, triggerFileDownload } from '../../../services/documentService';
import { DocumentPreviewModal } from '../../../components/documents/DocumentPreviewModal';
import { toast } from 'sonner';

interface FamilyMemberDetailsModalProps {
  member: FamilyRelationship;
  currentUserEmail?: string;
  onClose: () => void;
  onRemove: (relationshipId: string) => void;
}

export function FamilyMemberDetailsModal({
  member,
  currentUserEmail,
  onClose,
  onRemove
}: FamilyMemberDetailsModalProps) {
  const [documents, setDocuments] = useState<DocumentModel[]>([]);
  const [loadingDocs, setLoadingDocs] = useState(false);
  const [previewingDoc, setPreviewingDoc] = useState<{ id: string; title: string } | null>(null);
  const [downloading, setDownloading] = useState<string | null>(null);

  // Determine if showing guardian or dependent details based on current user
  const isDependentView = member.guardian?.email === currentUserEmail;
  const userShow = isDependentView ? member.dependent : member.guardian;
  const roleLabel = isDependentView ? 'Dependent' : 'Guardian';
  
  const initials = userShow?.full_name
    ? userShow.full_name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : 'U';

  const joinedDate = new Date(member.created_at).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });

  useEffect(() => {
    if (isDependentView && userShow) {
      setLoadingDocs(true);
      fetchGuardianDocuments({ dependent_name: userShow.full_name })
        .then((res) => {
          const group = res.find((g) => g.dependent_id === userShow.id);
          if (group) {
            setDocuments(group.documents);
          }
        })
        .catch((err) => {
          console.error('Failed to load family documents', err);
        })
        .finally(() => {
          setLoadingDocs(false);
        });
    }
  }, [isDependentView, userShow]);

  const handleDownload = async (docId: string, title: string) => {
    setDownloading(docId);
    try {
      const url = await downloadDocumentUrl(docId);
      triggerFileDownload(title, url);
    } catch {
      toast.error('Failed to download document.');
    } finally {
      setDownloading(null);
    }
  };

  return (
    <>
      <div className="documents-modal-overlay" onClick={onClose} style={{ zIndex: 1000 }}>
        <div className="documents-modal-window" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '480px', maxHeight: '90vh', display: 'flex', flexDirection: 'column' }}>
          <div className="documents-modal-header" style={{ paddingBottom: '12px' }}>
            <h2>Family Profile</h2>
            <button
              type="button"
              className="documents-modal-close"
              onClick={onClose}
              aria-label="Close details modal"
            >
              <span className="material-symbols-outlined">close</span>
            </button>
          </div>

          <div style={{ padding: '0 24px 24px 24px', display: 'flex', flexDirection: 'column', gap: '20px', overflowY: 'auto', flex: 1 }}>
            {/* Avatar and Name */}
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '12px', textAlign: 'center' }}>
              <div style={{
                width: '80px',
                height: '80px',
                borderRadius: '50%',
                backgroundColor: '#162839',
                color: '#ffffff',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '1.75rem',
                fontWeight: 700,
                boxShadow: '0 4px 10px rgba(0,0,0,0.06)'
              }}>
                {initials}
              </div>
              <div>
                <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#0f172a', margin: 0 }}>
                  {userShow?.full_name || 'Family Member'}
                </h3>
                <p style={{ fontSize: '0.875rem', color: '#64748b', margin: '4px 0 0 0' }}>
                  {userShow?.email || ''}
                </p>
              </div>
              <span style={{
                display: 'inline-block',
                padding: '4px 12px',
                borderRadius: '9999px',
                backgroundColor: '#e1e3e4',
                color: '#5c5f60',
                fontSize: '0.75rem',
                fontWeight: 600,
                textTransform: 'uppercase'
              }}>
                {roleLabel} ({getRelativeRelationshipLabel(member, currentUserEmail)})
              </span>
            </div>

            {/* Details Card */}
            <div style={{ backgroundColor: '#f8fafc', padding: '16px', borderRadius: '12px', display: 'flex', flexDirection: 'column', gap: '12px', border: '1px solid #e2e8f0' }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
                <span style={{ color: '#64748b' }}>Status</span>
                <span style={{
                  color: member.status === 'ACCEPTED' ? '#2d6a4f' : '#b58900',
                  fontWeight: 600,
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}>
                  {member.status === 'ACCEPTED' ? 'Active' : 'Pending'}
                  <span style={{
                    width: '6px',
                    height: '6px',
                    borderRadius: '50%',
                    backgroundColor: member.status === 'ACCEPTED' ? '#2d6a4f' : '#b58900'
                  }} />
                </span>
              </div>

              <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
                <span style={{ color: '#64748b' }}>Member Since</span>
                <span style={{ color: '#0f172a', fontWeight: 500 }}>{joinedDate}</span>
              </div>

              {isDependentView && (
                <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.875rem' }}>
                  <span style={{ color: '#64748b' }}>Accessible Documents</span>
                  <span style={{ color: '#0f172a', fontWeight: 500 }}>{loadingDocs ? 'Loading...' : documents.length}</span>
                </div>
              )}
            </div>

            {/* Dependent's Accessible Documents List */}
            {isDependentView && member.status === 'ACCEPTED' && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                <h4 style={{ fontSize: '0.875rem', fontWeight: 600, color: '#162839', margin: '0 0 4px 0', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  Accessible Documents
                </h4>
                {loadingDocs ? (
                  <div style={{ display: 'flex', justifyContent: 'center', padding: '16px' }}>
                    <div className="spinner" style={{ width: '24px', height: '24px' }} />
                  </div>
                ) : documents.length === 0 ? (
                  <p style={{ fontSize: '0.875rem', color: '#64748b', fontStyle: 'italic', margin: 0 }}>
                    No visible documents available.
                  </p>
                ) : (
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', maxHeight: '200px', overflowY: 'auto', paddingRight: '4px' }}>
                    {documents.map((doc) => (
                      <div key={doc.id} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '10px', backgroundColor: '#f8fafc', borderRadius: '8px', border: '1px solid #e2e8f0' }}>
                        <div style={{ minWidth: 0, flex: 1, paddingRight: '8px' }}>
                          <p style={{ fontSize: '0.875rem', fontWeight: 600, color: '#0f172a', margin: 0, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>
                            {doc.title}
                          </p>
                          <p style={{ fontSize: '0.75rem', color: '#64748b', margin: 0 }}>
                            {doc.document_type}
                          </p>
                        </div>
                        <div style={{ display: 'flex', gap: '6px', flexShrink: 0 }}>
                          <button
                            type="button"
                            onClick={() => setPreviewingDoc({ id: doc.id, title: doc.title })}
                            style={{ padding: '4px', background: 'transparent', border: 'none', color: '#2c3e50', cursor: 'pointer' }}
                            title="Preview Document"
                          >
                            <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>visibility</span>
                          </button>
                          <button
                            type="button"
                            onClick={() => handleDownload(doc.id, doc.title)}
                            disabled={downloading === doc.id}
                            style={{ padding: '4px', background: 'transparent', border: 'none', color: '#2c3e50', cursor: 'pointer' }}
                            title="Download Document"
                          >
                            <span className="material-symbols-outlined" style={{ fontSize: '20px' }}>
                              {downloading === doc.id ? 'progress_activity' : 'download'}
                            </span>
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            )}

            {/* Remove Action Button */}
            <button
              type="button"
              onClick={() => onRemove(member.id)}
              style={{
                width: '100%',
                padding: '12px',
                backgroundColor: 'transparent',
                border: '1px solid #f87171',
                color: '#ef4444',
                borderRadius: '8px',
                fontWeight: 600,
                fontSize: '0.875rem',
                cursor: 'pointer',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                gap: '8px',
                transition: 'all 0.2s',
                marginTop: 'auto'
              }}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = '#fef2f2';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = 'transparent';
              }}
            >
              <span className="material-symbols-outlined">no_accounts</span>
              Remove Relationship
            </button>
          </div>
        </div>
      </div>

      {previewingDoc && (
        <DocumentPreviewModal
          documentId={previewingDoc.id}
          documentName={previewingDoc.title}
          allowDownload={true}
          onClose={() => setPreviewingDoc(null)}
        />
      )}
    </>
  );
}
