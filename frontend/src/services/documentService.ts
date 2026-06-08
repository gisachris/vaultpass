import { api } from '../lib/api';
import {
  DocumentListResponse,
  DocumentModel,
  DocumentType,
  DocumentUpdatePayload,
  DocumentUploadPayload,
} from '../types/document';

interface DownloadResponse {
  download_url: string;
}

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

export async function downloadDocumentUrl(documentId: string): Promise<string> {
  const response = await api.get<DownloadResponse>(`/documents/${documentId}/download`);
  return response.data.download_url;
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
