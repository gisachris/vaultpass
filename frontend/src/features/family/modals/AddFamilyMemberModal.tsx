import React, { useState } from 'react';
import { RelationshipType } from '../types';

interface AddFamilyMemberModalProps {
  onClose: () => void;
  onInvite: (email: string, relationship: RelationshipType, notes: string) => Promise<void>;
}

export function AddFamilyMemberModal({ onClose, onInvite }: AddFamilyMemberModalProps) {
  const [email, setEmail] = useState('');
  const [relationship, setRelationship] = useState<RelationshipType | ''>('');
  const [notes, setNotes] = useState('');
  const [loading, setLoading] = useState(false);
  const [err, setErr] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !relationship) return;

    setLoading(true);
    setErr(null);
    try {
      await onInvite(email, relationship, notes);
      onClose();
    } catch (e: any) {
      setErr(e.message || 'An error occurred while sending invitation.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="documents-modal-overlay" onClick={onClose} style={{ zIndex: 1000 }}>
      <div className="documents-modal-window" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '480px' }}>
        <div className="documents-modal-header">
          <div>
            <h2>Add Family Member</h2>
            <p style={{ marginTop: '4px', fontSize: '0.875rem', color: '#64748b' }}>
              Invite a trusted contact to your secure family workspace.
            </p>
          </div>
          <button
            type="button"
            className="documents-modal-close"
            onClick={onClose}
            aria-label="Close invite modal"
          >
            <span className="material-symbols-outlined">close</span>
          </button>
        </div>

        <form className="documents-modal-body" onSubmit={handleSubmit} style={{ padding: '0 24px 24px 24px' }}>
          <div className="documents-modal-row" style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#1e293b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Email Address
            </label>
            <div style={{ position: 'relative' }}>
              <span className="material-symbols-outlined" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }}>
                mail
              </span>
              <input
                type="email"
                placeholder="e.g. name@family.com"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                required
                style={{ width: 'full', padding: '10px 12px 10px 40px', border: '1px solid #e2e8f0', borderRadius: '8px', outline: 'none' }}
              />
            </div>
          </div>

          <div className="documents-modal-row" style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
            <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#1e293b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
              Relationship
            </label>
            <div style={{ position: 'relative' }}>
              <span className="material-symbols-outlined" style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b' }}>
                group
              </span>
              <select
                value={relationship}
                onChange={(e) => setRelationship(e.target.value as RelationshipType)}
                required
                style={{ width: '100%', padding: '10px 40px 10px 40px', border: '1px solid #e2e8f0', borderRadius: '8px', outline: 'none', appearance: 'none', background: 'transparent' }}
              >
                <option value="" disabled>Select relationship</option>
                <option value="SPOUSE">Spouse</option>
                <option value="PARENT">Parent</option>
                <option value="CHILD">Child</option>
                <option value="SIBLING">Sibling</option>
                <option value="PARTNER">Partner</option>
                <option value="OTHER">Other / Trusted Contact</option>
              </select>
              <span className="material-symbols-outlined" style={{ position: 'absolute', right: '12px', top: '50%', transform: 'translateY(-50%)', color: '#64748b', pointerEvents: 'none' }}>
                expand_more
              </span>
            </div>
          </div>

          <div className="documents-modal-row" style={{ display: 'flex', flexDirection: 'column', gap: '8px', marginBottom: '16px' }}>
            <div style={{ display: 'flex', justifyContent: 'between', alignItems: 'center' }}>
              <label style={{ fontSize: '0.75rem', fontWeight: 600, color: '#1e293b', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                Optional Message
              </label>
              <span style={{ fontSize: '10px', color: '#64748b' }}>150 chars max</span>
            </div>
            <textarea
              maxLength={150}
              placeholder="Tell them why you are inviting them..."
              value={notes}
              onChange={(e) => setNotes(e.target.value)}
              rows={3}
              style={{ width: '100%', padding: '10px 12px', border: '1px solid #e2e8f0', borderRadius: '8px', outline: 'none', resize: 'none' }}
            />
          </div>

          <div style={{ padding: '12px', backgroundColor: '#e2e8f0', borderRadius: '8px', display: 'flex', gap: '12px', alignItems: 'start', border: '1px solid #cbd5e1', marginBottom: '20px' }}>
            <span className="material-symbols-outlined" style={{ color: '#1e293b', fontSize: '1.25rem', marginTop: '2px' }}>
              verified_user
            </span>
            <p style={{ fontSize: '0.75rem', color: '#1e293b', margin: 0, lineHeight: 1.5 }}>
              Security Notice: Family members will have view access to shared documents only after confirming their identity. You can revoke access at any time.
            </p>
          </div>

          {err && <div className="documents-modal-error" style={{ marginBottom: '16px' }}>{err}</div>}

          <div className="documents-modal-actions" style={{ padding: 0 }}>
            <button
              type="submit"
              disabled={loading}
              className="button button-primary"
              style={{ flex: 1, height: '44px', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '8px' }}
            >
              {loading ? (
                <>
                  <span className="material-symbols-outlined animate-spin">progress_activity</span>
                  Sending...
                </>
              ) : (
                <>
                  Send Invitation
                  <span className="material-symbols-outlined">send</span>
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
        </form>
      </div>
    </div>
  );
}
