import { api } from '../lib/api';

export interface DocumentShareModel {
  id: string;
  document_id: string;
  contact_id: string;
  owner_id: string;
  access_token: string;
  share_link: string;
  is_active: boolean;
  expires_at: string | null;
  last_accessed_at: string | null;
  created_at: string;
  updated_at: string | null;
  document_title?: string;
  contact_name?: string;
}

export interface PublicSharedDocument {
  title: string;
  document_type: string;
  created_at: string;
  expiry_date: string | null;
  download_url: string;
}

export interface CreateDocumentSharePayload {
  document_id: string;
  contact_id: string;
  expires_at?: string;
}

export async function fetchDocumentShares(): Promise<DocumentShareModel[]> {
  const response = await api.get<DocumentShareModel[]>('/v1/shares');
  return response.data;
}

export async function createDocumentShare(payload: CreateDocumentSharePayload): Promise<DocumentShareModel> {
  const response = await api.post<DocumentShareModel>('/v1/shares', payload);
  return response.data;
}

export async function deleteDocumentShare(shareId: string): Promise<void> {
  await api.delete(`/v1/shares/${shareId}`);
}

export async function revokeDocumentShare(shareId: string): Promise<DocumentShareModel> {
  const response = await api.patch<DocumentShareModel>(`/v1/shares/${shareId}/revoke`);
  return response.data;
}

export async function activateDocumentShare(shareId: string): Promise<DocumentShareModel> {
  const response = await api.patch<DocumentShareModel>(`/v1/shares/${shareId}/activate`);
  return response.data;
}

export async function fetchPublicSharedDocument(token: string): Promise<PublicSharedDocument> {
  // Use unauthenticated path relative to root url
  const response = await api.get<PublicSharedDocument>(`/public/share/${token}`);
  return response.data;
}
