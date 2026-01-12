import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Link, useSearchParams } from 'react-router-dom';
import { paymentService } from '@/services/payments';
import { useAuthStore } from '@/store/authStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { formatCurrency, formatDate, getInitials } from '@/lib/utils';
import { Check, X, Clock, AlertCircle, Loader2, Plus } from 'lucide-react';
import type { Payment } from '@/types';

export function PaymentsPage() {
  const { user } = useAuthStore();
  const queryClient = useQueryClient();
  const [searchParams] = useSearchParams();
  const statusFilter = searchParams.get('status') || '';

  const [selectedPayment, setSelectedPayment] = useState<Payment | null>(null);
  const [rejectReason, setRejectReason] = useState('');
  const [dialogMode, setDialogMode] = useState<'confirm' | 'reject' | null>(null);

  const { data: payments, isLoading } = useQuery({
    queryKey: ['payments', statusFilter],
    queryFn: () => paymentService.getPayments(undefined, statusFilter || undefined),
  });

  const { data: pendingPayments = [] } = useQuery({
    queryKey: ['pending-payments'],
    queryFn: paymentService.getPendingPayments,
  });

  const confirmMutation = useMutation({
    mutationFn: (paymentId: string) => paymentService.confirmPayment(paymentId),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      queryClient.invalidateQueries({ queryKey: ['pending-payments'] });
      queryClient.invalidateQueries({ queryKey: ['balances'] });
      setSelectedPayment(null);
      setDialogMode(null);
    },
  });

  const rejectMutation = useMutation({
    mutationFn: ({ paymentId, reason }: { paymentId: string; reason: string }) =>
      paymentService.rejectPayment(paymentId, reason),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['payments'] });
      queryClient.invalidateQueries({ queryKey: ['pending-payments'] });
      setSelectedPayment(null);
      setDialogMode(null);
      setRejectReason('');
    },
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'confirmed':
        return <Check className="h-4 w-4 text-green-500" />;
      case 'rejected':
        return <X className="h-4 w-4 text-red-500" />;
      case 'pending':
        return <Clock className="h-4 w-4 text-yellow-500" />;
      default:
        return <AlertCircle className="h-4 w-4 text-muted-foreground" />;
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'confirmed':
        return 'bg-green-100 text-green-800';
      case 'rejected':
        return 'bg-red-100 text-red-800';
      case 'pending':
        return 'bg-yellow-100 text-yellow-800';
      default:
        return 'bg-gray-100 text-gray-800';
    }
  };

  const handleConfirm = () => {
    if (selectedPayment) {
      confirmMutation.mutate(selectedPayment.id);
    }
  };

  const handleReject = () => {
    if (selectedPayment && rejectReason) {
      rejectMutation.mutate({ paymentId: selectedPayment.id, reason: rejectReason });
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Payments</h1>
          <p className="text-muted-foreground">Track and manage your payments</p>
        </div>
        <Button asChild>
          <Link to="/payments/new">
            <Plus className="mr-2 h-4 w-4" />
            Record Payment
          </Link>
        </Button>
      </div>

      {/* Pending Confirmations */}
      {pendingPayments.length > 0 && (
        <Card className="border-yellow-500">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <AlertCircle className="h-5 w-5 text-yellow-500" />
              Pending Confirmations ({pendingPayments.length})
            </CardTitle>
            <CardDescription>Payments waiting for your confirmation</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            {pendingPayments.map((payment) => (
              <div
                key={payment.id}
                className="flex items-center justify-between p-4 rounded-lg border bg-muted/50"
              >
                <div className="flex items-center gap-4">
                  <Avatar>
                    <AvatarImage src={payment.payer?.profile_picture || ''} />
                    <AvatarFallback>{getInitials(payment.payer?.name || 'U')}</AvatarFallback>
                  </Avatar>
                  <div>
                    <p className="font-medium">{payment.payer?.name} paid you</p>
                    <p className="text-sm text-muted-foreground">{formatDate(payment.date)}</p>
                  </div>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-lg font-semibold">{formatCurrency(payment.amount)}</span>
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => {
                        setSelectedPayment(payment);
                        setDialogMode('reject');
                      }}
                    >
                      <X className="h-4 w-4" />
                    </Button>
                    <Button
                      size="sm"
                      onClick={() => {
                        setSelectedPayment(payment);
                        setDialogMode('confirm');
                      }}
                    >
                      <Check className="h-4 w-4" />
                    </Button>
                  </div>
                </div>
              </div>
            ))}
          </CardContent>
        </Card>
      )}

      {/* All Payments */}
      <Tabs defaultValue="all" className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="pending">Pending</TabsTrigger>
          <TabsTrigger value="confirmed">Confirmed</TabsTrigger>
          <TabsTrigger value="rejected">Rejected</TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          <PaymentList payments={payments?.payments || []} isLoading={isLoading} user={user} getStatusIcon={getStatusIcon} getStatusColor={getStatusColor} />
        </TabsContent>
        <TabsContent value="pending">
          <PaymentList payments={(payments?.payments || []).filter(p => p.status === 'pending')} isLoading={isLoading} user={user} getStatusIcon={getStatusIcon} getStatusColor={getStatusColor} />
        </TabsContent>
        <TabsContent value="confirmed">
          <PaymentList payments={(payments?.payments || []).filter(p => p.status === 'confirmed')} isLoading={isLoading} user={user} getStatusIcon={getStatusIcon} getStatusColor={getStatusColor} />
        </TabsContent>
        <TabsContent value="rejected">
          <PaymentList payments={(payments?.payments || []).filter(p => p.status === 'rejected')} isLoading={isLoading} user={user} getStatusIcon={getStatusIcon} getStatusColor={getStatusColor} />
        </TabsContent>
      </Tabs>

      {/* Confirm Dialog */}
      <Dialog open={dialogMode === 'confirm'} onOpenChange={() => setDialogMode(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Payment</DialogTitle>
            <DialogDescription>
              Are you sure you received {formatCurrency(selectedPayment?.amount || 0)} from{' '}
              {selectedPayment?.payer?.name}?
            </DialogDescription>
          </DialogHeader>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogMode(null)}>
              Cancel
            </Button>
            <Button onClick={handleConfirm} disabled={confirmMutation.isPending}>
              {confirmMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Confirm Payment
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      {/* Reject Dialog */}
      <Dialog open={dialogMode === 'reject'} onOpenChange={() => setDialogMode(null)}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Reject Payment</DialogTitle>
            <DialogDescription>
              Why are you rejecting this payment of {formatCurrency(selectedPayment?.amount || 0)}?
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <Label htmlFor="reason">Reason</Label>
            <Input
              id="reason"
              value={rejectReason}
              onChange={(e) => setRejectReason(e.target.value)}
              placeholder="e.g., I didn't receive this payment"
            />
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setDialogMode(null)}>
              Cancel
            </Button>
            <Button
              variant="destructive"
              onClick={handleReject}
              disabled={!rejectReason || rejectMutation.isPending}
            >
              {rejectMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Reject Payment
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

function PaymentList({
  payments,
  isLoading,
  user,
  getStatusIcon,
  getStatusColor,
}: {
  payments: Payment[];
  isLoading: boolean;
  user: any;
  getStatusIcon: (status: string) => React.ReactNode;
  getStatusColor: (status: string) => string;
}) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((i) => (
          <Card key={i} className="animate-pulse">
            <CardContent className="h-20" />
          </Card>
        ))}
      </div>
    );
  }

  if (payments.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <p className="text-muted-foreground">No payments found</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-3">
      {payments.map((payment) => {
        const isPayer = payment.payer_id === user?.id;
        const otherUser = isPayer ? payment.receiver : payment.payer;

        return (
          <Card key={payment.id}>
            <CardContent className="flex items-center justify-between py-4">
              <div className="flex items-center gap-4">
                <Avatar>
                  <AvatarImage src={otherUser?.profile_picture || ''} />
                  <AvatarFallback>{getInitials(otherUser?.name || 'U')}</AvatarFallback>
                </Avatar>
                <div>
                  <p className="font-medium">
                    {isPayer ? `You paid ${otherUser?.name}` : `${otherUser?.name} paid you`}
                  </p>
                  <p className="text-sm text-muted-foreground">
                    {formatDate(payment.date)}
                    {payment.description && ` • ${payment.description}`}
                  </p>
                </div>
              </div>
              <div className="flex items-center gap-4">
                <span className={`text-lg font-semibold ${isPayer ? 'text-red-600' : 'text-green-600'}`}>
                  {isPayer ? '-' : '+'}{formatCurrency(payment.amount)}
                </span>
                <span className={`flex items-center gap-1 px-2 py-1 rounded-full text-xs ${getStatusColor(payment.status)}`}>
                  {getStatusIcon(payment.status)}
                  {payment.status}
                </span>
              </div>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
