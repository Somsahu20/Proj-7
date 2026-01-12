import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { groupService } from '@/services/groups';
import { balanceService } from '@/services/balances';
import { paymentService } from '@/services/payments';
import { useAuthStore } from '@/store/authStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { formatCurrency, getInitials } from '@/lib/utils';
import { Plus, Users, TrendingUp, TrendingDown, ArrowRight, AlertCircle } from 'lucide-react';

export function DashboardPage() {
  const { user } = useAuthStore();

  const { data: groups = [], isLoading: groupsLoading } = useQuery({
    queryKey: ['groups'],
    queryFn: groupService.getGroups,
  });

  const { data: balances, isLoading: balancesLoading } = useQuery({
    queryKey: ['balances'],
    queryFn: balanceService.getBalances,
  });

  const { data: pendingPayments = [], isLoading: paymentsLoading } = useQuery({
    queryKey: ['pending-payments'],
    queryFn: paymentService.getPendingPayments,
  });

  const isLoading = groupsLoading || balancesLoading || paymentsLoading;

  return (
    <div className="space-y-6">
      {/* Welcome Section */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Welcome back, {user?.name?.split(' ')[0]}!</h1>
          <p className="text-muted-foreground">Here's an overview of your expenses</p>
        </div>
        <div className="flex gap-2">
          <Button asChild>
            <Link to="/groups/new">
              <Plus className="mr-2 h-4 w-4" />
              New Group
            </Link>
          </Button>
        </div>
      </div>

      {/* Balance Summary Cards */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total Balance</CardTitle>
            {balances && balances.total_balance >= 0 ? (
              <TrendingUp className="h-4 w-4 text-green-500" />
            ) : (
              <TrendingDown className="h-4 w-4 text-red-500" />
            )}
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${
              balances && balances.total_balance >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {balancesLoading ? '...' : formatCurrency(balances?.total_balance || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              {balances && balances.total_balance >= 0 ? 'You are owed overall' : 'You owe overall'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">You Are Owed</CardTitle>
            <TrendingUp className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-600">
              {balancesLoading ? '...' : formatCurrency(balances?.you_are_owed || 0)}
            </div>
            <p className="text-xs text-muted-foreground">From all groups</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">You Owe</CardTitle>
            <TrendingDown className="h-4 w-4 text-red-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {balancesLoading ? '...' : formatCurrency(balances?.you_owe || 0)}
            </div>
            <p className="text-xs text-muted-foreground">To all groups</p>
          </CardContent>
        </Card>
      </div>

      {/* Pending Payments Alert */}
      {pendingPayments.length > 0 && (
        <Card className="border-yellow-500">
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium flex items-center gap-2">
              <AlertCircle className="h-4 w-4 text-yellow-500" />
              Pending Payment Confirmations
            </CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-sm text-muted-foreground mb-2">
              You have {pendingPayments.length} payment(s) waiting for your confirmation
            </p>
            <Button variant="outline" size="sm" asChild>
              <Link to="/payments?status=pending">
                Review Payments
                <ArrowRight className="ml-2 h-4 w-4" />
              </Link>
            </Button>
          </CardContent>
        </Card>
      )}

      <div className="grid gap-6 md:grid-cols-2">
        {/* Groups */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Your Groups</CardTitle>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/groups">View All</Link>
              </Button>
            </div>
            <CardDescription>Groups you're part of</CardDescription>
          </CardHeader>
          <CardContent>
            {isLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-12 bg-muted animate-pulse rounded" />
                ))}
              </div>
            ) : groups.length === 0 ? (
              <div className="text-center py-6">
                <Users className="h-12 w-12 mx-auto text-muted-foreground mb-2" />
                <p className="text-muted-foreground">No groups yet</p>
                <Button size="sm" className="mt-2" asChild>
                  <Link to="/groups/new">Create your first group</Link>
                </Button>
              </div>
            ) : (
              <div className="space-y-3">
                {groups.slice(0, 5).map((group) => (
                  <Link
                    key={group.id}
                    to={`/groups/${group.id}`}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-muted transition-colors"
                  >
                    <div className="flex items-center gap-3">
                      <Avatar>
                        <AvatarImage src={group.image_url || ''} />
                        <AvatarFallback>{getInitials(group.name)}</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{group.name}</p>
                        <p className="text-xs text-muted-foreground">
                          {group.member_count} member{group.member_count !== 1 ? 's' : ''}
                        </p>
                      </div>
                    </div>
                    <ArrowRight className="h-4 w-4 text-muted-foreground" />
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        {/* Balance by Group */}
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <CardTitle>Balances by Group</CardTitle>
              <Button variant="ghost" size="sm" asChild>
                <Link to="/balances">View Details</Link>
              </Button>
            </div>
            <CardDescription>Your balance in each group</CardDescription>
          </CardHeader>
          <CardContent>
            {balancesLoading ? (
              <div className="space-y-3">
                {[1, 2, 3].map((i) => (
                  <div key={i} className="h-12 bg-muted animate-pulse rounded" />
                ))}
              </div>
            ) : !balances?.group_balances?.length ? (
              <div className="text-center py-6">
                <p className="text-muted-foreground">No balances to show</p>
              </div>
            ) : (
              <div className="space-y-3">
                {balances.group_balances.slice(0, 5).map((gb) => (
                  <Link
                    key={gb.group_id}
                    to={`/groups/${gb.group_id}`}
                    className="flex items-center justify-between p-3 rounded-lg hover:bg-muted transition-colors"
                  >
                    <p className="font-medium">{gb.group_name}</p>
                    <span className={`font-semibold ${
                      gb.your_total_balance >= 0 ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {gb.your_total_balance >= 0 ? '+' : ''}{formatCurrency(gb.your_total_balance)}
                    </span>
                  </Link>
                ))}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
