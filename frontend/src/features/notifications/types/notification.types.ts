export type NotificationType = 'INFO' | 'SUCCESS' | 'WARNING' | 'ERROR';

export type NotificationReadFilter = 'ALL' | 'READ' | 'UNREAD';
export type NotificationSortDirection = 'desc' | 'asc';

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: NotificationType;
  is_read: boolean;
  related_document_id?: string | null;
  related_contact_id?: string | null;
  related_share_id?: string | null;
  created_at: string;
  updated_at?: string | null;
}

export interface NotificationListResponse {
  items: Notification[];
  total: number;
  page: number;
  pages: number;
  limit: number;
}

export interface NotificationUnreadCountResponse {
  unread_count: number;
}
