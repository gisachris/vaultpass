import { api } from '../lib/api';

// ─── Access Level ────────────────────────────────────────────────────────────
export type AccessLevel = 'view' | 'view_download' | 'edit_metadata';

export const ACCESS_LEVEL_LABELS: Record<AccessLevel, string> = {
  view: 'View Only',
  view_download: 'View + Download',
  edit_metadata: 'Edit Metadata',
};

export const ACCESS_LEVEL_DESCRIPTIONS: Record<AccessLevel, string> = {
  view: 'Can view document but cannot download.',
  view_download: 'Can view and download document.',
  edit_metadata: 'Can view, download, and update document metadata. Cannot delete.',
};

// ─── Models ──────────────────────────────────────────────────────────────────
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
  // Internal sharing fields (present when share targets a registered user)
  recipient_user_id?: string | null;
  access_level?: AccessLevel | null;
}

export interface PublicSharedDocument {
  title: string;
  document_type: string;
  created_at: string;
  expiry_date: string | null;
  download_url: string | null;
  allow_download: boolean;
}

// ─── Payloads ─────────────────────────────────────────────────────────────────
export interface CreateDocumentSharePayload {
  document_id: string;
  contact_id: string;
  expires_at?: string;
  // External link options — stored in UI, wired to backend in a later sprint
  allow_download?: boolean;
  password?: string;
}

export interface InternalSharePayload {
  document_id: string;
  contact_id: string;
  // access_level will be sent to backend in a later sprint when it supports it
  access_level?: AccessLevel;
  expires_at?: string;
}

// ─── Share info summary (for document row badges) ────────────────────────────
export interface DocumentShareInfo {
  internalCount: number;
  externalCount: number;
  hasInternal: boolean;
  hasExternal: boolean;
}

// ─── API functions ────────────────────────────────────────────────────────────

export async function fetchDocumentShares(): Promise<DocumentShareModel[]> {
  const response = await api.get<DocumentShareModel[]>('/v1/shares');
  return response.data;
}

export async function fetchSharesForDocument(documentId: string): Promise<DocumentShareModel[]> {
  const response = await api.get<DocumentShareModel[]>('/v1/shares', {
    params: { document_id: documentId },
  });
  return response.data;
}

/**
 * Create a share (internal or external) — the backend determines which path
 * to take based on whether the contact has a linked_user_id.
 */
export async function createDocumentShare(payload: CreateDocumentSharePayload): Promise<DocumentShareModel> {
  const response = await api.post<DocumentShareModel>('/v1/shares', payload);
  return response.data;
}

/**
 * Create an internal share for a registered VaultPass user.
 * access_level is included in the payload for future backend support.
 */
export async function createInternalShare(payload: InternalSharePayload): Promise<DocumentShareModel> {
  const response = await api.post<DocumentShareModel>('/v1/shares', {
    document_id: payload.document_id,
    contact_id: payload.contact_id,
    expires_at: payload.expires_at,
    // access_level forwarded for when backend supports it
    access_level: payload.access_level,
  });
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

export async function fetchPublicSharedDocument(token: string, password?: string): Promise<PublicSharedDocument> {
  const headers = password ? { 'X-Share-Password': password } : undefined;
  const response = await api.get<PublicSharedDocument>(`/public/share/${token}`, { headers });
  return response.data;
}

/**
 * Build a share info map keyed by document_id from a list of shares.
 * Used to efficiently render per-document sharing badges.
 */
export function buildShareInfoMap(shares: DocumentShareModel[]): Record<string, DocumentShareInfo> {
  const map: Record<string, DocumentShareInfo> = {};

  for (const share of shares) {
    if (!share.is_active) continue;

    const existing = map[share.document_id] ?? {
      internalCount: 0,
      externalCount: 0,
      hasInternal: false,
      hasExternal: false,
    };

    if (share.recipient_user_id) {
      existing.internalCount += 1;
      existing.hasInternal = true;
    } else {
      existing.externalCount += 1;
      existing.hasExternal = true;
    }

    map[share.document_id] = existing;
  }

  return map;
}
