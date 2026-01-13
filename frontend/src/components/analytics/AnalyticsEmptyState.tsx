import { Card, CardContent } from '@/components/ui/card';
import { BarChart3 } from 'lucide-react';

interface AnalyticsEmptyStateProps {
  message?: string;
}

export function AnalyticsEmptyState({ message }: AnalyticsEmptyStateProps) {
  return (
    <Card>
      <CardContent className="flex flex-col items-center justify-center py-12">
        <div className="rounded-full bg-muted p-4 mb-4">
          <BarChart3 className="h-8 w-8 text-muted-foreground" />
        </div>
        <h3 className="text-lg font-medium mb-2">No Analytics Data</h3>
        <p className="text-muted-foreground text-center max-w-md">
          {message || 'Add some expenses to see analytics and spending insights here.'}
        </p>
      </CardContent>
    </Card>
  );
}
