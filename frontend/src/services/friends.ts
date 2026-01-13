import api from './api';
import { Friendship, FriendList } from '../types';

export const friendsService = {
  async getFriends(): Promise<FriendList> {
    const { data } = await api.get<FriendList>('/friends');
    return data;
  },

  async sendFriendRequest(email: string): Promise<Friendship> {
    const { data } = await api.post<Friendship>('/friends/request', { email });
    return data;
  },

  async acceptFriendRequest(friendshipId: string): Promise<Friendship> {
    const { data } = await api.post<Friendship>(`/friends/${friendshipId}/accept`);
    return data;
  },

  async declineFriendRequest(friendshipId: string): Promise<void> {
    await api.post(`/friends/${friendshipId}/decline`);
  },

  async removeFriend(friendshipId: string): Promise<void> {
    await api.delete(`/friends/${friendshipId}`);
  },

  async getFriendGroup(friendId: string): Promise<{ group_id: string }> {
    const { data } = await api.get<{ group_id: string }>(`/friends/${friendId}/group`);
    return data;
  },
};
