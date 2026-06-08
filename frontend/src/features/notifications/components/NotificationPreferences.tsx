import { useEffect, useState } from 'react';

const STORAGE_KEY = 'vaultpass_notification_preferences';

interface PreferenceState {
  emailSummaries: boolean;
  pushNotifications: boolean;
  criticalAlertsOnly: boolean;
}

const defaultPreferences: PreferenceState = {
  emailSummaries: true,
  pushNotifications: true,
  criticalAlertsOnly: false,
};

export function NotificationPreferences() {
  const [preferences, setPreferences] = useState<PreferenceState>(defaultPreferences);

  useEffect(() => {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored) {
      try {
        setPreferences(JSON.parse(stored));
      } catch {
        setPreferences(defaultPreferences);
      }
    }
  }, []);

  useEffect(() => {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(preferences));
  }, [preferences]);

  const toggle = (key: keyof PreferenceState) => {
    setPreferences((current) => ({
      ...current,
      [key]: !current[key],
    }));
  };

  return (
    <div className="notification-preferences">
      <h4>Preferences</h4>
      <p>Manage how and when you receive alerts from VaultPass.</p>
      <div className="notification-preferences__item">
        <span>Email Summaries</span>
        <button type="button" className={`toggle ${preferences.emailSummaries ? 'toggle--active' : ''}`} onClick={() => toggle('emailSummaries')}>
          <span className="toggle__thumb" />
        </button>
      </div>
      <div className="notification-preferences__item">
        <span>Push Notifications</span>
        <button type="button" className={`toggle ${preferences.pushNotifications ? 'toggle--active' : ''}`} onClick={() => toggle('pushNotifications')}>
          <span className="toggle__thumb" />
        </button>
      </div>
      <div className="notification-preferences__item">
        <span>Critical Alerts Only</span>
        <button type="button" className={`toggle ${preferences.criticalAlertsOnly ? 'toggle--active' : ''}`} onClick={() => toggle('criticalAlertsOnly')}>
          <span className="toggle__thumb" />
        </button>
      </div>
      <a className="notification-preferences__link" href="#">
        View all notification settings <span className="material-symbols-outlined">arrow_forward</span>
      </a>
    </div>
  );
}
