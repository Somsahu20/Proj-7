import { useParams, Link, useNavigate } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { expenseService } from '@/services/expenses';
import { useAuthStore } from '@/store/authStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { getInitials, formatCurrency, formatDate } from '@/lib/utils';
import { ArrowLeft, Trash2, Loader2, Receipt, Calendar, Users, FileText, Gavel } from 'lucide-react';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { useState } from 'react';

export function ExpenseDetailPage() {
  const { expenseId } = useParams<{ expenseId: string }>();
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [deleteDialogOpen, setDeleteDialogOpen] = useState(false);

  const { data: expense, isLoading, error } = useQuery({
    queryKey: ['expense', expenseId],
    queryFn: () => expenseService.getExpense(expenseId!),
    enabled: !!expenseId,
  });

  const deleteMutation = useMutation({
    mutationFn: () => expenseService.deleteExpense(expenseId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['expenses'] });
      if (expense?.group_id) {
        navigate(`/groups/${expense.group_id}`);
      } else {
        navigate('/dashboard');
      }
    },
  });

  const handleDelete = () => {
    deleteMutation.mutate();
    setDeleteDialogOpen(false);
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  if (error || !expense) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold">Expense not found</h2>
        <p className="text-muted-foreground mt-2">The expense you're looking for doesn't exist or you don't have access to it.</p>
        <Button asChild className="mt-4">
          <Link to="/dashboard">Back to Dashboard</Link>
        </Button>
      </div>
    );
  }

  const isOwner = expense.created_by_id === user?.id || expense.payer_id === user?.id;

  return (
    <div className="space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button variant="ghost" size="icon" asChild>
            <Link to={expense.group_id ? `/groups/${expense.group_id}` : '/dashboard'}>
              <ArrowLeft className="h-5 w-5" />
            </Link>
          </Button>
          <div>
            <h1 className="text-3xl font-bold">{expense.description}</h1>
            <p className="text-muted-foreground">Expense Details</p>
          </div>
        </div>
        <div className="flex gap-2">
          <Button variant="outline" size="sm" asChild>
            <Link
              to={`/groups/${expense.group_id}`}
              state={{ openCreate: true, targetType: 'expense', targetId: expense.id, tab: 'disputes' }}
            >
              <Gavel className="h-4 w-4 mr-2" />
              Open Dispute
            </Link>
          </Button>
          {isOwner && (
            <Dialog open={deleteDialogOpen} onOpenChange={setDeleteDialogOpen}>
              <DialogTrigger asChild>
                <Button variant="destructive" size="sm">
                  <Trash2 className="h-4 w-4 mr-2" />
                  Delete
                </Button>
              </DialogTrigger>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Delete Expense</DialogTitle>
                  <DialogDescription>
                    Are you sure you want to delete this expense? This action cannot be undone.
                  </DialogDescription>
                </DialogHeader>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setDeleteDialogOpen(false)}>
                    Cancel
                  </Button>
                  <Button
                    variant="destructive"
                    onClick={handleDelete}
                    disabled={deleteMutation.isPending}
                  >
                    {deleteMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                    Delete
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          )}
        </div>
      </div>

      {/* Main Details Card */}
      <Card>
        <CardHeader>
          <div className="flex items-center justify-between">
            <div>
              <CardTitle className="text-2xl">{formatCurrency(expense.amount)}</CardTitle>
              <CardDescription>{expense.description}</CardDescription>
            </div>
            {expense.category && (
              <span className="px-2 py-1 bg-secondary text-secondary-foreground rounded-md text-sm">{expense.category}</span>
            )}
          </div>
        </CardHeader>
        <CardContent className="space-y-6">
          {/* Paid by */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Receipt className="h-4 w-4" />
              <span>Paid by</span>
            </div>
            <div className="flex items-center gap-2">
              <Avatar className="h-8 w-8">
                <AvatarImage src={expense.payer?.profile_picture || ''} />
                <AvatarFallback>{getInitials(expense.payer?.name || 'Unknown')}</AvatarFallback>
              </Avatar>
              <span className="font-medium">
                {expense.payer?.id === user?.id ? 'You' : expense.payer?.name || 'Unknown'}
              </span>
            </div>
          </div>

          {/* Date */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Calendar className="h-4 w-4" />
              <span>Date</span>
            </div>
            <span>{formatDate(expense.date)}</span>
          </div>

          {/* Split Type */}
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2 text-muted-foreground">
              <Users className="h-4 w-4" />
              <span>Split</span>
            </div>
            <span className="px-2 py-1 border rounded-md text-sm">{expense.split_type}</span>
          </div>

          {/* Notes */}
          {expense.notes && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-muted-foreground">
                <FileText className="h-4 w-4" />
                <span>Notes</span>
              </div>
              <p className="text-sm bg-muted p-3 rounded-md">{expense.notes}</p>
            </div>
          )}

          {/* Receipt */}
          {expense.receipt_url && (
            <div className="space-y-2">
              <div className="flex items-center gap-2 text-muted-foreground">
                <Receipt className="h-4 w-4" />
                <span>Receipt</span>
              </div>
              <a
                href={expense.receipt_url}
                target="_blank"
                rel="noopener noreferrer"
                className="text-primary hover:underline text-sm"
              >
                View Receipt
              </a>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Splits Card */}
      <Card>
        <CardHeader>
          <CardTitle>Split Details</CardTitle>
          <CardDescription>How this expense is split between participants</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {expense.splits?.map((split) => (
              <div
                key={split.id}
                className="flex items-center justify-between p-3 bg-muted/50 rounded-lg"
              >
                <div className="flex items-center gap-3">
                  <Avatar className="h-8 w-8">
                    <AvatarImage src={split.user?.profile_picture || ''} />
                    <AvatarFallback>{getInitials(split.user?.name || 'Unknown')}</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium">
                      {split.user?.id === user?.id ? 'You' : split.user?.name || 'Unknown'}
                    </p>
                    {split.shares && <p className="text-xs text-muted-foreground">{split.shares} shares</p>}
                    {split.percentage && <p className="text-xs text-muted-foreground">{split.percentage}%</p>}
                  </div>
                </div>
                <div className="text-right">
                  <p className="font-medium">{formatCurrency(split.amount)}</p>
                  {split.is_settled ? (
                    <span className="px-2 py-0.5 bg-secondary text-secondary-foreground rounded-md text-xs">Settled</span>
                  ) : (
                    <span className="px-2 py-0.5 border rounded-md text-xs">Pending</span>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Metadata */}
      <div className="text-xs text-muted-foreground text-center">
        Created {formatDate(expense.created_at)}
        {expense.updated_at && expense.updated_at !== expense.created_at && (
          <> &middot; Updated {formatDate(expense.updated_at)}</>
        )}
      </div>
    </div>
  );
}
