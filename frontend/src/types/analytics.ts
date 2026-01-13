// Analytics Types

export type TimePeriod = '7d' | '30d' | '3m' | '1y';

export interface CategorySpending {
  category: string;
  amount: number;
  percentage: number;
  expense_count: number;
}

export interface SpendingDataPoint {
  date: string;
  amount: number;
  expense_count: number;
}

export interface MemberContribution {
  user_id: string;
  user_name: string;
  profile_picture?: string;
  total_paid: number;
  total_share: number;
  net_contribution: number;
}

export interface FriendSpending {
  friend_id: string;
  friend_name: string;
  profile_picture?: string;
  total_spent: number;
  expense_count: number;
}

export interface GroupAnalyticsResponse {
  group_id: string;
  group_name: string;
  period: string;
  start_date: string;
  end_date: string;
  total_spending: number;
  expense_count: number;
  category_breakdown: CategorySpending[];
  spending_over_time: SpendingDataPoint[];
  member_contributions: MemberContribution[];
  average_expense: number;
  top_category?: string;
}

export interface FriendsAnalyticsResponse {
  period: string;
  start_date: string;
  end_date: string;
  total_spending: number;
  expense_count: number;
  category_breakdown: CategorySpending[];
  spending_over_time: SpendingDataPoint[];
  friend_breakdown: FriendSpending[];
  average_expense: number;
  top_category?: string;
}
