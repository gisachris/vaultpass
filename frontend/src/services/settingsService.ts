import { api } from '../lib/api';
import {
  UpdatePasswordPayload,
  NotificationPreferences,
  PrivacySettings,
  ReminderSettings,
  SecuritySettings,
} from '../types/settings';

// ─── Password ────────────────────────────────────────────────────────────────
export async function changePassword(payload: UpdatePasswordPayload): Promise<void> {
  await api.put('/settings/password', {
    current_password: payload.current_password,
    new_password: payload.new_password,
  });
}

// ─── Notification Preferences ────────────────────────────────────────────────
export async function getNotificationPreferences(): Promise<NotificationPreferences> {
  const response = await api.get<NotificationPreferences>('/settings/notifications');
  return response.data;
}

export async function updateNotificationPreferences(
  payload: Partial<NotificationPreferences>
): Promise<NotificationPreferences> {
  const response = await api.put<NotificationPreferences>('/settings/notifications', payload);
  return response.data;
}

// ─── Privacy Settings ────────────────────────────────────────────────────────
export async function getPrivacySettings(): Promise<PrivacySettings> {
  const response = await api.get<PrivacySettings>('/settings/privacy');
  return response.data;
}

export async function updatePrivacySettings(
  payload: Partial<PrivacySettings>
): Promise<PrivacySettings> {
  const response = await api.put<PrivacySettings>('/settings/privacy', payload);
  return response.data;
}

// ─── Reminder Settings ───────────────────────────────────────────────────────
export async function getReminderSettings(): Promise<ReminderSettings> {
  const response = await api.get<ReminderSettings>('/settings/reminders');
  return response.data;
}

export async function updateReminderSettings(
  payload: Partial<ReminderSettings>
): Promise<ReminderSettings> {
  const response = await api.put<ReminderSettings>('/settings/reminders', payload);
  return response.data;
}

// ─── Security Settings ───────────────────────────────────────────────────────
export async function getSecuritySettings(): Promise<SecuritySettings> {
  const response = await api.get<SecuritySettings>('/settings/security');
  return response.data;
}

export async function updateSecuritySettings(
  payload: Partial<SecuritySettings>
): Promise<SecuritySettings> {
  const response = await api.put<SecuritySettings>('/settings/security', payload);
  return response.data;
}
