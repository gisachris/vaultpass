import { api } from '../lib/api';
import {
  DocumentListResponse,
  DocumentModel,
  DocumentType,
  DocumentUpdatePayload,
  DocumentUploadPayload,
  DocumentPreviewResponse,
  DocumentDownloadResponse,
} from '../types/document';

export async function fetchDocuments(
  page: number,
  limit: number,
  search?: string,
): Promise<DocumentListResponse> {
  const response = await api.get<DocumentListResponse>('/documents', {
    params: {
      page,
      limit,
      search: search?.trim() || undefined,
    },
  });
  return response.data;
}

export async function fetchDocumentDetails(documentId: string): Promise<DocumentModel> {
  const response = await api.get<DocumentModel>(`/documents/${documentId}`);
  return response.data;
}

/** Returns a signed preview URL (10-minute expiry). */
export async function previewDocumentUrl(documentId: string): Promise<string> {
  const response = await api.get<DocumentPreviewResponse>(`/documents/${documentId}/preview`);
  return response.data.data.preview_url;
}

/** Returns a signed download URL (15-minute expiry). */
export async function downloadDocumentUrl(documentId: string): Promise<string> {
  const response = await api.get<DocumentDownloadResponse>(`/documents/${documentId}/download`);
  return response.data.data.download_url;
}

/**
 * Trigger a file download without navigating away.
 * Creates a hidden anchor, clicks it, and removes it.
 */
export function triggerFileDownload(fileName: string, url: string): void {
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = fileName;
  anchor.target = '_blank';
  anchor.rel = 'noopener noreferrer';
  document.body.appendChild(anchor);
  anchor.click();
  document.body.removeChild(anchor);
}

export async function uploadDocument(payload: DocumentUploadPayload): Promise<DocumentModel> {
  const formData = new FormData();
  formData.append('file', payload.file);
  formData.append('title', payload.title);
  formData.append('document_type', payload.document_type);
  if (payload.description) {
    formData.append('description', payload.description);
  }
  if (payload.expiry_date) {
    formData.append('expiry_date', payload.expiry_date);
  }

  const response = await api.post<DocumentModel>('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  });
  return response.data;
}

export async function updateDocument(
  documentId: string,
  payload: DocumentUpdatePayload,
): Promise<DocumentModel> {
  const response = await api.put<DocumentModel>(`/documents/${documentId}`, payload);
  return response.data;
}

export async function deleteDocument(documentId: string): Promise<void> {
  await api.delete(`/documents/${documentId}`);
}
