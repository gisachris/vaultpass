interface NotificationPaginationProps {
  page: number;
  pages: number;
  onPrevious: () => void;
  onNext: () => void;
  loading: boolean;
}

export function NotificationPagination({ page, pages, onPrevious, onNext, loading }: NotificationPaginationProps) {
  return (
    <div className="notification-pagination">
      <button type="button" className="button button-secondary" onClick={onPrevious} disabled={page <= 1 || loading}>
        Previous
      </button>
      <span>
        Page {page} of {pages}
      </span>
      <button type="button" className="button button-secondary" onClick={onNext} disabled={page >= pages || loading}>
        Next
      </button>
    </div>
  );
}
