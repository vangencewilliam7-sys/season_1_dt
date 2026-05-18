import { ApiClient } from '../client';

export const DashboardService = {
  getHealth: () => ApiClient.get('/health'),
  getStats: async (expertId = 'demo') => {
    const res = await fetch(`/api/stats?expertId=${expertId}`);
    if (!res.ok) throw new Error('Failed to fetch stats');
    return res.json();
  }
};
