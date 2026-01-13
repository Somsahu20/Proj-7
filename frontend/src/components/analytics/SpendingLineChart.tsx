import {
  AreaChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { format, parseISO } from 'date-fns';
import { formatCurrency } from '@/lib/utils';
import type { SpendingDataPoint, TimePeriod } from '@/types/analytics';

interface SpendingLineChartProps {
  data: SpendingDataPoint[];
  period: TimePeriod;
}

export function SpendingLineChart({ data, period }: SpendingLineChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-[300px] items-center justify-center text-muted-foreground">
        No spending data available
      </div>
    );
  }

  // Format dates based on period
  const getDateFormat = () => {
    switch (period) {
      case '7d':
        return 'EEE'; // Mon, Tue, etc.
      case '30d':
        return 'MMM d'; // Jan 1
      case '3m':
      case '1y':
        return 'MMM d'; // Jan 1
      default:
        return 'MMM d';
    }
  };

  const chartData = data.map((item) => ({
    date: item.date,
    formattedDate: format(parseISO(item.date), getDateFormat()),
    amount: Number(item.amount),
    count: item.expense_count,
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <AreaChart data={chartData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
        <defs>
          <linearGradient id="colorAmount" x1="0" y1="0" x2="0" y2="1">
            <stop offset="5%" stopColor="#22c55e" stopOpacity={0.8} />
            <stop offset="95%" stopColor="#22c55e" stopOpacity={0} />
          </linearGradient>
        </defs>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis
          dataKey="formattedDate"
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
          formatter={(value) => [formatCurrency(Number(value)), 'Amount']}
          labelFormatter={(_, payload) => {
            if (payload && payload[0]) {
              return format(parseISO(payload[0].payload.date), 'MMMM d, yyyy');
            }
            return '';
          }}
        />
        <Area
          type="monotone"
          dataKey="amount"
          stroke="#22c55e"
          fillOpacity={1}
          fill="url(#colorAmount)"
        />
      </AreaChart>
    </ResponsiveContainer>
  );
}
