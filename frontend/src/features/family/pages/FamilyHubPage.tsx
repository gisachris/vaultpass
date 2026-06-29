import { useState, useMemo } from 'react';
import { useFamily } from '../hooks/useFamily';
import { useAuth } from '../../../context/AuthContext';
import { AppSidebar } from '../../../components/ui/AppSidebar';
import { UserProfileMenu } from '../../../components/profile/UserProfileMenu';
import { AddFamilyMemberModal } from '../modals/AddFamilyMemberModal';
import { FamilyMemberDetailsModal } from '../modals/FamilyMemberDetailsModal';
import { RemoveRelationshipConfirmation } from '../modals/RemoveRelationshipConfirmation';
import { FamilyRelationship, RelationshipType } from '../types';
import './FamilyHubPage.css';

export function FamilyHubPage() {
  const { user } = useAuth();
  const {
    summary,
    members,
    sentInvitations,
    receivedInvitations,
    loading,
    error,
    refresh,
    inviteMember,
    acceptInvite,
    declineInvite,
    removeRelation
  } = useFamily();

  // Search & Filter state
  const [search, setSearch] = useState('');
  const [activeFilter, setActiveFilter] = useState<'ALL' | 'GUARDIANS' | 'DEPENDENTS' | 'PENDING'>('ALL');

  // Modals state
  const [inviteOpen, setInviteOpen] = useState(false);
  const [selectedMember, setSelectedMember] = useState<FamilyRelationship | null>(null);
  const [confirmDeleteMember, setConfirmDeleteMember] = useState<FamilyRelationship | null>(null);

  // Success Notification state
  const [successMsg, setSuccessMsg] = useState<string | null>(null);

  const triggerNotification = (msg: string) => {
    setSuccessMsg(msg);
    setTimeout(() => setSuccessMsg(null), 4000);
  };

  // Helper to resolve profile name/email for family list
  const getRelationDetails = (item: FamilyRelationship) => {
    const isDependentView = item.guardian?.email === user?.email;
    const targetUser = isDependentView ? item.dependent : item.guardian;
    const roleLabel = isDependentView ? 'Dependent' : 'Guardian';
    return { targetUser, roleLabel };
  };

  // Filtered members list based on filters and search queries
  const filteredMembers = useMemo(() => {
    return members.filter((item) => {
      const { targetUser, roleLabel } = getRelationDetails(item);
      const name = targetUser?.full_name || '';
      const email = targetUser?.email || '';
      const relationType = item.relationship;

      // Filter check
      if (activeFilter === 'GUARDIANS' && roleLabel !== 'Guardian') return false;
      if (activeFilter === 'DEPENDENTS' && roleLabel !== 'Dependent') return false;
      if (activeFilter === 'PENDING') return false; // Handled separately in Pending list

      // Search check
      if (search) {
        const query = search.toLowerCase();
        return (
          name.toLowerCase().includes(query) ||
          email.toLowerCase().includes(query) ||
          relationType.toLowerCase().includes(query)
        );
      }
      return true;
    });
  }, [members, activeFilter, search, user?.email]);

  const handleInviteSubmit = async (email: string, relationship: RelationshipType, notes: string) => {
    await inviteMember({ email, relationship, notes });
    triggerNotification('Family invitation successfully sent!');
  };

  const handleAcceptInvite = async (id: string) => {
    await acceptInvite(id);
    triggerNotification('Family invitation accepted!');
  };

  const handleDeclineInvite = async (id: string) => {
    await declineInvite(id);
    triggerNotification('Family invitation declined.');
  };

  const handleRemoveRelationship = async () => {
    if (!confirmDeleteMember) return;
    await removeRelation(confirmDeleteMember.id);
    setConfirmDeleteMember(null);
    setSelectedMember(null);
    triggerNotification('Family relationship successfully removed.');
  };

  if (error) {
    return (
      <div className="family-hub-page">
        <AppSidebar cta={
          <button onClick={() => setInviteOpen(true)} className="button button-primary" style={{ width: '100%' }}>
            <span className="material-symbols-outlined">person_add</span>
            Invite Member
          </button>
        } />
        <div className="documents-main">
          <div className="dashboard-error-state">
            <span className="material-symbols-outlined">error_outline</span>
            <h2>Unable to load Family Hub</h2>
            <p>{error}</p>
            <button type="button" className="button button-primary" onClick={refresh}>
              Try again
            </button>
          </div>
        </div>
      </div>
    );
  }

  if (loading && !summary) {
    return (
      <div className="family-hub-page">
        <AppSidebar cta={
          <button onClick={() => setInviteOpen(true)} className="button button-primary" style={{ width: '100%' }}>
            <span className="material-symbols-outlined">person_add</span>
            Invite Member
          </button>
        } />
        <div className="documents-main">
          <div className="dashboard-loading-state">
            <div className="spinner" />
            <p>Loading Family Hub…</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="family-hub-page">
      <AppSidebar cta={
        <button onClick={() => setInviteOpen(true)} className="button button-primary" style={{ width: '100%' }}>
          <span className="material-symbols-outlined">person_add</span>
          Invite Member
        </button>
      } />

      <div className="documents-main">
        {/* Sticky Header */}
        <header className="documents-topbar">
          <div className="documents-search">
            <span className="material-symbols-outlined">search</span>
            <input
              type="text"
              placeholder="Search family members..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
          </div>
          <div className="documents-topbar-actions">
            <button type="button" className="icon-button" onClick={refresh} title="Refresh family list">
              <span className="material-symbols-outlined">refresh</span>
            </button>
            <UserProfileMenu variant="topbar" />
          </div>
        </header>

        {/* Content Canvas */}
        <main className="documents-canvas">
          <section className="documents-headline">
            <div>
              <h1>Family Hub</h1>
              <p>Manage family relationships, guardians, dependents, and document access control permissions.</p>
            </div>
          </section>

          {/* Success Alerts */}
          {successMsg && (
            <div style={{
              margin: '0 0 24px 0',
              padding: '16px',
              backgroundColor: '#dcfce7',
              color: '#166534',
              borderRadius: '12px',
              border: '1px solid #bbf7d0',
              fontSize: '0.875rem',
              fontWeight: 600,
              display: 'flex',
              alignItems: 'center',
              gap: '8px'
            }}>
              <span className="material-symbols-outlined">check_circle</span>
              {successMsg}
            </div>
          )}

          {/* Summary Cards */}
          <section className="dashboard-overview-cards">
            <div className="metric-card">
              <div className="metric-icon" style={{ color: '#162839', backgroundColor: 'rgba(22,40,57,0.05)' }}>
                <span className="material-symbols-outlined">family_history</span>
              </div>
              <div className="metric-content">
                <p className="metric-label">Family Members</p>
                <h3 className="metric-value">{String(summary?.family_members || 0).padStart(2, '0')}</h3>
                <p className="metric-sublabel">Active Relationships</p>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon" style={{ color: '#362308', backgroundColor: 'rgba(54,35,8,0.05)' }}>
                <span className="material-symbols-outlined">child_care</span>
              </div>
              <div className="metric-content">
                <p className="metric-label">Dependents</p>
                <h3 className="metric-value">{String(summary?.dependent_count || 0).padStart(2, '0')}</h3>
                <p className="metric-sublabel">Managed Accounts</p>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon" style={{ color: '#2c3e50', backgroundColor: 'rgba(44,62,80,0.05)' }}>
                <span className="material-symbols-outlined">gavel</span>
              </div>
              <div className="metric-content">
                <p className="metric-label">Guardians</p>
                <h3 className="metric-value">{String(summary?.guardian_count || 0).padStart(2, '0')}</h3>
                <p className="metric-sublabel">Authorized Access</p>
              </div>
            </div>

            <div className="metric-card">
              <div className="metric-icon" style={{ color: '#b58900', backgroundColor: 'rgba(181,137,0,0.05)' }}>
                <span className="material-symbols-outlined">forward_to_inbox</span>
              </div>
              <div className="metric-content">
                <p className="metric-label">Pending</p>
                <h3 className="metric-value">{String(summary?.pending_invitations || 0).padStart(2, '0')}</h3>
                <p className="metric-sublabel">Awaiting Confirmation</p>
              </div>
            </div>
          </section>

          {/* Filter Chips */}
          <div className="chip-filters">
            {(['ALL', 'GUARDIANS', 'DEPENDENTS', 'PENDING'] as const).map((filter) => (
              <button
                key={filter}
                className={`filter-chip ${activeFilter === filter ? 'active' : ''}`}
                onClick={() => setActiveFilter(filter)}
              >
                {filter.charAt(0) + filter.slice(1).toLowerCase()}
              </button>
            ))}
          </div>

          {/* Layout Grid */}
          <div className="family-hub-grid">
            {/* Left Main Section */}
            <div className="dashboard-left-column" style={{ flex: 1 }}>
              {activeFilter !== 'PENDING' ? (
                <>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '8px' }}>
                    <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#162839', margin: 0 }}>Your Family</h3>
                    <button
                      onClick={() => setInviteOpen(true)}
                      style={{ background: 'transparent', border: 'none', color: '#162839', fontWeight: 600, cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px' }}
                    >
                      Invite Member
                      <span className="material-symbols-outlined" style={{ fontSize: '18px' }}>add_circle</span>
                    </button>
                  </div>

                  {filteredMembers.length === 0 ? (
                    <div className="empty-state" style={{ backgroundColor: '#ffffff', borderRadius: '1rem', border: '1px solid #e2e8f0' }}>
                      <span className="material-symbols-outlined">group</span>
                      <p>No family members found matching the filters.</p>
                      <button onClick={() => setInviteOpen(true)} className="button button-primary" style={{ marginTop: '12px' }}>
                        Invite Someone
                      </button>
                    </div>
                  ) : (
                    <div className="family-members-grid">
                      {filteredMembers.map((item) => {
                        const { targetUser, roleLabel } = getRelationDetails(item);
                        const initials = targetUser?.full_name
                          ? targetUser.full_name
                              .split(' ')
                              .map((n) => n[0])
                              .join('')
                              .toUpperCase()
                              .slice(0, 2)
                          : 'U';

                        return (
                          <div key={item.id} className="member-card">
                            <div className="member-card-header">
                              <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                                <div className="member-avatar">{initials}</div>
                                <div>
                                  <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#162839', margin: 0 }}>
                                    {targetUser?.full_name}
                                  </h4>
                                  <span className={`member-role-badge ${roleLabel.toLowerCase()}`}>
                                    {roleLabel} ({item.relationship})
                                  </span>
                                </div>
                              </div>
                              <button
                                onClick={() => setSelectedMember(item)}
                                className="icon-button"
                                style={{ padding: '4px' }}
                                title="View Member Profile"
                              >
                                <span className="material-symbols-outlined">more_vert</span>
                              </button>
                            </div>

                            <div className="member-details-grid">
                              <div className="member-detail-box">
                                <p className="member-detail-label">Status</p>
                                <p className="member-detail-value" style={{ color: '#2d6a4f', display: 'flex', alignItems: 'center', gap: '4px' }}>
                                  Active
                                  <span style={{ width: '6px', height: '6px', borderRadius: '50%', backgroundColor: '#2d6a4f' }} />
                                </p>
                              </div>
                              <div className="member-detail-box">
                                <p className="member-detail-label">Joined</p>
                                <p className="member-detail-value">
                                  {new Date(item.created_at).toLocaleDateString(undefined, { month: 'short', year: 'numeric' })}
                                </p>
                              </div>
                            </div>

                            <div className="member-card-footer">
                              <p className="member-joined-date">{targetUser?.email}</p>
                              <div style={{ display: 'flex', gap: '8px' }}>
                                <button
                                  onClick={() => setSelectedMember(item)}
                                  className="button"
                                  style={{ padding: '6px 12px', fontSize: '0.75rem', height: '32px', backgroundColor: '#162839', color: '#ffffff' }}
                                >
                                  Manage
                                </button>
                              </div>
                            </div>
                          </div>
                        );
                      })}

                      {/* Add Member Card */}
                      <div className="add-member-dashed-card" onClick={() => setInviteOpen(true)}>
                        <div style={{ width: '48px', height: '48px', borderRadius: '50%', backgroundColor: '#efedef', display: 'flex', alignItems: 'center', justifyContent: 'center', color: '#64748b', marginBottom: '16px' }}>
                          <span className="material-symbols-outlined">person_add</span>
                        </div>
                        <h4 style={{ fontSize: '1rem', fontWeight: 600, color: '#475569', margin: '0 0 4px 0' }}>Add Member</h4>
                        <p style={{ fontSize: '0.75rem', color: '#64748b', margin: 0 }}>Expand your family vault and assign roles.</p>
                      </div>
                    </div>
                  )}
                </>
              ) : (
                <>
                  {/* Pending tab view */}
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#162839', marginBottom: '16px' }}>Received Invitations</h3>
                  {receivedInvitations.length === 0 ? (
                    <div className="empty-state" style={{ backgroundColor: '#ffffff', borderRadius: '1rem', border: '1px solid #e2e8f0', marginBottom: '32px' }}>
                      <span className="material-symbols-outlined">mail</span>
                      <p>No pending received invitations.</p>
                    </div>
                  ) : (
                    <div className="family-members-grid" style={{ marginBottom: '32px' }}>
                      {receivedInvitations.map((invite) => {
                        const initials = invite.guardian?.full_name
                          ? invite.guardian.full_name
                              .split(' ')
                              .map((n) => n[0])
                              .join('')
                              .toUpperCase()
                              .slice(0, 2)
                          : 'U';
                        return (
                          <div key={invite.id} className="pending-invite-card">
                            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                              <div style={{ width: '40px', height: '40px', borderRadius: '50%', backgroundColor: '#162839', color: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                                {initials}
                              </div>
                              <div>
                                <h5 style={{ fontSize: '0.875rem', fontWeight: 600, color: '#162839', margin: 0 }}>
                                  {invite.guardian?.full_name}
                                </h5>
                                <p style={{ fontSize: '0.75rem', color: '#64748b', margin: 0 }}>
                                  Invite to join as {invite.relationship.toLowerCase()}
                                </p>
                              </div>
                            </div>
                            {invite.notes && (
                              <div className="pending-invite-msg">
                                "{invite.notes}"
                              </div>
                            )}
                            <div style={{ display: 'flex', gap: '8px' }}>
                              <button
                                onClick={() => handleAcceptInvite(invite.id)}
                                className="button button-primary"
                                style={{ flex: 1, height: '36px', fontSize: '0.75rem', padding: '0 12px' }}
                              >
                                Accept
                              </button>
                              <button
                                onClick={() => handleDeclineInvite(invite.id)}
                                className="button button-secondary"
                                style={{ flex: 1, height: '36px', fontSize: '0.75rem', padding: '0 12px' }}
                              >
                                Decline
                              </button>
                            </div>
                          </div>
                        );
                      })}
                    </div>
                  )}

                  <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#162839', marginBottom: '16px' }}>Sent Invitations</h3>
                  {sentInvitations.length === 0 ? (
                    <div className="empty-state" style={{ backgroundColor: '#ffffff', borderRadius: '1rem', border: '1px solid #e2e8f0' }}>
                      <span className="material-symbols-outlined">send</span>
                      <p>No pending sent invitations.</p>
                    </div>
                  ) : (
                    <div className="family-members-grid">
                      {sentInvitations.map((invite) => {
                        const initials = invite.dependent?.full_name
                          ? invite.dependent.full_name
                              .split(' ')
                              .map((n) => n[0])
                              .join('')
                              .toUpperCase()
                              .slice(0, 2)
                          : 'U';
                        return (
                          <div key={invite.id} className="pending-invite-card">
                            <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                              <div style={{ width: '40px', height: '40px', borderRadius: '50%', backgroundColor: '#e2e8f0', color: '#475569', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                                {initials}
                              </div>
                              <div>
                                <h5 style={{ fontSize: '0.875rem', fontWeight: 600, color: '#162839', margin: 0 }}>
                                  {invite.dependent?.full_name}
                                </h5>
                                <p style={{ fontSize: '0.75rem', color: '#64748b', margin: 0 }}>
                                  Role: {invite.relationship.toLowerCase()}
                                </p>
                              </div>
                            </div>
                            <button
                              onClick={() => removeRelation(invite.id)}
                              className="button button-secondary"
                              style={{ width: '100%', height: '36px', fontSize: '0.75rem', padding: '0 12px', borderColor: '#f87171', color: '#ef4444' }}
                            >
                              Cancel Invitation
                            </button>
                          </div>
                        );
                      })}
                    </div>
                  )}
                </>
              )}
            </div>

            {/* Right Side Column (Invitations Preview & Warnings) */}
            <div className="dashboard-right-column" style={{ width: '380px', flexShrink: 0 }}>
              {activeFilter !== 'PENDING' && (
                <>
                  <h3 style={{ fontSize: '1.25rem', fontWeight: 600, color: '#162839', margin: 0 }}>Pending Invitations</h3>
                  {receivedInvitations.length === 0 && sentInvitations.length === 0 ? (
                    <div className="empty-state" style={{ backgroundColor: '#ffffff', borderRadius: '1rem', border: '1px solid #e2e8f0' }}>
                      <span className="material-symbols-outlined">mail</span>
                      <p>No pending invitations.</p>
                    </div>
                  ) : (
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                      {/* Received list */}
                      {receivedInvitations.map((invite) => (
                        <div key={invite.id} className="pending-invite-card">
                          <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
                            <div style={{ width: '40px', height: '40px', borderRadius: '50%', backgroundColor: '#162839', color: '#ffffff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold' }}>
                              {(invite.guardian?.full_name || 'U').substring(0, 2).toUpperCase()}
                            </div>
                            <div>
                              <h5 style={{ fontSize: '0.875rem', fontWeight: 600, color: '#162839', margin: 0 }}>
                                {invite.guardian?.full_name}
                              </h5>
                              <p style={{ fontSize: '0.75rem', color: '#64748b', margin: 0 }}>
                                Guardian Request
                              </p>
                            </div>
                          </div>
                          {invite.notes && (
                            <div className="pending-invite-msg">
                              "{invite.notes}"
                            </div>
                          )}
                          <div style={{ display: 'flex', gap: '8px' }}>
                            <button
                              onClick={() => handleAcceptInvite(invite.id)}
                              className="button button-primary"
                              style={{ flex: 1, height: '36px', fontSize: '0.75rem', padding: '0 12px' }}
                            >
                              Accept
                            </button>
                            <button
                              onClick={() => handleDeclineInvite(invite.id)}
                              className="button button-secondary"
                              style={{ flex: 1, height: '36px', fontSize: '0.75rem', padding: '0 12px' }}
                            >
                              Decline
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </>
              )}

              {/* Security Audit CTA Card */}
              <div style={{ backgroundColor: '#162839', padding: '24px', borderRadius: '1rem', color: '#ffffff', position: 'relative', overflow: 'hidden' }}>
                <div style={{ position: 'relative', zIndex: 10 }}>
                  <h4 style={{ fontSize: '1.1rem', fontWeight: 600, margin: '0 0 8px 0' }}>Security Check</h4>
                  <p style={{ fontSize: '0.75rem', opacity: 0.8, lineHeight: 1.5, margin: '0 0 16px 0' }}>
                    Ensure all guardians have updated their emergency contact info and biometric signatures.
                  </p>
                  <button
                    className="button"
                    style={{ width: '100%', height: '36px', backgroundColor: '#ffffff', color: '#162839', fontWeight: 600 }}
                  >
                    Run Security Audit
                  </button>
                </div>
                <span className="material-symbols-outlined" style={{ position: 'absolute', right: '-16px', bottom: '-16px', fontSize: '100px', opacity: 0.05, transform: 'rotate(12deg)' }}>
                  verified_user
                </span>
              </div>
            </div>
          </div>
        </main>
      </div>

      {/* Modals Mounting */}
      {inviteOpen && (
        <AddFamilyMemberModal
          onClose={() => setInviteOpen(false)}
          onInvite={handleInviteSubmit}
        />
      )}

      {selectedMember && (
        <FamilyMemberDetailsModal
          member={selectedMember}
          currentUserEmail={user?.email}
          onClose={() => setSelectedMember(null)}
          onRemove={(id) => {
            const memberToConfirm = members.find((m) => m.id === id);
            if (memberToConfirm) {
              setConfirmDeleteMember(memberToConfirm);
            }
          }}
        />
      )}

      {confirmDeleteMember && (
        <RemoveRelationshipConfirmation
          relationship={confirmDeleteMember}
          currentUserEmail={user?.email}
          onClose={() => setConfirmDeleteMember(null)}
          onConfirm={handleRemoveRelationship}
        />
      )}
    </div>
  );
}
export default FamilyHubPage;
