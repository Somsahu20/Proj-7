import api from './api';
import type { Notification } from '@/types';

export interface NotificationListResponse {
  notifications: Notification[];
  unread_count: number;
  total: number;
  page: number;
  per_page: number;
}

export interface UnreadCountResponse {
  unread_count: number;
  by_type: Record<string, number>;
}

export const notificationService = {
  async getNotifications(
    page = 1,
    perPage = 20,
    unreadOnly = false
  ): Promise<NotificationListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });

    if (unreadOnly) params.append('unread_only', 'true');

    const { data } = await api.get<NotificationListResponse>(`/notifications?${params}`);
    return data;
  },

  async getUnreadCount(): Promise<UnreadCountResponse> {
    const { data } = await api.get<UnreadCountResponse>('/notifications/unread-count');
    return data;
  },

  async markAsRead(notificationIds: string[]): Promise<void> {
    await api.post('/notifications/mark-read', { notification_ids: notificationIds });
  },

  async markAllAsRead(): Promise<void> {
    await api.post('/notifications/mark-all-read');
  },

  async deleteNotification(notificationId: string): Promise<void> {
    await api.delete(`/notifications/${notificationId}`);
  },

  // SSE connection for real-time notifications
  createEventSource(): EventSource {
    const token = localStorage.getItem('token');
    return new EventSource(`/api/v1/notifications/stream/events?token=${token}`);
  },
};
