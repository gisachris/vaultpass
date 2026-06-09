import { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { toast } from 'sonner';
import { AppSidebar } from '../components/ui/AppSidebar';
import { UserProfileMenu } from '../components/profile/UserProfileMenu';
import { useAuth } from '../context/AuthContext';
import { getProfile, updateProfile } from '../services/profileService';
import {
  changePassword,
  getNotificationPreferences,
  updateNotificationPreferences,
  getPrivacySettings,
  updatePrivacySettings,
  getReminderSettings,
  updateReminderSettings,
} from '../services/settingsService';
import type {
  UserProfile,
  NotificationPreferences,
  PrivacySettings,
  ReminderSettings,
} from '../types/settings';
import './SettingsPage.css';

// ─── Schemas ──────────────────────────────────────────────────────────────────
const profileSchema = z.object({
  full_name: z.string().min(1, 'Name is required').max(100),
  phone_number: z.string().optional(),
});

const passwordSchema = z
  .object({
    current_password: z.string().min(1, 'Current password is required'),
    new_password: z.string().min(8, 'Password must be at least 8 characters'),
    confirm_password: z.string().min(1, 'Please confirm your new password'),
  })
  .refine((d) => d.new_password === d.confirm_password, {
    message: "Passwords don't match",
    path: ['confirm_password'],
  });

type ProfileForm = z.infer<typeof profileSchema>;
type PasswordForm = z.infer<typeof passwordSchema>;

// ─── Section enum ─────────────────────────────────────────────────────────────
type Section = 'profile' | 'password' | 'notifications' | 'privacy' | 'reminders';

// ─── Component ────────────────────────────────────────────────────────────────
export function SettingsPage() {
  const { user, refreshUser } = useAuth();
  const [activeSection, setActiveSection] = useState<Section>('profile');

  // Profile state
  const [profileLoading, setProfileLoading] = useState(true);
  const [profileSaving, setProfileSaving] = useState(false);
  const [profile, setProfile] = useState<UserProfile | null>(null);

  // Notification prefs
  const [notifPrefs, setNotifPrefs] = useState<NotificationPreferences | null>(null);
  const [notifSaving, setNotifSaving] = useState(false);

  // Privacy
  const [privacy, setPrivacy] = useState<PrivacySettings | null>(null);
  const [privacySaving, setPrivacySaving] = useState(false);

  // Reminders
  const [reminders, setReminders] = useState<ReminderSettings | null>(null);
  const [reminderSaving, setReminderSaving] = useState(false);

  // Password saving
  const [passwordSaving, setPasswordSaving] = useState(false);

  // ─── Profile form ──────────────────────────────────────────────────────────
  const {
    register: regProfile,
    handleSubmit: handleProfileSubmit,
    reset: resetProfile,
    formState: { errors: profileErrors },
  } = useForm<ProfileForm>({ resolver: zodResolver(profileSchema) });

  // ─── Password form ─────────────────────────────────────────────────────────
  const {
    register: regPwd,
    handleSubmit: handlePwdSubmit,
    reset: resetPwd,
    formState: { errors: pwdErrors },
  } = useForm<PasswordForm>({ resolver: zodResolver(passwordSchema) });

  // ─── Load data ─────────────────────────────────────────────────────────────
  useEffect(() => {
    async function load() {
      setProfileLoading(true);
      try {
        const [p, n, priv, rem] = await Promise.allSettled([
          getProfile(),
          getNotificationPreferences(),
          getPrivacySettings(),
          getReminderSettings(),
        ]);

        if (p.status === 'fulfilled') {
          setProfile(p.value);
          resetProfile({
            full_name: p.value.full_name,
            phone_number: p.value.phone_number ?? '',
          });
        }
        if (n.status === 'fulfilled') setNotifPrefs(n.value);
        if (priv.status === 'fulfilled') setPrivacy(priv.value);
        if (rem.status === 'fulfilled') setReminders(rem.value);
      } finally {
        setProfileLoading(false);
      }
    }
    load();
  }, [resetProfile]);

  // ─── Handlers ──────────────────────────────────────────────────────────────
  const onSaveProfile = async (data: ProfileForm) => {
    setProfileSaving(true);
    try {
      const updated = await updateProfile({
        full_name: data.full_name,
        phone_number: data.phone_number || null,
      });
      setProfile(updated);
      await refreshUser();
      toast.success('Profile updated successfully');
    } catch {
      toast.error('Failed to save profile');
    } finally {
      setProfileSaving(false);
    }
  };

  const onChangePassword = async (data: PasswordForm) => {
    setPasswordSaving(true);
    try {
      await changePassword(data);
      resetPwd();
      toast.success('Password changed successfully');
    } catch (err: unknown) {
      const msg =
        (err as { response?: { data?: { detail?: string } } })?.response?.data?.detail ||
        'Failed to change password';
      toast.error(msg);
    } finally {
      setPasswordSaving(false);
    }
  };

  const onSaveNotifPrefs = async () => {
    if (!notifPrefs) return;
    setNotifSaving(true);
    try {
      const updated = await updateNotificationPreferences(notifPrefs);
      setNotifPrefs(updated);
      toast.success('Notification preferences saved');
    } catch {
      toast.error('Failed to save notification preferences');
    } finally {
      setNotifSaving(false);
    }
  };

  const onSavePrivacy = async () => {
    if (!privacy) return;
    setPrivacySaving(true);
    try {
      const updated = await updatePrivacySettings(privacy);
      setPrivacy(updated);
      toast.success('Privacy settings saved');
    } catch {
      toast.error('Failed to save privacy settings');
    } finally {
      setPrivacySaving(false);
    }
  };

  const onSaveReminders = async () => {
    if (!reminders) return;
    setReminderSaving(true);
    try {
      const updated = await updateReminderSettings(reminders);
      setReminders(updated);
      toast.success('Reminder settings saved');
    } catch {
      toast.error('Failed to save reminder settings');
    } finally {
      setReminderSaving(false);
    }
  };

  // ─── Render ────────────────────────────────────────────────────────────────
  return (
    <div className="settings-layout">
      <AppSidebar />

      <div className="settings-main">
        {/* Topbar */}
        <header className="settings-topbar">
          <h1 className="settings-topbar__title">Settings</h1>
          <UserProfileMenu variant="topbar" />
        </header>

        <div className="settings-body">
          {/* Left nav */}
          <aside className="settings-nav">
            {(
              [
                { id: 'profile',       label: 'Profile',            icon: 'person' },
                { id: 'password',      label: 'Password',           icon: 'lock' },
                { id: 'notifications', label: 'Notifications',      icon: 'notifications' },
                { id: 'privacy',       label: 'Privacy',            icon: 'shield' },
                { id: 'reminders',     label: 'Reminders',          icon: 'alarm' },
              ] as { id: Section; label: string; icon: string }[]
            ).map(({ id, label, icon }) => (
              <button
                key={id}
                type="button"
                className={`settings-nav__item ${activeSection === id ? 'settings-nav__item--active' : ''}`}
                onClick={() => setActiveSection(id)}
              >
                <span className="material-symbols-outlined">{icon}</span>
                {label}
              </button>
            ))}
          </aside>

          {/* Content panel */}
          <div className="settings-panel">
            {/* ── PROFILE ─────────────────────────────────────────────────── */}
            {activeSection === 'profile' && (
              <section className="settings-section">
                <div className="settings-section__header">
                  <h2>Profile Information</h2>
                  <p>Update your name and contact details</p>
                </div>

                {profileLoading ? (
                  <div className="settings-skeleton">
                    <div className="skeleton-row" />
                    <div className="skeleton-row" />
                    <div className="skeleton-row skeleton-row--short" />
                  </div>
                ) : (
                  <form onSubmit={handleProfileSubmit(onSaveProfile)} className="settings-form">
                    <div className="settings-avatar-row">
                      <div className="settings-avatar-preview">
                        {profile?.profile_image ? (
                          <img src={profile.profile_image} alt="Profile" />
                        ) : (
                          <span className="material-symbols-outlined">person</span>
                        )}
                      </div>
                      <div>
                        <p className="settings-avatar-name">{profile?.full_name}</p>
                        <p className="settings-avatar-email">{user?.email}</p>
                      </div>
                    </div>

                    <div className="form-group">
                      <label className="form-label" htmlFor="full_name">Full Name</label>
                      <input
                        id="full_name"
                        className={`form-input ${profileErrors.full_name ? 'form-input--error' : ''}`}
                        placeholder="e.g. Jane Doe"
                        {...regProfile('full_name')}
                      />
                      {profileErrors.full_name && (
                        <p className="form-error">{profileErrors.full_name.message}</p>
                      )}
                    </div>

                    <div className="form-group">
                      <label className="form-label" htmlFor="email_display">Email Address</label>
                      <input
                        id="email_display"
                        className="form-input form-input--readonly"
                        value={user?.email ?? ''}
                        readOnly
                      />
                      <p className="form-hint">Email address cannot be changed here.</p>
                    </div>

                    <div className="form-group">
                      <label className="form-label" htmlFor="phone_number">Phone Number</label>
                      <input
                        id="phone_number"
                        className="form-input"
                        placeholder="+1 555 000 0000"
                        {...regProfile('phone_number')}
                      />
                    </div>

                    <button
                      type="submit"
                      className="btn-primary"
                      disabled={profileSaving}
                    >
                      {profileSaving ? 'Saving…' : 'Save Changes'}
                    </button>
                  </form>
                )}
              </section>
            )}

            {/* ── PASSWORD ─────────────────────────────────────────────────── */}
            {activeSection === 'password' && (
              <section className="settings-section">
                <div className="settings-section__header">
                  <h2>Change Password</h2>
                  <p>Choose a strong password to protect your vault</p>
                </div>

                <form onSubmit={handlePwdSubmit(onChangePassword)} className="settings-form">
                  <div className="form-group">
                    <label className="form-label" htmlFor="current_password">Current Password</label>
                    <input
                      id="current_password"
                      type="password"
                      className={`form-input ${pwdErrors.current_password ? 'form-input--error' : ''}`}
                      {...regPwd('current_password')}
                    />
                    {pwdErrors.current_password && (
                      <p className="form-error">{pwdErrors.current_password.message}</p>
                    )}
                  </div>

                  <div className="form-group">
                    <label className="form-label" htmlFor="new_password">New Password</label>
                    <input
                      id="new_password"
                      type="password"
                      className={`form-input ${pwdErrors.new_password ? 'form-input--error' : ''}`}
                      {...regPwd('new_password')}
                    />
                    {pwdErrors.new_password && (
                      <p className="form-error">{pwdErrors.new_password.message}</p>
                    )}
                  </div>

                  <div className="form-group">
                    <label className="form-label" htmlFor="confirm_password">Confirm New Password</label>
                    <input
                      id="confirm_password"
                      type="password"
                      className={`form-input ${pwdErrors.confirm_password ? 'form-input--error' : ''}`}
                      {...regPwd('confirm_password')}
                    />
                    {pwdErrors.confirm_password && (
                      <p className="form-error">{pwdErrors.confirm_password.message}</p>
                    )}
                  </div>

                  <button type="submit" className="btn-primary" disabled={passwordSaving}>
                    {passwordSaving ? 'Changing…' : 'Change Password'}
                  </button>
                </form>
              </section>
            )}

            {/* ── NOTIFICATIONS ────────────────────────────────────────────── */}
            {activeSection === 'notifications' && (
              <section className="settings-section">
                <div className="settings-section__header">
                  <h2>Notification Preferences</h2>
                  <p>Choose how VaultPass alerts you</p>
                </div>

                {!notifPrefs ? (
                  <div className="settings-skeleton">
                    {[0, 1, 2, 3].map((i) => <div key={i} className="skeleton-row" />)}
                  </div>
                ) : (
                  <div className="settings-form">
                    {(
                      [
                        { key: 'email_notifications',    label: 'Email Notifications',    hint: 'Receive alerts via email' },
                        { key: 'push_notifications',     label: 'Push Notifications',     hint: 'Browser push alerts' },
                        { key: 'document_expiry_alerts', label: 'Document Expiry Alerts', hint: 'Get warned before documents expire' },
                        { key: 'share_activity_alerts',  label: 'Share Activity Alerts',  hint: 'When your shared links are accessed' },
                        { key: 'login_alerts',           label: 'Login Alerts',           hint: 'Notify on new sign-ins' },
                      ] as { key: keyof NotificationPreferences; label: string; hint: string }[]
                    ).map(({ key, label, hint }) => (
                      <label key={key} className="settings-toggle">
                        <div>
                          <p className="settings-toggle__label">{label}</p>
                          <p className="settings-toggle__hint">{hint}</p>
                        </div>
                        <input
                          type="checkbox"
                          className="toggle-checkbox"
                          checked={!!notifPrefs[key]}
                          onChange={(e) =>
                            setNotifPrefs((prev) => prev ? { ...prev, [key]: e.target.checked } : prev)
                          }
                        />
                      </label>
                    ))}

                    <button className="btn-primary" onClick={onSaveNotifPrefs} disabled={notifSaving}>
                      {notifSaving ? 'Saving…' : 'Save Preferences'}
                    </button>
                  </div>
                )}
              </section>
            )}

            {/* ── PRIVACY ──────────────────────────────────────────────────── */}
            {activeSection === 'privacy' && (
              <section className="settings-section">
                <div className="settings-section__header">
                  <h2>Privacy Settings</h2>
                  <p>Control who can see your profile</p>
                </div>

                {!privacy ? (
                  <div className="settings-skeleton">
                    {[0, 1].map((i) => <div key={i} className="skeleton-row" />)}
                  </div>
                ) : (
                  <div className="settings-form">
                    {(
                      [
                        { key: 'show_profile_to_contacts', label: 'Show Profile to Contacts', hint: 'Trusted contacts can see your name and email' },
                        { key: 'allow_emergency_access',   label: 'Allow Emergency Access',   hint: 'Designated contacts can request emergency vault access' },
                      ] as { key: keyof PrivacySettings; label: string; hint: string }[]
                    ).map(({ key, label, hint }) => (
                      <label key={key} className="settings-toggle">
                        <div>
                          <p className="settings-toggle__label">{label}</p>
                          <p className="settings-toggle__hint">{hint}</p>
                        </div>
                        <input
                          type="checkbox"
                          className="toggle-checkbox"
                          checked={!!privacy[key]}
                          onChange={(e) =>
                            setPrivacy((prev) => prev ? { ...prev, [key]: e.target.checked } : prev)
                          }
                        />
                      </label>
                    ))}
                    <button className="btn-primary" onClick={onSavePrivacy} disabled={privacySaving}>
                      {privacySaving ? 'Saving…' : 'Save Privacy Settings'}
                    </button>
                  </div>
                )}
              </section>
            )}

            {/* ── REMINDERS ────────────────────────────────────────────────── */}
            {activeSection === 'reminders' && (
              <section className="settings-section">
                <div className="settings-section__header">
                  <h2>Reminder Settings</h2>
                  <p>Configure how early and how often you are reminded about expiring documents</p>
                </div>

                {!reminders ? (
                  <div className="settings-skeleton">
                    <div className="skeleton-row" />
                    <div className="skeleton-row skeleton-row--short" />
                  </div>
                ) : (
                  <div className="settings-form">
                    <div className="form-group">
                      <label className="form-label" htmlFor="expiry_days">
                        Remind me (days before expiry)
                      </label>
                      <input
                        id="expiry_days"
                        type="number"
                        min={1}
                        max={365}
                        className="form-input"
                        value={reminders.expiry_reminder_days}
                        onChange={(e) =>
                          setReminders((prev) =>
                            prev ? { ...prev, expiry_reminder_days: Number(e.target.value) } : prev
                          )
                        }
                      />
                    </div>

                    <div className="form-group">
                      <label className="form-label" htmlFor="reminder_freq">Reminder Frequency</label>
                      <select
                        id="reminder_freq"
                        className="form-input"
                        value={reminders.reminder_frequency}
                        onChange={(e) =>
                          setReminders((prev) =>
                            prev
                              ? { ...prev, reminder_frequency: e.target.value as ReminderSettings['reminder_frequency'] }
                              : prev
                          )
                        }
                      >
                        <option value="daily">Daily</option>
                        <option value="weekly">Weekly</option>
                        <option value="monthly">Monthly</option>
                      </select>
                    </div>

                    <button className="btn-primary" onClick={onSaveReminders} disabled={reminderSaving}>
                      {reminderSaving ? 'Saving…' : 'Save Reminders'}
                    </button>
                  </div>
                )}
              </section>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
