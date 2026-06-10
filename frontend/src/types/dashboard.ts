export interface DashboardSummary {
  total_documents: number;
  trusted_contacts: number;
  active_shares: number;
  unread_notifications: number;
  shared_with_me_count: number;
  documents_previewed_count?: number;
  documents_downloaded_count?: number;
}

export interface DocumentHealth {
  valid_documents: number;
  expiring_soon: number;
  expired_documents: number;
}

export interface DocumentCategory {
  category: string;
  count: number;
}

export interface ExpiringDocument {
  document_id: string;
  document_name: string;
  category: string;
  expiry_date: string;
  days_remaining: number;
}

export interface RecentActivity {
  action: string;
  description: string;
  created_at: string;
}

export interface RecentNotification {
  id: string;
  title: string;
  message: string;
  is_read: boolean;
  created_at: string;
}

export interface SharedWithMeDocument {
  share_id: string;
  document_title: string;
  owner_name: string;
  shared_at: string;
}

export interface AccountOverview {
  account_created: string;
  last_login: string | null;
  storage_used_mb: number;
}

export interface DashboardData {
  summary: DashboardSummary;
  document_health: DocumentHealth;
  categories: DocumentCategory[];
  expiring_documents: ExpiringDocument[];
  recent_activity: RecentActivity[];
  recent_notifications: RecentNotification[];
  recent_shared_documents: SharedWithMeDocument[];
  account_overview: AccountOverview;
}
