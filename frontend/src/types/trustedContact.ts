export interface TrustedContactModel {
  id: string;
  full_name: string;
  email: string;
  phone_number?: string | null;
  relationship: string;
  notes?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface TrustedContactListResponse {
  items: TrustedContactModel[];
  total: number;
  page: number;
  page_size: number;
}

export interface TrustedContactCreatePayload {
  full_name: string;
  email: string;
  phone_number?: string;
  relationship: string;
  notes?: string;
}
