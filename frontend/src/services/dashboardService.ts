import { api } from '../lib/api';
import { DashboardData } from '../types/dashboard';

const DASHBOARD_PATH = '/dashboard';

export async function fetchDashboard(): Promise<DashboardData> {
  const response = await api.get<DashboardData>(DASHBOARD_PATH);
  return response.data;
}
