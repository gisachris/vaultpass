import { useState } from 'react';
import { FamilyRelationship } from '../types';

interface RemoveRelationshipConfirmationProps {
  relationship: FamilyRelationship;
  currentUserEmail?: string;
  onClose: () => void;
  onConfirm: () => Promise<void>;
}

export function RemoveRelationshipConfirmation({
  relationship,
  currentUserEmail,
  onClose,
  onConfirm
}: RemoveRelationshipConfirmationProps) {
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const isDependentView = relationship.guardian?.email === currentUserEmail;
  const userShow = isDependentView ? relationship.dependent : relationship.guardian;

  const handleConfirm = async () => {
    setLoading(true);
    setErr(null);
    try {
      await onConfirm();
      onClose();
    } catch (e: any) {
      setErr(e.message || 'Failed to remove relationship.');
    } finally {
      setLoading(false);
    }
  };

  const initials = userShow?.full_name
    ? userShow.full_name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : 'U';

  return (
    <div className="documents-modal-overlay" onClick={onClose} style={{ zIndex: 1010 }}>
      <div className="documents-modal-window" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '480px' }}>
        <div style={{ padding: '24px 24px 16px 24px', display: 'flex', gap: '16px', alignItems: 'start' }}>
          <div style={{
            width: '48px',
            height: '48px',
            borderRadius: '50%',
            backgroundColor: '#ffdad6',
            color: '#ba1a1a',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            flexShrink: 0
          }}>
            <span className="material-symbols-outlined" style={{ fontSize: '1.75rem' }}>person_remove</span>
          </div>
          <div style={{ flex: 1 }}>
            <h2 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#162839', margin: '0 0 8px 0' }}>
              Remove Relationship
            </h2>
            <p style={{ fontSize: '0.875rem', color: '#43474c', margin: 0, lineHeight: 1.6 }}>
              Are you sure you want to remove <span style={{ fontWeight: 'bold', color: '#162839' }}>{userShow?.full_name}</span>? This will immediately revoke their automatic access to all shared documents and folders.
            </p>
          </div>
        </div>

        {/* Profile Card */}
        <div style={{ margin: '0 24px 24px 24px', padding: '16px', backgroundColor: '#f5f3f4', borderRadius: '8px', display: 'flex', alignItems: 'center', gap: '16px' }}>
          <div style={{
            width: '40px',
            height: '40px',
            borderRadius: '50%',
            backgroundColor: '#162839',
            color: '#ffffff',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1rem',
            fontWeight: 700
          }}>
            {initials}
          </div>
          <div>
            <div style={{ fontSize: '0.75rem', fontWeight: 600, color: '#162839', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              {isDependentView ? 'Dependent' : 'Guardian'}
            </div>
            <div style={{ fontSize: '0.875rem', color: '#43474c' }}>
              {userShow?.email}
            </div>
          </div>
        </div>

        {/* Warning Alert */}
        <div style={{ margin: '0 24px 24px 24px', padding: '12px', borderRadius: '4px', border: '1px solid #b5890020', backgroundColor: '#b5890008', display: 'flex', gap: '12px', alignItems: 'start' }}>
          <span className="material-symbols-outlined" style={{ color: '#b58900', fontSize: '20px' }}>warning</span>
          <p style={{ fontSize: '0.75rem', color: '#43474c', margin: 0, lineHeight: 1.5 }}>
            This action is <span style={{ fontWeight: 600 }}>irreversible</span>. You will need to re-invite them if you wish to re-establish the relationship in the future.
          </p>
        </div>

        {err && <div className="documents-modal-error" style={{ margin: '0 24px 16px 24px' }}>{err}</div>}

        {/* Actions Footer */}
        <div className="documents-modal-actions" style={{ backgroundColor: '#f5f3f4', padding: '16px 24px' }}>
          <button
            type="button"
            disabled={loading}
            onClick={handleConfirm}
            className="button"
            style={{
              flex: 1,
              height: '44px',
              backgroundColor: '#ba1a1a',
              color: '#ffffff',
              border: 'none',
              borderRadius: '8px',
              fontWeight: 600,
              fontSize: '0.875rem',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              gap: '8px'
            }}
          >
            {loading ? (
              <>
                <span className="material-symbols-outlined animate-spin">progress_activity</span>
                Removing...
              </>
            ) : (
              <>
                Remove Relationship
              </>
            )}
          </button>
          <button
            type="button"
            className="button button-secondary"
            onClick={onClose}
            style={{ flex: 1, height: '44px' }}
          >
            Cancel
          </button>
        </div>
      </div>
    </div>
  );
}
