import api from './api';
import type { Group, GroupDetail, Member, Invitation } from '@/types';

export interface CreateGroupData {
  name: string;
  description?: string;
  category: string;
}

export interface UpdateGroupData {
  name?: string;
  description?: string;
  category?: string;
  settings?: Record<string, unknown>;
}

export const groupService = {
  async getGroups(): Promise<Group[]> {
    const { data } = await api.get<Group[]>('/groups');
    return data;
  },

  async getGroup(groupId: string): Promise<GroupDetail> {
    const { data } = await api.get<GroupDetail>(`/groups/${groupId}`);
    return data;
  },

  async createGroup(groupData: CreateGroupData): Promise<Group> {
    const { data } = await api.post<Group>('/groups', groupData);
    return data;
  },

  async updateGroup(groupId: string, updates: UpdateGroupData): Promise<Group> {
    const { data } = await api.patch<Group>(`/groups/${groupId}`, updates);
    return data;
  },

  async deleteGroup(groupId: string): Promise<void> {
    await api.delete(`/groups/${groupId}`);
  },

  async uploadGroupImage(groupId: string, file: File): Promise<Group> {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post<Group>(`/groups/${groupId}/image`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Members
  async getMembers(groupId: string): Promise<Member[]> {
    const { data } = await api.get<Member[]>(`/groups/${groupId}/members`);
    return data;
  },

  async updateMemberRole(groupId: string, userId: string, role: 'admin' | 'member'): Promise<Member> {
    const { data } = await api.patch<Member>(`/groups/${groupId}/members/${userId}/role`, { role });
    return data;
  },

  async removeMember(groupId: string, userId: string): Promise<void> {
    await api.delete(`/groups/${groupId}/members/${userId}`);
  },

  // Invitations
  async getInvitations(groupId: string): Promise<Invitation[]> {
    const { data } = await api.get<Invitation[]>(`/groups/${groupId}/invitations`);
    return data;
  },

  async createInvitation(groupId: string, email: string): Promise<Invitation> {
    const { data } = await api.post<Invitation>(`/groups/${groupId}/invitations`, { email });
    return data;
  },

  async acceptInvitation(token: string): Promise<{ group_id: string }> {
    const { data } = await api.post<{ group_id: string }>('/groups/invitations/accept', { token });
    return data;
  },

  async cancelInvitation(groupId: string, invitationId: string): Promise<void> {
    await api.delete(`/groups/${groupId}/invitations/${invitationId}`);
  },

  // User's pending invitations
  async getMyInvitations(): Promise<Invitation[]> {
    const { data } = await api.get<Invitation[]>('/users/me/invitations');
    return data;
  },

  async acceptInvitationById(invitationId: string): Promise<{ group_id: string }> {
    const { data } = await api.post<{ group_id: string }>(`/users/me/invitations/${invitationId}/accept`);
    return data;
  },

  async declineInvitation(invitationId: string): Promise<void> {
    await api.post(`/users/me/invitations/${invitationId}/decline`);
  },
};
