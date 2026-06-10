import { useEffect, useState, useMemo } from 'react';
import { useLocation } from 'react-router-dom';
import { toast } from 'sonner';
import {
  fetchDocumentShares,
  deleteDocumentShare,
  revokeDocumentShare,
  activateDocumentShare,
  DocumentShareModel
} from '../services/documentShareService';
import { fetchDocuments } from '../services/documentService';
import { fetchTrustedContacts } from '../services/trustedContactsService';
import { DocumentModel } from '../types/document';
import { TrustedContactModel } from '../types/trustedContact';
import { AppSidebar } from '../components/ui/AppSidebar';
import { UserProfileMenu } from '../components/profile/UserProfileMenu';
import './SharedAccessPage.css';

export function SharedAccessPage() {
  const location = useLocation();
  const [shares, setShares] = useState<DocumentShareModel[]>([]);
  const [documents, setDocuments] = useState<DocumentModel[]>([]);
  const [contacts, setContacts] = useState<TrustedContactModel[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadData = async () => {
    setLoading(true);
    setError('');
    try {
      // Fetch shares, docs, and contacts concurrently
      const [sharesData, docsResult, contactsResult] = await Promise.all([
        fetchDocumentShares(),
        fetchDocuments(1, 100), // Fetch up to 100 documents for mapping
        fetchTrustedContacts(1, 100), // Fetch up to 100 contacts for mapping
      ]);

      setShares(sharesData);
      setDocuments(docsResult.items);
      setContacts(contactsResult.items);
    } catch (err: any) {
      setError('Failed to retrieve sharing logs.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadData();
  }, []);

  // Lookups mapping IDs to object titles
  const docLookup = useMemo(() => {
    const map: Record<string, string> = {};
    documents.forEach((d) => {
      map[d.id] = d.title;
    });
    return map;
  }, [documents]);

  const contactLookup = useMemo(() => {
    const map: Record<string, string> = {};
    contacts.forEach((c) => {
      map[c.id] = c.full_name;
    });
    return map;
  }, [contacts]);

  const handleToggleActive = async (share: DocumentShareModel) => {
    try {
      if (share.is_active) {
        await revokeDocumentShare(share.id);
        toast.success('Share link successfully revoked.');
      } else {
        await activateDocumentShare(share.id);
        toast.success('Share link successfully reactivated.');
      }
      await loadData();
    } catch (err: any) {
      toast.error('Unable to update share configuration.');
    }
  };

  const handleDeleteShare = async (shareId: string) => {
    if (!window.confirm('Are you sure you want to delete this shared link? Access will be immediately lost.')) {
      return;
    }
    try {
      await deleteDocumentShare(shareId);
      toast.success('Shared link deleted successfully.');
      await loadData();
    } catch (err: any) {
      toast.error('Unable to delete sharing record.');
    }
  };

  const copyLinkToClipboard = (accessToken: string) => {
    const link = `${window.location.origin}/shared/${accessToken}`;
    navigator.clipboard.writeText(link);
    toast.success('Share link copied to clipboard!');
  };

  return (
    <div className="shares-page">
      <AppSidebar />

      <div className="shares-main">
        <header className="shares-topbar">
          <div className="shares-topbar-title">
            <h1>Shared Access Logs</h1>
          </div>
          <UserProfileMenu variant="topbar" />
        </header>

        <main className="shares-canvas">
          <section className="shares-headline">
            <p>Monitor, configure, and revoke access keys you have issued to trusted contacts.</p>
          </section>

          {loading ? (
            <div className="shares-empty-state">
              <p>Loading shared access logs...</p>
            </div>
          ) : error ? (
            <div className="shares-error">{error}</div>
          ) : shares.length === 0 ? (
            <div className="shares-empty-state">
              <h2>No document shares yet</h2>
              <p>Go to your Documents list, click options, and select "Share" to generate secure access links.</p>
            </div>
          ) : (
            <div className="shares-table-container">
              <table className="shares-table">
                <thead>
                  <tr>
                    <th>Document</th>
                    <th>Shared With</th>
                    <th>Expires At</th>
                    <th>Last Accessed</th>
                    <th>Status</th>
                    <th>Share Link</th>
                    <th>Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {shares.map((share) => {
                    const isExpired = share.expires_at ? new Date(share.expires_at) < new Date() : false;
                    const statusText = !share.is_active ? 'Revoked' : isExpired ? 'Expired' : 'Active';
                    const statusClass = !share.is_active ? 'status--revoked' : isExpired ? 'status--expired' : 'status--active';

                    return (
                      <tr key={share.id}>
                        <td>
                          <strong>{docLookup[share.document_id] || 'Loading...'}</strong>
                        </td>
                        <td>{contactLookup[share.contact_id] || 'Loading...'}</td>
                        <td>{share.expires_at ? new Date(share.expires_at).toLocaleDateString() : 'Never'}</td>
                        <td>{share.last_accessed_at ? new Date(share.last_accessed_at).toLocaleString() : 'Never'}</td>
                        <td>
                          <span className={`status-badge ${statusClass}`}>{statusText}</span>
                        </td>
                        <td>
                          <div className="share-link-copy-row">
                            <input
                              type="text"
                              readOnly
                              value={`${window.location.origin}/shared/${share.access_token}`}
                            />
                            <button
                              type="button"
                              className="copy-btn"
                              onClick={() => copyLinkToClipboard(share.access_token)}
                              title="Copy to clipboard"
                            >
                              <span className="material-symbols-outlined">content_copy</span>
                            </button>
                          </div>
                        </td>
                        <td>
                          <div className="shares-action-buttons">
                            <button
                              type="button"
                              className={`action-btn toggle-btn ${share.is_active ? 'btn--revoke' : 'btn--activate'}`}
                              onClick={() => handleToggleActive(share)}
                              disabled={isExpired}
                            >
                              {share.is_active ? 'Revoke' : 'Activate'}
                            </button>
                            <button
                              type="button"
                              className="action-btn delete-btn"
                              onClick={() => handleDeleteShare(share.id)}
                            >
                              Delete
                            </button>
                          </div>
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
