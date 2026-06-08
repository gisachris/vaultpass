import { NotificationReadFilter, NotificationType, NotificationSortDirection } from '../types/notification.types';

interface NotificationFiltersProps {
  filter: NotificationReadFilter;
  typeFilter: NotificationType | 'ALL';
  sorting: NotificationSortDirection;
  unreadCount: number;
  onFilterChange: (filter: NotificationReadFilter) => void;
  onTypeFilterChange: (type: NotificationType | 'ALL') => void;
  onSortingChange: (sorting: NotificationSortDirection) => void;
  onClearAll: () => void;
}

const statusFilters: Array<{ key: NotificationReadFilter; label: string }> = [
  { key: 'ALL', label: 'All' },
  { key: 'UNREAD', label: 'Unread' },
  { key: 'READ', label: 'Read' },
];

const typeFilters: Array<{ key: NotificationType | 'ALL'; label: string }> = [
  { key: 'ALL', label: 'All' },
  { key: 'INFO', label: 'Info' },
  { key: 'SUCCESS', label: 'Success' },
  { key: 'WARNING', label: 'Warning' },
  { key: 'ERROR', label: 'Error' },
];

export function NotificationFilters({
  filter,
  typeFilter,
  sorting,
  unreadCount,
  onFilterChange,
  onTypeFilterChange,
  onSortingChange,
  onClearAll,
}: NotificationFiltersProps) {
  return (
    <section className="notification-filters">
      <div className="notification-filters__header">
        <div>
          <h3>Filters</h3>
          <p>{unreadCount} unread notification{unreadCount === 1 ? '' : 's'}</p>
        </div>
        <button type="button" className="button button-secondary notification-filters__clear" onClick={onClearAll}>
          Clear All
        </button>
      </div>

      <div className="notification-filters__groups">
        <div className="notification-filter-group">
          <span>Status</span>
          <div className="notification-filter-buttons">
            {statusFilters.map((item) => (
              <button
                key={item.key}
                type="button"
                className={`notification-filter-button ${filter === item.key ? 'notification-filter-button--active' : ''}`}
                onClick={() => onFilterChange(item.key)}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <div className="notification-filter-group">
          <span>Type</span>
          <div className="notification-filter-buttons">
            {typeFilters.map((item) => (
              <button
                key={item.key}
                type="button"
                className={`notification-filter-button ${typeFilter === item.key ? 'notification-filter-button--active' : ''}`}
                onClick={() => onTypeFilterChange(item.key)}
              >
                {item.label}
              </button>
            ))}
          </div>
        </div>

        <div className="notification-filter-group notification-filter-group--sorting">
          <span>Sort</span>
          <button
            type="button"
            className={`notification-filter-button ${sorting === 'desc' ? 'notification-filter-button--active' : ''}`}
            onClick={() => onSortingChange('desc')}
          >
            Newest first
          </button>
          <button
            type="button"
            className={`notification-filter-button ${sorting === 'asc' ? 'notification-filter-button--active' : ''}`}
            onClick={() => onSortingChange('asc')}
          >
            Oldest first
          </button>
        </div>
      </div>
    </section>
  );
}
