import api from './api';
import type { BalanceOverview, GroupBalance, SettlementSuggestion } from '@/types';

export interface GroupSettlementResponse {
  group_id: string;
  group_name: string;
  suggestions: SettlementSuggestion[];
  total_transactions: number;
  original_transactions: number;
}

export const balanceService = {
  async getBalances(): Promise<BalanceOverview> {
    const { data } = await api.get<BalanceOverview>('/balances');
    return data;
  },

  async getGroupBalance(groupId: string): Promise<GroupBalance> {
    const { data } = await api.get<GroupBalance>(`/balances/group/${groupId}`);
    return data;
  },

  async getSettlementSuggestions(groupId: string): Promise<GroupSettlementResponse> {
    const { data } = await api.get<GroupSettlementResponse>(`/balances/group/${groupId}/settlements`);
    return data;
  },
};
