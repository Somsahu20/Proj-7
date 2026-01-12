import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { balanceService } from '@/services/balances';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { formatCurrency, getInitials } from '@/lib/utils';
import { TrendingUp, TrendingDown, ArrowRight, Loader2 } from 'lucide-react';

export function BalancesPage() {
  const { data: balances, isLoading } = useQuery({
    queryKey: ['balances'],
    queryFn: balanceService.getBalances,
  });

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Balances</h1>
        <p className="text-muted-foreground">Your balance overview across all groups</p>
      </div>

      {/* Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Balance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-3xl font-bold ${
              (balances?.total_balance || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {formatCurrency(balances?.total_balance || 0)}
            </div>
            <p className="text-sm text-muted-foreground mt-1">
              {(balances?.total_balance || 0) >= 0 ? 'You are owed overall' : 'You owe overall'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingUp className="h-4 w-4 text-green-500" />
              You Are Owed
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-green-600">
              {formatCurrency(balances?.you_are_owed || 0)}
            </div>
            <p className="text-sm text-muted-foreground mt-1">From all groups combined</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <TrendingDown className="h-4 w-4 text-red-500" />
              You Owe
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-3xl font-bold text-red-600">
              {formatCurrency(balances?.you_owe || 0)}
            </div>
            <p className="text-sm text-muted-foreground mt-1">To all groups combined</p>
          </CardContent>
        </Card>
      </div>

      {/* Group Balances */}
      <Card>
        <CardHeader>
          <CardTitle>By Group</CardTitle>
          <CardDescription>Your balance in each group</CardDescription>
        </CardHeader>
        <CardContent>
          {!balances?.group_balances?.length ? (
            <div className="text-center py-8">
              <p className="text-muted-foreground">No balances to show</p>
              <Button asChild className="mt-4">
                <Link to="/groups">View Your Groups</Link>
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {balances.group_balances.map((gb) => (
                <div key={gb.group_id} className="border rounded-lg p-4">
                  <div className="flex items-center justify-between mb-4">
                    <Link to={`/groups/${gb.group_id}`} className="flex items-center gap-2 hover:underline">
                      <h3 className="font-semibold text-lg">{gb.group_name}</h3>
                      <ArrowRight className="h-4 w-4" />
                    </Link>
                    <span className={`text-lg font-bold ${
                      gb.your_total_balance >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {gb.your_total_balance >= 0 ? '+' : ''}{formatCurrency(gb.your_total_balance)}
                    </span>
                  </div>

                  {gb.balances.length > 0 && (
                    <div className="space-y-2">
                      {gb.balances.map((b) => (
                        <div key={b.user_id} className="flex items-center justify-between py-2 border-t">
                          <div className="flex items-center gap-3">
                            <Avatar className="h-8 w-8">
                              <AvatarImage src={b.profile_picture || ''} />
                              <AvatarFallback>{getInitials(b.user_name)}</AvatarFallback>
                            </Avatar>
                            <div>
                              <p className="font-medium">{b.user_name}</p>
                              <p className="text-xs text-muted-foreground">{b.user_email}</p>
                            </div>
                          </div>
                          <div className="flex items-center gap-3">
                            {b.balance > 0 ? (
                              <span className="text-green-600">owes you {formatCurrency(b.balance)}</span>
                            ) : (
                              <span className="text-red-600">you owe {formatCurrency(Math.abs(b.balance))}</span>
                            )}
                            {b.balance < 0 && (
                              <Button size="sm" asChild>
                                <Link to={`/payments/new?group=${gb.group_id}&to=${b.user_id}&amount=${Math.abs(b.balance)}`}>
                                  Settle
                                </Link>
                              </Button>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
