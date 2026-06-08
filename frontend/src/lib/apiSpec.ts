import apiSpec from '../../../api.json';

type ApiEndpoint = {
  method: string;
  path: string;
  summary: string;
  description: string;
};

type ApiService = {
  name: string;
  base_path: string;
  endpoints: ApiEndpoint[];
};

function findService(name: string): ApiService {
  const modules = (apiSpec as any).modules as ApiService[] | undefined;
  const services = (apiSpec as any).services as ApiService[] | undefined;

  const entries = modules ?? services;
  if (!entries) {
    throw new Error('Invalid API specification: missing modules or services array.');
  }

  const service = entries.find((item) => item.name === name);
  if (!service) {
    throw new Error(`API specification does not contain service ${name}.`);
  }

  return service;
}

function normalizeServiceBasePath(path: string) {
  let normalized = path.trim();

  if (normalized === '/api') {
    normalized = '';
  } else if (normalized.startsWith('/api/')) {
    normalized = normalized.slice(5);
  }

  return normalized.replace(/^\/+/, '').replace(/\/+$/, '');
}

function buildServiceUrl(basePath: string, endpointPath: string) {
  const normalizedBase = basePath.replace(/\/+$/, '');
  const normalizedEndpoint = endpointPath.replace(/^\/+/, '');
  return normalizedEndpoint ? `${normalizedBase}/${normalizedEndpoint}` : normalizedBase;
}

const notificationsService = findService('Notifications');
const notificationsBasePath = normalizeServiceBasePath(notificationsService.base_path);

export const notificationApiPaths = {
  list: notificationsBasePath,
  unreadCount: buildServiceUrl(notificationsBasePath, '/unread-count'),
  markAllRead: buildServiceUrl(notificationsBasePath, '/read-all'),
  details: (notificationId: string) => buildServiceUrl(notificationsBasePath, `/${notificationId}`),
  markRead: (notificationId: string) => buildServiceUrl(notificationsBasePath, `/${notificationId}/read`),
  markUnread: (notificationId: string) => buildServiceUrl(notificationsBasePath, `/${notificationId}/unread`),
  deleteNotification: (notificationId: string) => buildServiceUrl(notificationsBasePath, `/${notificationId}`),
  deleteAll: notificationsBasePath,
};
