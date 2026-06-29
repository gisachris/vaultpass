import { api } from '../../../lib/api';
import {
  FamilySummary,
  FamilyRelationship,
  FamilyInvitationCreate,
  DependentDocuments,
  RelationshipType
} from '../types';

export async function fetchFamilySummary(): Promise<FamilySummary> {
  const response = await api.get<FamilySummary>('/family/summary');
  return response.data;
}

export async function fetchFamilyMembers(): Promise<FamilyRelationship[]> {
  const response = await api.get<FamilyRelationship[]>('/family');
  return response.data;
}

export async function fetchSentInvitations(): Promise<FamilyRelationship[]> {
  const response = await api.get<FamilyRelationship[]>('/family/invitations/sent');
  return response.data;
}

export async function fetchReceivedInvitations(): Promise<FamilyRelationship[]> {
  const response = await api.get<FamilyRelationship[]>('/family/invitations/received');
  return response.data;
}

export async function sendInvitation(payload: FamilyInvitationCreate): Promise<FamilyRelationship> {
  const response = await api.post<FamilyRelationship>('/family/invitations', payload);
  return response.data;
}

export async function acceptInvitation(id: string): Promise<FamilyRelationship> {
  const response = await api.post<FamilyRelationship>(`/family/invitations/${id}/accept`);
  return response.data;
}

export async function declineInvitation(id: string): Promise<FamilyRelationship> {
  const response = await api.post<FamilyRelationship>(`/family/invitations/${id}/decline`);
  return response.data;
}

export async function removeRelationship(id: string): Promise<void> {
  await api.delete(`/family/${id}`);
}

export interface FetchGuardianDocsParams {
  page?: number;
  limit?: number;
  search?: string;
  category?: string;
  dependent_name?: string;
  relationship?: RelationshipType;
}

export async function fetchGuardianDocuments(params?: FetchGuardianDocsParams): Promise<DependentDocuments[]> {
  const response = await api.get<DependentDocuments[]>('/family/documents', { params });
  return response.data;
}
