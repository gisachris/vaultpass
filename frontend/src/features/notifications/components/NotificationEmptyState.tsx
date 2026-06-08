export function NotificationEmptyState() {
  return (
    <div className="notification-empty-state">
      <span className="material-symbols-outlined notification-empty-state__icon">notifications</span>
      <div>
        <h3>No notifications yet</h3>
        <p>There are no alerts in your inbox right now. Check back later for updates.</p>
      </div>
    </div>
  );
}
