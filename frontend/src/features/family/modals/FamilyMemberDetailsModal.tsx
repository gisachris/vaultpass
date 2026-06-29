import { FamilyRelationship } from '../types';

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

  return (
    <div className="documents-modal-overlay" onClick={onClose} style={{ zIndex: 1000 }}>
      <div className="documents-modal-window" onClick={(e) => e.stopPropagation()} style={{ maxWidth: '440px' }}>
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

        <div style={{ padding: '0 24px 24px 24px', display: 'flex', flexDirection: 'column', gap: '20px' }}>
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
              {roleLabel} ({member.relationship})
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

            {member.notes && (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', fontSize: '0.875rem', borderTop: '1px solid #e2e8f0', paddingTop: '8px' }}>
                <span style={{ color: '#64748b', fontSize: '0.75rem', fontWeight: 600, textTransform: 'uppercase' }}>Invitation Notes</span>
                <span style={{ color: '#334155', fontStyle: 'italic' }}>"{member.notes}"</span>
              </div>
            )}
          </div>

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
              transition: 'all 0.2s'
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
  );
}
