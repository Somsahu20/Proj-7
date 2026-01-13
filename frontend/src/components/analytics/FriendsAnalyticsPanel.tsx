import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { analyticsService } from '@/services/analytics';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Loader2 } from 'lucide-react';
import { TimePeriodSelector } from './TimePeriodSelector';
import { CategoryPieChart } from './CategoryPieChart';
import { SpendingLineChart } from './SpendingLineChart';
import { FriendSpendingChart } from './FriendSpendingChart';
import { AnalyticsSummaryCards } from './AnalyticsSummaryCards';
import { AnalyticsEmptyState } from './AnalyticsEmptyState';
import type { TimePeriod } from '@/types/analytics';

export function FriendsAnalyticsPanel() {
  const [period, setPeriod] = useState<TimePeriod>('30d');

  const { data, isLoading, error } = useQuery({
    queryKey: ['friends-analytics', period],
    queryFn: () => analyticsService.getFriendsAnalytics(period),
    staleTime: 5 * 60 * 1000, // 5 minutes
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error) {
    return (
      <Card>
        <CardContent className="py-8 text-center text-red-600">
          Failed to load analytics. Please try again.
        </CardContent>
      </Card>
    );
  }

  if (!data || data.expense_count === 0) {
    return (
      <div className="space-y-4">
        <TimePeriodSelector value={period} onChange={setPeriod} />
        <AnalyticsEmptyState message="Add expenses with friends to see spending analytics here." />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <TimePeriodSelector value={period} onChange={setPeriod} />

      <AnalyticsSummaryCards
        totalSpending={data.total_spending}
        expenseCount={data.expense_count}
        averageExpense={data.average_expense}
        topCategory={data.top_category}
      />

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Spending by Category</CardTitle>
            <CardDescription>How friend expenses are distributed</CardDescription>
          </CardHeader>
          <CardContent>
            <CategoryPieChart data={data.category_breakdown} />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Spending Over Time</CardTitle>
            <CardDescription>Daily spending trends with friends</CardDescription>
          </CardHeader>
          <CardContent>
            <SpendingLineChart data={data.spending_over_time} period={period} />
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Spending by Friend</CardTitle>
          <CardDescription>Total expenses shared with each friend</CardDescription>
        </CardHeader>
        <CardContent>
          <FriendSpendingChart data={data.friend_breakdown} />
        </CardContent>
      </Card>
    </div>
  );
}
