import { useEffect, useState } from 'react';
import { AxiosError } from 'axios';
import {
  fetchNotifications,
  fetchUnreadCount,
  markAllNotificationsRead,
  markNotificationRead,
  markNotificationUnread,
  deleteNotification as deleteNotificationApi,
  deleteAllNotifications as deleteAllNotificationsApi,
} from '../api/notificationApi';
import {
  Notification,
  NotificationReadFilter,
  NotificationSortDirection,
  NotificationType,
} from '../types/notification.types';

interface UseNotificationsResult {
  notifications: Notification[];
  total: number;
  page: number;
  pages: number;
  limit: number;
  unreadCount: number;
  filter: NotificationReadFilter;
  typeFilter: NotificationType | 'ALL';
  sorting: NotificationSortDirection;
  loading: boolean;
  actionLoading: boolean;
  error: string | null;
  setPage: (page: number) => void;
  setFilter: (filter: NotificationReadFilter) => void;
  setTypeFilter: (type: NotificationType | 'ALL') => void;
  setSorting: (sorting: NotificationSortDirection) => void;
  refresh: () => Promise<void>;
  markAllRead: () => Promise<void>;
  markRead: (notificationId: string) => Promise<void>;
  markUnread: (notificationId: string) => Promise<void>;
  deleteNotification: (notificationId: string) => Promise<void>;
  deleteAll: () => Promise<void>;
}

export function useNotifications(): UseNotificationsResult {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const [total, setTotal] = useState(0);
  const [page, setPage] = useState(1);
  const [limit] = useState(10);
  const [pages, setPages] = useState(1);
  const [unreadCount, setUnreadCount] = useState(0);
  const [filter, setFilter] = useState<NotificationReadFilter>('ALL');
  const [typeFilter, setTypeFilter] = useState<NotificationType | 'ALL'>('ALL');
  const [sorting, setSorting] = useState<NotificationSortDirection>('desc');
  const [loading, setLoading] = useState(false);
  const [actionLoading, setActionLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadNotifications = async () => {
    setLoading(true);
    setError(null);

    try {
      const [notificationData, unreadData] = await Promise.all([
        fetchNotifications(page, limit, filter, typeFilter, sorting),
        fetchUnreadCount(),
      ]);

      setNotifications(notificationData.items);
      setTotal(notificationData.total);
      setPages(notificationData.pages);
      setUnreadCount(unreadData.unread_count);
    } catch (err) {
      if (err instanceof AxiosError) {
        setError(err.response?.data?.detail || err.message || 'Unable to load notifications.');
      } else {
        setError('Unable to load notifications.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    setPage(1);
  }, [filter, typeFilter, sorting]);

  useEffect(() => {
    loadNotifications();
  }, [page, filter, typeFilter, sorting]);

  const refresh = async () => {
    await loadNotifications();
  };

  const markAllRead = async () => {
    setActionLoading(true);
    try {
      await markAllNotificationsRead();
      setNotifications((current) => current.map((notification) => ({ ...notification, is_read: true })));
      setUnreadCount(0);
    } finally {
      setActionLoading(false);
    }
  };

  const markRead = async (notificationId: string) => {
    setActionLoading(true);
    try {
      await markNotificationRead(notificationId);
      setNotifications((current) =>
        current.map((notification) =>
          notification.id === notificationId ? { ...notification, is_read: true } : notification,
        ),
      );
      setUnreadCount((current) => Math.max(current - 1, 0));
    } finally {
      setActionLoading(false);
    }
  };

  const markUnread = async (notificationId: string) => {
    setActionLoading(true);
    try {
      await markNotificationUnread(notificationId);
      setNotifications((current) =>
        current.map((notification) =>
          notification.id === notificationId ? { ...notification, is_read: false } : notification,
        ),
      );
      setUnreadCount((current) => current + 1);
    } finally {
      setActionLoading(false);
    }
  };

  const deleteNotification = async (notificationId: string) => {
    setActionLoading(true);
    try {
      await deleteNotificationApi(notificationId);
      setNotifications((current) => current.filter((notification) => notification.id !== notificationId));
      setTotal((current) => Math.max(current - 1, 0));
      setUnreadCount((current) =>
        current - (notifications.find((notification) => notification.id === notificationId)?.is_read ? 0 : 1),
      );
    } finally {
      setActionLoading(false);
    }
  };

  const deleteAll = async () => {
    setActionLoading(true);
    try {
      await deleteAllNotificationsApi();
      setNotifications([]);
      setTotal(0);
      setPages(1);
      setPage(1);
      setUnreadCount(0);
    } finally {
      setActionLoading(false);
    }
  };

  return {
    notifications,
    total,
    page,
    pages,
    limit,
    unreadCount,
    filter,
    typeFilter,
    sorting,
    loading,
    actionLoading,
    error,
    setPage,
    setFilter,
    setTypeFilter,
    setSorting,
    refresh,
    markAllRead,
    markRead,
    markUnread,
    deleteNotification,
    deleteAll,
  };
}
