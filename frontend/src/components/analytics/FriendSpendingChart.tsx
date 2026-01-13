import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Cell,
} from 'recharts';
import { formatCurrency } from '@/lib/utils';
import type { FriendSpending } from '@/types/analytics';

interface FriendSpendingChartProps {
  data: FriendSpending[];
}

const COLORS = [
  '#22c55e',
  '#3b82f6',
  '#a855f7',
  '#f97316',
  '#ec4899',
  '#14b8a6',
  '#eab308',
  '#6366f1',
];

export function FriendSpendingChart({ data }: FriendSpendingChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-[300px] items-center justify-center text-muted-foreground">
        No friend spending data available
      </div>
    );
  }

  const chartData = data.map((friend, index) => ({
    name: friend.friend_name.split(' ')[0], // First name
    fullName: friend.friend_name,
    amount: Number(friend.total_spent),
    count: friend.expense_count,
    fill: COLORS[index % COLORS.length],
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis
          dataKey="name"
          tick={{ fontSize: 12 }}
          tickLine={false}
          axisLine={false}
        />
        <YAxis
          tickFormatter={(value) => `$${value}`}
          tick={{ fontSize: 12 }}
          tickLine={false}
          axisLine={false}
        />
        <Tooltip
          formatter={(value) => [formatCurrency(Number(value)), 'Total Spent']}
          labelFormatter={(_, payload) => {
            if (payload && payload[0]) {
              const { fullName, count } = payload[0].payload;
              return `${fullName} (${count} expenses)`;
            }
            return '';
          }}
        />
        <Bar dataKey="amount" radius={[4, 4, 0, 0]}>
          {chartData.map((entry, index) => (
            <Cell key={`cell-${index}`} fill={entry.fill} />
          ))}
        </Bar>
      </BarChart>
    </ResponsiveContainer>
  );
}
