import { Card, CardContent } from '@/components/ui/card';
import { formatCurrency } from '@/lib/utils';
import { DollarSign, Receipt, TrendingUp, Tag } from 'lucide-react';

interface AnalyticsSummaryCardsProps {
  totalSpending: number;
  expenseCount: number;
  averageExpense: number;
  topCategory?: string;
}

export function AnalyticsSummaryCards({
  totalSpending,
  expenseCount,
  averageExpense,
  topCategory,
}: AnalyticsSummaryCardsProps) {
  const cards = [
    {
      title: 'Total Spending',
      value: formatCurrency(totalSpending),
      icon: DollarSign,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      title: 'Total Expenses',
      value: expenseCount.toString(),
      icon: Receipt,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      title: 'Average Expense',
      value: formatCurrency(averageExpense),
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      title: 'Top Category',
      value: topCategory || 'N/A',
      icon: Tag,
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-4">
      {cards.map((card) => (
        <Card key={card.title}>
          <CardContent className="flex items-center gap-4 p-4">
            <div className={`rounded-full p-2 ${card.bgColor}`}>
              <card.icon className={`h-5 w-5 ${card.color}`} />
            </div>
            <div>
              <p className="text-sm text-muted-foreground">{card.title}</p>
              <p className="text-xl font-semibold">{card.value}</p>
            </div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
