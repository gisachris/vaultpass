export type DocumentType =
  | 'PASSPORT'
  | 'NATIONAL_ID'
  | 'BIRTH_CERTIFICATE'
  | 'ACADEMIC_CERTIFICATE'
  | 'PROPERTY_DOCUMENT'
  | 'WILL'
  | 'OTHER';

export type DocumentCategoryFilter = 'ALL' | 'ID' | 'LEGAL' | 'MEDICAL';

export interface DocumentModel {
  id: string;
  owner_id: string;
  title: string;
  document_type: DocumentType;
  description?: string | null;
  file_name: string;
  file_path: string;
  file_size: number;
  mime_type: string;
  expiry_date?: string | null;
  uploaded_at: string;
  created_at: string;
  updated_at?: string | null;
}

export interface DocumentListResponse {
  items: DocumentModel[];
  total: number;
  page: number;
  limit: number;
}

export interface DocumentUploadPayload {
  file: File;
  title: string;
  document_type: DocumentType;
  description?: string;
  expiry_date?: string;
}

export interface DocumentUpdatePayload {
  title: string;
  document_type: DocumentType;
  description?: string;
  expiry_date?: string;
}

export const DOCUMENT_TYPE_LABELS: Record<DocumentType, string> = {
  PASSPORT: 'Passport',
  NATIONAL_ID: 'National ID',
  BIRTH_CERTIFICATE: 'Birth Certificate',
  ACADEMIC_CERTIFICATE: 'Academic Certificate',
  PROPERTY_DOCUMENT: 'Property Document',
  WILL: 'Last Will',
  OTHER: 'Other',
};

export const DOCUMENT_TYPE_ICONS: Record<DocumentType, string> = {
  PASSPORT: 'badge',
  NATIONAL_ID: 'badge',
  BIRTH_CERTIFICATE: 'badge',
  ACADEMIC_CERTIFICATE: 'school',
  PROPERTY_DOCUMENT: 'gavel',
  WILL: 'gavel',
  OTHER: 'description',
};

export const DOCUMENT_CATEGORY_BUTTONS: ReadonlyArray<{
  key: DocumentCategoryFilter;
  label: string;
}> = [
  { key: 'ALL', label: 'All Documents' },
  { key: 'ID', label: 'ID' },
  { key: 'LEGAL', label: 'Legal' },
  { key: 'MEDICAL', label: 'Medical' },
];

export const DOCUMENT_CATEGORY_TYPE_MAP: Record<DocumentCategoryFilter, DocumentType[]> = {
  ALL: [
    'PASSPORT',
    'NATIONAL_ID',
    'BIRTH_CERTIFICATE',
    'ACADEMIC_CERTIFICATE',
    'PROPERTY_DOCUMENT',
    'WILL',
    'OTHER',
  ],
  ID: ['PASSPORT', 'NATIONAL_ID', 'BIRTH_CERTIFICATE'],
  LEGAL: ['PROPERTY_DOCUMENT', 'WILL'],
  MEDICAL: [],
};
