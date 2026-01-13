import api from './api';
import type { Dispute, DisputeVote } from '@/types';

export interface CreateDisputeData {
  expense_id?: string;
  payment_id?: string;
  reason: string;
  description: string;
  evidence_urls?: string[];
}

export interface VoteOnDisputeData {
  vote: 'approve' | 'reject' | 'abstain';
  comment?: string;
}

export interface ResolveDisputeData {
  resolution: 'upheld' | 'dismissed' | 'modified';
  resolution_notes?: string;
}

export const disputeService = {
  async getDisputes(status?: string, groupId?: string): Promise<Dispute[]> {
    const params = new URLSearchParams();
    if (status) params.append('status', status);
    if (groupId) params.append('group_id', groupId);
    const query = params.toString();
    const { data } = await api.get<Dispute[]>(`/disputes${query ? `?${query}` : ''}`);
    return data;
  },

  async getDispute(disputeId: string): Promise<Dispute> {
    const { data } = await api.get<Dispute>(`/disputes/${disputeId}`);
    return data;
  },

  async createDispute(payload: CreateDisputeData): Promise<Dispute> {
    const { data } = await api.post<Dispute>('/disputes', payload);
    return data;
  },

  async voteOnDispute(disputeId: string, payload: VoteOnDisputeData): Promise<DisputeVote> {
    const { data } = await api.post<DisputeVote>(`/disputes/${disputeId}/vote`, payload);
    return data;
  },

  async resolveDispute(disputeId: string, payload: ResolveDisputeData): Promise<Dispute> {
    const { data } = await api.post<Dispute>(`/disputes/${disputeId}/resolve`, payload);
    return data;
  },
};
