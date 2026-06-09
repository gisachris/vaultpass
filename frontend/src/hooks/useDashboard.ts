import { useEffect, useState } from 'react';
import { AxiosError } from 'axios';
import { fetchDashboard } from '../services/dashboardService';
import { DashboardData } from '../types/dashboard';

interface UseDashboardResult {
  data: DashboardData | null;
  loading: boolean;
  error: string | null;
  refresh: () => Promise<void>;
}

export function useDashboard(): UseDashboardResult {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadDashboard = async () => {
    setLoading(true);
    setError(null);

    try {
      const dashboardData = await fetchDashboard();
      setData(dashboardData);
    } catch (err) {
      if (err instanceof AxiosError) {
        setError(err.response?.data?.detail || err.message || 'Unable to load dashboard.');
      } else {
        setError('Unable to load dashboard.');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDashboard();
  }, []);

  const refresh = async () => {
    await loadDashboard();
  };

  return {
    data,
    loading,
    error,
    refresh,
  };
}
