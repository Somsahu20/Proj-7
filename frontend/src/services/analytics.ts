import api from './api';
import type { GroupAnalyticsResponse, FriendsAnalyticsResponse, TimePeriod } from '@/types/analytics';

export const analyticsService = {
  async getGroupAnalytics(groupId: string, period: TimePeriod = '30d'): Promise<GroupAnalyticsResponse> {
    const { data } = await api.get<GroupAnalyticsResponse>(
      `/analytics/group/${groupId}?period=${period}`
    );
    return data;
  },

  async getFriendsAnalytics(period: TimePeriod = '30d'): Promise<FriendsAnalyticsResponse> {
    const { data } = await api.get<FriendsAnalyticsResponse>(
      `/analytics/friends?period=${period}`
    );
    return data;
  },
};
