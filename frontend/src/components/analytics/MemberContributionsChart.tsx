import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  Legend,
} from 'recharts';
import { formatCurrency } from '@/lib/utils';
import type { MemberContribution } from '@/types/analytics';

interface MemberContributionsChartProps {
  data: MemberContribution[];
}

export function MemberContributionsChart({ data }: MemberContributionsChartProps) {
  if (!data || data.length === 0) {
    return (
      <div className="flex h-[300px] items-center justify-center text-muted-foreground">
        No member contribution data available
      </div>
    );
  }

  const chartData = data.map((member) => ({
    name: member.user_name.split(' ')[0], // First name only for chart
    fullName: member.user_name,
    paid: Number(member.total_paid),
    share: Number(member.total_share),
    net: Number(member.net_contribution),
  }));

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={chartData} layout="vertical" margin={{ top: 10, right: 30, left: 60, bottom: 0 }}>
        <CartesianGrid strokeDasharray="3 3" className="stroke-muted" />
        <XAxis
          type="number"
          tickFormatter={(value) => `$${value}`}
          tick={{ fontSize: 12 }}
        />
        <YAxis
          type="category"
          dataKey="name"
          tick={{ fontSize: 12 }}
          width={50}
        />
        <Tooltip
          formatter={(value, name) => [
            formatCurrency(Number(value)),
            name === 'paid' ? 'Total Paid' : 'Their Share',
          ]}
          labelFormatter={(_, payload) => {
            if (payload && payload[0]) {
              return payload[0].payload.fullName;
            }
            return '';
          }}
        />
        <Legend />
        <Bar dataKey="paid" name="Paid" fill="#22c55e" radius={[0, 4, 4, 0]} />
        <Bar dataKey="share" name="Share" fill="#3b82f6" radius={[0, 4, 4, 0]} />
      </BarChart>
    </ResponsiveContainer>
  );
}
