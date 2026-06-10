export interface UserProfile {
  id: string;
  full_name: string;
  email: string;
  phone_number?: string | null;
  profile_image?: string | null;
  role?: string;
}

export interface UpdateProfilePayload {
  full_name?: string;
  phone_number?: string | null;
}

export interface UpdatePasswordPayload {
  current_password: string;
  new_password: string;
  confirm_password: string;
}

export interface NotificationPreferences {
  email_notifications: boolean;
  push_notifications: boolean;
  document_expiry_alerts: boolean;
  share_activity_alerts: boolean;
  login_alerts: boolean;
}

export interface PrivacySettings {
  show_profile_to_contacts: boolean;
  allow_emergency_access: boolean;
}

export interface ReminderSettings {
  expiry_reminder_days: number;
  reminder_frequency: 'daily' | 'weekly' | 'monthly';
}

export interface SecuritySettings {
  two_factor_enabled: boolean;
  session_timeout_minutes: number;
}
