import api from './api';
import type { Payment, PaymentProof } from '@/types';

export interface CreatePaymentData {
  group_id: string;
  receiver_id: string;
  amount: number;
  description?: string;
  payment_method?: string;
  date: string;
}

export interface PaymentListResponse {
  payments: Payment[];
  total: number;
  page: number;
  per_page: number;
}

export const paymentService = {
  async getPayments(
    groupId?: string,
    status?: string,
    page = 1,
    perPage = 20
  ): Promise<PaymentListResponse> {
    const params = new URLSearchParams({
      page: page.toString(),
      per_page: perPage.toString(),
    });

    if (groupId) params.append('group_id', groupId);
    if (status) params.append('status', status);

    const { data } = await api.get<PaymentListResponse>(`/payments?${params}`);
    return data;
  },

  async getPendingPayments(): Promise<Payment[]> {
    const { data } = await api.get<Payment[]>('/payments/pending');
    return data;
  },

  async getPayment(paymentId: string): Promise<Payment> {
    const { data } = await api.get<Payment>(`/payments/${paymentId}`);
    return data;
  },

  async createPayment(paymentData: CreatePaymentData): Promise<Payment> {
    const { data } = await api.post<Payment>('/payments', paymentData);
    return data;
  },

  async confirmPayment(paymentId: string): Promise<Payment> {
    const { data } = await api.post<Payment>(`/payments/${paymentId}/confirm`);
    return data;
  },

  async rejectPayment(paymentId: string, reason: string): Promise<Payment> {
    const { data } = await api.post<Payment>(`/payments/${paymentId}/reject`, { reason });
    return data;
  },

  async cancelPayment(paymentId: string, reason?: string): Promise<Payment> {
    const { data } = await api.post<Payment>(`/payments/${paymentId}/cancel`, { reason });
    return data;
  },

  async uploadProof(paymentId: string, file: File): Promise<PaymentProof> {
    const formData = new FormData();
    formData.append('file', file);
    const { data } = await api.post<PaymentProof>(`/payments/${paymentId}/proof`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    });
    return data;
  },
};
