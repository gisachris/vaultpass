import { api } from '../../../lib/api';
import { notificationApiPaths } from '../../../lib/apiSpec';
import {
  Notification,
  NotificationListResponse,
  NotificationUnreadCountResponse,
  NotificationReadFilter,
  NotificationSortDirection,
  NotificationType,
} from '../types/notification.types';

export async function fetchNotifications(
  page: number,
  limit: number,
  filter: NotificationReadFilter,
  type: NotificationType | 'ALL',
  sorting: NotificationSortDirection,
): Promise<NotificationListResponse> {
  const params: Record<string, unknown> = {
    page,
    limit,
    sorting,
  };

  if (filter === 'READ') {
    params.is_read = true;
  }

  if (filter === 'UNREAD') {
    params.is_read = false;
  }

  if (type !== 'ALL') {
    params.type = type;
  }

  const response = await api.get<NotificationListResponse>(notificationApiPaths.list, {
    params,
  });
  return response.data;
}

export async function fetchUnreadCount(): Promise<NotificationUnreadCountResponse> {
  const response = await api.get<NotificationUnreadCountResponse>(notificationApiPaths.unreadCount);
  return response.data;
}

export async function markAllNotificationsRead(): Promise<void> {
  await api.patch(notificationApiPaths.markAllRead);
}

export async function fetchNotificationDetails(notificationId: string): Promise<Notification> {
  const response = await api.get<Notification>(notificationApiPaths.details(notificationId));
  return response.data;
}

export async function markNotificationRead(notificationId: string): Promise<void> {
  await api.patch(notificationApiPaths.markRead(notificationId));
}

export async function markNotificationUnread(notificationId: string): Promise<void> {
  await api.patch(notificationApiPaths.markUnread(notificationId));
}

export async function deleteNotification(notificationId: string): Promise<void> {
  await api.delete(notificationApiPaths.deleteNotification(notificationId));
}

export async function deleteAllNotifications(): Promise<void> {
  await api.delete(notificationApiPaths.deleteAll);
}
