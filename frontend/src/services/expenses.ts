import api from './api';
import type { Expense, Comment, Reaction } from '@/types';

export interface CreateExpenseData {
  group_id: string;
  description: string;
  amount: number;
  date: string;
  payer_id: string;
  split_type: 'equal' | 'unequal' | 'shares' | 'percentage';
  category?: string;
  notes?: string;
  participant_ids?: string[];
  splits?: Array<{
    user_id: string;
    amount?: number;
    shares?: number;
    percentage?: number;
  }>;
}

export interface UpdateExpenseData {
  description?: string;
  amount?: number;
  date?: string;
  payer_id?: string;
  split_type?: 'equal' | 'unequal' | 'shares' | 'percentage';
  category?: string;
  notes?: string;
  participant_ids?: string[];
  splits?: Array<{
    user_id: string;
    amount?: number;
    shares?: number;
    percentage?: number;
  }>;
}

export interface ExpenseFilters {
  category?: string;
  payer_id?: string;
  start_date?: string;
  end_date?: string;
  search?: string;
}

export interface ExpenseListResponse {
  expenses: Expense[];
  total: number;
  page: number;
  per_page: number;
  total_pages: number;
}

export const expenseService = {
  async getExpenses(
    groupId: string,
    page = 1,
    perPage = 20,
    filters?: ExpenseFilters
  ): Promise<ExpenseListResponse> {
    const params = new URLSearchParams({
      group_id: groupId,
      page: page.toString(),
      per_page: perPage.toString(),
    });

    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }

    const { data } = await api.get<ExpenseListResponse>(`/expenses?${params}`);
    return data;
  },

  async getExpense(expenseId: string): Promise<Expense> {
    const { data } = await api.get<Expense>(`/expenses/${expenseId}`);
    return data;
  },

  async createExpense(expenseData: CreateExpenseData): Promise<Expense> {
    const { data } = await api.post<Expense>('/expenses', expenseData);
    return data;
  },

  async updateExpense(expenseId: string, updates: UpdateExpenseData): Promise<Expense> {
    const { data } = await api.patch<Expense>(`/expenses/${expenseId}`, updates);
    return data;
  },

  async deleteExpense(expenseId: string): Promise<void> {
    await api.delete(`/expenses/${expenseId}`);
  },

  async uploadReceipt(expenseId: string, file: File): Promise<Expense> {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post<Expense>(`/expenses/${expenseId}/receipt`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },

  // Comments
  async getComments(expenseId: string): Promise<Comment[]> {
    const { data } = await api.get<Comment[]>(`/expenses/${expenseId}/comments`);
    return data;
  },

  async createComment(expenseId: string, content: string, parentId?: string): Promise<Comment> {
    const { data } = await api.post<Comment>(`/expenses/${expenseId}/comments`, {
      content,
      parent_id: parentId,
    });
    return data;
  },

  async updateComment(expenseId: string, commentId: string, content: string): Promise<Comment> {
    const { data } = await api.patch<Comment>(`/expenses/${expenseId}/comments/${commentId}`, {
      content,
    });
    return data;
  },

  async deleteComment(expenseId: string, commentId: string): Promise<void> {
    await api.delete(`/expenses/${expenseId}/comments/${commentId}`);
  },

  // Reactions
  async getReactions(expenseId: string): Promise<Reaction[]> {
    const { data } = await api.get<Reaction[]>(`/expenses/${expenseId}/reactions`);
    return data;
  },

  async addReaction(expenseId: string, emoji: string): Promise<void> {
    await api.post(`/expenses/${expenseId}/reactions`, { emoji });
  },

  async removeReaction(expenseId: string, emoji: string): Promise<void> {
    await api.delete(`/expenses/${expenseId}/reactions/${encodeURIComponent(emoji)}`);
  },
};
