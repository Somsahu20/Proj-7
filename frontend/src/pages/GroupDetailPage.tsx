import { useEffect, useState } from 'react';
import { useParams, Link, useLocation } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { groupService } from '@/services/groups';
import { expenseService } from '@/services/expenses';
import { balanceService } from '@/services/balances';
import { useAuthStore } from '@/store/authStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { formatCurrency, formatDate, getInitials } from '@/lib/utils';
import { Plus, Users, Receipt, CreditCard, Settings, ArrowLeft, Send, Loader2, TrendingUp, TrendingDown, Gavel, BarChart3 } from 'lucide-react';
import { DisputesPanel } from '@/pages/DisputesPage';
import { GroupAnalyticsPanel } from '@/components/analytics';

export function GroupDetailPage() {
  const { groupId } = useParams<{ groupId: string }>();
  const location = useLocation();
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [inviteEmail, setInviteEmail] = useState('');
  const [inviteDialogOpen, setInviteDialogOpen] = useState(false);
  const [activeTab, setActiveTab] = useState('expenses');

  useEffect(() => {
    const state = location.state as
      | { tab?: string; openCreate?: boolean; targetType?: 'expense' | 'payment'; targetId?: string }
      | null;
    if (state?.tab) {
      setActiveTab(state.tab);
      return;
    }
    if (state?.openCreate) {
      setActiveTab('disputes');
    }
  }, [location.state]);

  const { data: group, isLoading: groupLoading } = useQuery({
    queryKey: ['group', groupId],
    queryFn: () => groupService.getGroup(groupId!),
    enabled: !!groupId,
  });

  const { data: expenses } = useQuery({
    queryKey: ['expenses', groupId],
    queryFn: () => expenseService.getExpenses(groupId!, 1, 10),
    enabled: !!groupId,
  });

  const { data: balance } = useQuery({
    queryKey: ['group-balance', groupId],
    queryFn: () => balanceService.getGroupBalance(groupId!),
    enabled: !!groupId,
  });

  const { data: settlements } = useQuery({
    queryKey: ['settlements', groupId],
    queryFn: () => balanceService.getSettlementSuggestions(groupId!),
    enabled: !!groupId,
  });

  const inviteMutation = useMutation({
    mutationFn: (email: string) => groupService.createInvitation(groupId!, email),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['group', groupId] });
      setInviteEmail('');
      setInviteDialogOpen(false);
    },
  });

  const isAdmin = group?.members?.some(m => m.user_id === user?.id && m.role === 'admin');

  if (groupLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (!group) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold">Group not found</h2>
        <Button asChild className="mt-4">
          <Link to="/groups">Back to Groups</Link>
        </Button>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" asChild>
          <Link to="/groups">
            <ArrowLeft className="h-5 w-5" />
          </Link>
        </Button>
        <Avatar className="h-16 w-16">
          <AvatarImage src={group.image_url || ''} />
          <AvatarFallback className="text-lg">{getInitials(group.name)}</AvatarFallback>
        </Avatar>
        <div className="flex-1">
          <h1 className="text-3xl font-bold">{group.name}</h1>
          <p className="text-muted-foreground capitalize">{group.category} • {group.members?.length} members</p>
        </div>
        <div className="flex gap-2">
          <Button asChild>
            <Link to={`/groups/${groupId}/expenses/new`}>
              <Plus className="mr-2 h-4 w-4" />
              Add Expense
            </Link>
          </Button>
          {isAdmin && (
            <Button variant="outline" asChild>
              <Link to={`/groups/${groupId}/settings`}>
                <Settings className="h-4 w-4" />
              </Link>
            </Button>
          )}
        </div>
      </div>

      {/* Balance Summary */}
      <div className="grid gap-4 md:grid-cols-3">
        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Your Balance</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${
              (group.your_balance || 0) >= 0 ? 'text-green-600' : 'text-red-600'
            }`}>
              {formatCurrency(group.your_balance || 0)}
            </div>
            <p className="text-xs text-muted-foreground">
              {(group.your_balance || 0) >= 0 ? 'You are owed' : 'You owe'}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Total Expenses</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{formatCurrency(group.total_expenses || 0)}</div>
            <p className="text-xs text-muted-foreground">{expenses?.total || 0} expenses</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm font-medium">Settlement Needed</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{settlements?.total_transactions || 0}</div>
            <p className="text-xs text-muted-foreground">transactions to settle</p>
          </CardContent>
        </Card>
      </div>

      {/* Tabs */}
      <Tabs value={activeTab} onValueChange={setActiveTab} className="space-y-4">
        <TabsList>
          <TabsTrigger value="expenses">
            <Receipt className="mr-2 h-4 w-4" />
            Expenses
          </TabsTrigger>
          <TabsTrigger value="balances">
            <CreditCard className="mr-2 h-4 w-4" />
            Balances
          </TabsTrigger>
          <TabsTrigger value="members">
            <Users className="mr-2 h-4 w-4" />
            Members
          </TabsTrigger>
          <TabsTrigger value="disputes">
            <Gavel className="mr-2 h-4 w-4" />
            Disputes
          </TabsTrigger>
          <TabsTrigger value="analytics">
            <BarChart3 className="mr-2 h-4 w-4" />
            Analytics
          </TabsTrigger>
        </TabsList>

        {/* Expenses Tab */}
        <TabsContent value="expenses" className="space-y-4">
          {!expenses?.expenses?.length ? (
            <Card>
              <CardContent className="py-12 text-center">
                <Receipt className="h-12 w-12 mx-auto text-muted-foreground mb-4" />
                <h3 className="font-semibold mb-2">No expenses yet</h3>
                <p className="text-muted-foreground mb-4">Add your first expense to get started</p>
                <Button asChild>
                  <Link to={`/groups/${groupId}/expenses/new`}>
                    <Plus className="mr-2 h-4 w-4" />
                    Add Expense
                  </Link>
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-2">
              {expenses.expenses.map((expense) => (
                <Card key={expense.id} className="hover:shadow-sm transition-shadow">
                  <Link to={`/expenses/${expense.id}`}>
                    <CardContent className="flex items-center gap-4 py-4">
                      <div className="flex-1">
                        <p className="font-medium">{expense.description}</p>
                        <p className="text-sm text-muted-foreground">
                          Paid by {expense.payer?.name || 'Unknown'} • {formatDate(expense.date)}
                        </p>
                      </div>
                      <div className="text-right">
                        <p className="font-semibold">{formatCurrency(expense.amount)}</p>
                        <p className="text-xs text-muted-foreground capitalize">{expense.category || 'General'}</p>
                      </div>
                    </CardContent>
                  </Link>
                </Card>
              ))}
              {expenses.total > 10 && (
                <Button variant="outline" className="w-full" asChild>
                  <Link to={`/groups/${groupId}/expenses`}>View All Expenses</Link>
                </Button>
              )}
            </div>
          )}
        </TabsContent>

        {/* Balances Tab */}
        <TabsContent value="balances" className="space-y-4">
          <Card>
            <CardHeader>
              <CardTitle>Who Owes Whom</CardTitle>
              <CardDescription>Current balances between members</CardDescription>
            </CardHeader>
            <CardContent>
              {!balance?.balances?.length ? (
                <p className="text-center text-muted-foreground py-4">All settled up!</p>
              ) : (
                <div className="space-y-3">
                  {balance.balances.map((b) => (
                    <div key={b.user_id} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                      <div className="flex items-center gap-3">
                        <Avatar className="h-8 w-8">
                          <AvatarImage src={b.profile_picture || ''} />
                          <AvatarFallback>{getInitials(b.user_name)}</AvatarFallback>
                        </Avatar>
                        <span>{b.user_name}</span>
                      </div>
                      <div className="flex items-center gap-2">
                        {b.balance > 0 ? (
                          <>
                            <TrendingUp className="h-4 w-4 text-green-500" />
                            <span className="text-green-600 font-medium">owes you {formatCurrency(b.balance)}</span>
                          </>
                        ) : (
                          <>
                            <TrendingDown className="h-4 w-4 text-red-500" />
                            <span className="text-red-600 font-medium">you owe {formatCurrency(Math.abs(b.balance))}</span>
                          </>
                        )}
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </CardContent>
          </Card>

          {settlements && settlements.suggestions.length > 0 && (
            <Card>
              <CardHeader>
                <CardTitle>Suggested Settlements</CardTitle>
                <CardDescription>
                  Optimized to minimize transactions ({settlements.total_transactions} instead of {settlements.original_transactions})
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {settlements.suggestions.map((s, i) => (
                  <div key={i} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">{s.from_user_name}</span>
                      <Send className="h-4 w-4 text-muted-foreground" />
                      <span className="font-medium">{s.to_user_name}</span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{formatCurrency(s.amount)}</span>
                      <Button size="sm" asChild>
                        <Link to={`/payments/new?group=${groupId}&to=${s.to_user_id}&amount=${s.amount}`}>
                          Record
                        </Link>
                      </Button>
                    </div>
                  </div>
                ))}
              </CardContent>
            </Card>
          )}
        </TabsContent>

        {/* Members Tab */}
        <TabsContent value="members" className="space-y-4">
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <div>
                  <CardTitle>Members</CardTitle>
                  <CardDescription>{group.members?.length} member{group.members?.length !== 1 ? 's' : ''}</CardDescription>
                </div>
                <Dialog open={inviteDialogOpen} onOpenChange={setInviteDialogOpen}>
                  <DialogTrigger asChild>
                    <Button>
                      <Plus className="mr-2 h-4 w-4" />
                      Invite
                    </Button>
                  </DialogTrigger>
                  <DialogContent>
                    <DialogHeader>
                      <DialogTitle>Invite Member</DialogTitle>
                      <DialogDescription>Send an invitation to join this group</DialogDescription>
                    </DialogHeader>
                    <div className="space-y-4 py-4">
                      <div className="space-y-2">
                        <Label htmlFor="email">Email Address</Label>
                        <Input
                          id="email"
                          type="email"
                          value={inviteEmail}
                          onChange={(e) => setInviteEmail(e.target.value)}
                          placeholder="friend@example.com"
                        />
                      </div>
                    </div>
                    <DialogFooter>
                      <Button variant="outline" onClick={() => setInviteDialogOpen(false)}>Cancel</Button>
                      <Button onClick={() => inviteMutation.mutate(inviteEmail)} disabled={inviteMutation.isPending}>
                        {inviteMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                        Send Invitation
                      </Button>
                    </DialogFooter>
                  </DialogContent>
                </Dialog>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-3">
                {group.members?.map((member) => (
                  <div key={member.id} className="flex items-center justify-between p-3 rounded-lg bg-muted/50">
                    <div className="flex items-center gap-3">
                      <Avatar>
                        <AvatarImage src={member.user.profile_picture || ''} />
                        <AvatarFallback>{getInitials(member.user.name)}</AvatarFallback>
                      </Avatar>
                      <div>
                        <p className="font-medium">{member.user.name}</p>
                        <p className="text-sm text-muted-foreground">{member.user.email}</p>
                      </div>
                    </div>
                    <span className={`text-xs px-2 py-1 rounded-full ${
                      member.role === 'admin' ? 'bg-primary/10 text-primary' : 'bg-muted text-muted-foreground'
                    }`}>
                      {member.role}
                    </span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        {/* Disputes Tab */}
        <TabsContent value="disputes" className="space-y-4">
          <DisputesPanel
            groupId={groupId}
            hideHeader
            prefill={location.state as { openCreate?: boolean; targetType?: 'expense' | 'payment'; targetId?: string } | null}
          />
        </TabsContent>

        {/* Analytics Tab */}
        <TabsContent value="analytics" className="space-y-4">
          <GroupAnalyticsPanel groupId={groupId!} />
        </TabsContent>
      </Tabs>
    </div>
  );
}
