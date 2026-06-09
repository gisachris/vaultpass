export interface ReceivedShare {
  share_id: string;
  document_id: string;
  document_title: string;
  document_type: string;
  owner_name: string;
  shared_at: string;
  expires_at: string | null;
  is_active: boolean;
}

export interface ReceivedShareDetail extends ReceivedShare {
  owner_id: string;
  contact_id: string;
  last_accessed_at: string | null;
}
