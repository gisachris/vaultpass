import { DocumentModel } from '../../../types/document';

export type RelationshipType = 'SPOUSE' | 'PARENT' | 'CHILD' | 'SIBLING' | 'PARTNER' | 'OTHER';

export type RelationshipStatus = 'PENDING' | 'ACCEPTED' | 'DECLINED' | 'REMOVED';

export interface FamilyUser {
  id: string;
  full_name: string;
  email: string;
}

export interface FamilyRelationship {
  id: string;
  guardian_id: string;
  dependent_id: string;
  relationship: RelationshipType;
  status: RelationshipStatus;
  invited_by: string;
  notes: string | null;
  created_at: string;
  accepted_at: string | null;
  guardian?: FamilyUser;
  dependent?: FamilyUser;
}

export interface FamilySummary {
  family_members: number;
  guardian_count: number;
  dependent_count: number;
  accessible_documents: number;
  pending_invitations: number;
}

export interface DependentDocuments {
  dependent_id: string;
  dependent_name: string;
  relationship: RelationshipType;
  documents: DocumentModel[];
}

export interface FamilyInvitationCreate {
  email: string;
  relationship: RelationshipType;
  notes?: string;
}

export function getRelativeRelationshipLabel(
  relationship: FamilyRelationship,
  currentUserEmail?: string
): string {
  const isGuardianCurrentUser = relationship.guardian?.email === currentUserEmail;
  const rel = relationship.relationship;

  if (isGuardianCurrentUser) {
    if (rel === 'PARENT') return 'Child';
    if (rel === 'CHILD') return 'Parent';
  } else {
    if (rel === 'PARENT') return 'Parent';
    if (rel === 'CHILD') return 'Child';
  }

  return rel.charAt(0) + rel.slice(1).toLowerCase();
}

