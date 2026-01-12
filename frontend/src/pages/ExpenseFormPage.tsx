import { useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { z } from 'zod';
import { groupService } from '@/services/groups';
import { expenseService, CreateExpenseData } from '@/services/expenses';
import { useAuthStore } from '@/store/authStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { getInitials } from '@/lib/utils';
import { ArrowLeft, Loader2, Check } from 'lucide-react';

const CATEGORIES = [
  { value: 'food', label: 'Food & Drinks' },
  { value: 'transport', label: 'Transport' },
  { value: 'accommodation', label: 'Accommodation' },
  { value: 'entertainment', label: 'Entertainment' },
  { value: 'shopping', label: 'Shopping' },
  { value: 'utilities', label: 'Utilities' },
  { value: 'groceries', label: 'Groceries' },
  { value: 'healthcare', label: 'Healthcare' },
  { value: 'other', label: 'Other' },
];

const expenseSchema = z.object({
  description: z.string().min(1, 'Description is required').max(200),
  amount: z.number().positive('Amount must be positive'),
  date: z.string().min(1, 'Date is required'),
  category: z.string().optional(),
  notes: z.string().optional(),
});

type ExpenseFormData = z.infer<typeof expenseSchema>;

export function ExpenseFormPage() {
  const navigate = useNavigate();
  const { groupId } = useParams<{ groupId: string }>();
  const { user } = useAuthStore();
  const queryClient = useQueryClient();

  const [splitType, setSplitType] = useState<'equal' | 'unequal' | 'shares' | 'percentage'>('equal');
  const [payerId, setPayerId] = useState(user?.id || '');
  const [selectedParticipants, setSelectedParticipants] = useState<string[]>([]);
  const [customSplits, setCustomSplits] = useState<Record<string, number>>({});

  const { data: group, isLoading: groupLoading } = useQuery({
    queryKey: ['group', groupId],
    queryFn: () => groupService.getGroup(groupId!),
    enabled: !!groupId,
  });

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<ExpenseFormData>({
    resolver: zodResolver(expenseSchema),
    defaultValues: {
      date: new Date().toISOString().split('T')[0],
    },
  });

  const amount = watch('amount') || 0;

  const createMutation = useMutation({
    mutationFn: expenseService.createExpense,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['expenses', groupId] });
      queryClient.invalidateQueries({ queryKey: ['group', groupId] });
      queryClient.invalidateQueries({ queryKey: ['balances'] });
      navigate(`/groups/${groupId}`);
    },
  });

  const members = group?.members || [];

  // Initialize participants when group loads
  if (members.length > 0 && selectedParticipants.length === 0) {
    setSelectedParticipants(members.map(m => m.user_id));
  }

  const toggleParticipant = (userId: string) => {
    setSelectedParticipants(prev =>
      prev.includes(userId)
        ? prev.filter(id => id !== userId)
        : [...prev, userId]
    );
  };

  const onSubmit = async (data: ExpenseFormData) => {
    const expenseData: CreateExpenseData = {
      group_id: groupId!,
      description: data.description,
      amount: data.amount,
      date: data.date,
      payer_id: payerId,
      split_type: splitType,
      category: data.category,
      notes: data.notes,
    };

    if (splitType === 'equal') {
      expenseData.participant_ids = selectedParticipants;
    } else {
      expenseData.splits = Object.entries(customSplits).map(([userId, value]) => ({
        user_id: userId,
        ...(splitType === 'unequal' && { amount: value }),
        ...(splitType === 'shares' && { shares: value }),
        ...(splitType === 'percentage' && { percentage: value }),
      }));
    }

    createMutation.mutate(expenseData);
  };

  const calculateEqualSplit = () => {
    if (selectedParticipants.length === 0) return 0;
    return amount / selectedParticipants.length;
  };

  if (groupLoading) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <Loader2 className="h-8 w-8 animate-spin" />
      </div>
    );
  }

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-2xl font-bold">Add Expense</h1>
          <p className="text-muted-foreground">{group?.name}</p>
        </div>
      </div>

      <form onSubmit={handleSubmit(onSubmit)}>
        <Card>
          <CardHeader>
            <CardTitle>Expense Details</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="description">Description</Label>
              <Input
                id="description"
                {...register('description')}
                placeholder="What was this expense for?"
              />
              {errors.description && (
                <p className="text-sm text-destructive">{errors.description.message}</p>
              )}
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="amount">Amount</Label>
                <Input
                  id="amount"
                  type="number"
                  step="0.01"
                  {...register('amount', { valueAsNumber: true })}
                  placeholder="0.00"
                />
                {errors.amount && (
                  <p className="text-sm text-destructive">{errors.amount.message}</p>
                )}
              </div>

              <div className="space-y-2">
                <Label htmlFor="date">Date</Label>
                <Input id="date" type="date" {...register('date')} />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label>Paid by</Label>
                <Select value={payerId} onValueChange={setPayerId}>
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    {members.map((member) => (
                      <SelectItem key={member.user_id} value={member.user_id}>
                        {member.user.name}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label>Category</Label>
                <Select {...register('category')}>
                  <SelectTrigger>
                    <SelectValue placeholder="Select category" />
                  </SelectTrigger>
                  <SelectContent>
                    {CATEGORIES.map((cat) => (
                      <SelectItem key={cat.value} value={cat.value}>
                        {cat.label}
                      </SelectItem>
                    ))}
                  </SelectContent>
                </Select>
              </div>
            </div>

            <div className="space-y-2">
              <Label htmlFor="notes">Notes (optional)</Label>
              <Input id="notes" {...register('notes')} placeholder="Additional details..." />
            </div>
          </CardContent>
        </Card>

        <Card className="mt-4">
          <CardHeader>
            <CardTitle>Split Options</CardTitle>
            <CardDescription>How should this expense be split?</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <Tabs value={splitType} onValueChange={(v) => setSplitType(v as typeof splitType)}>
              <TabsList className="grid grid-cols-4">
                <TabsTrigger value="equal">Equal</TabsTrigger>
                <TabsTrigger value="unequal">Unequal</TabsTrigger>
                <TabsTrigger value="shares">Shares</TabsTrigger>
                <TabsTrigger value="percentage">%</TabsTrigger>
              </TabsList>

              <TabsContent value="equal" className="space-y-4 mt-4">
                <p className="text-sm text-muted-foreground">
                  Split equally among selected participants
                </p>
                <div className="grid grid-cols-2 gap-2">
                  {members.map((member) => (
                    <div
                      key={member.user_id}
                      className={`flex items-center gap-3 p-3 rounded-lg border cursor-pointer transition-colors ${
                        selectedParticipants.includes(member.user_id)
                          ? 'border-primary bg-primary/5'
                          : 'hover:bg-muted'
                      }`}
                      onClick={() => toggleParticipant(member.user_id)}
                    >
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={member.user.profile_picture || ''} />
                        <AvatarFallback>{getInitials(member.user.name)}</AvatarFallback>
                      </Avatar>
                      <div className="flex-1">
                        <p className="text-sm font-medium">{member.user.name}</p>
                        {selectedParticipants.includes(member.user_id) && amount > 0 && (
                          <p className="text-xs text-muted-foreground">
                            ${calculateEqualSplit().toFixed(2)}
                          </p>
                        )}
                      </div>
                      {selectedParticipants.includes(member.user_id) && (
                        <Check className="h-4 w-4 text-primary" />
                      )}
                    </div>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="unequal" className="space-y-4 mt-4">
                <p className="text-sm text-muted-foreground">
                  Enter specific amounts for each person
                </p>
                <div className="space-y-2">
                  {members.map((member) => (
                    <div key={member.user_id} className="flex items-center gap-3">
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={member.user.profile_picture || ''} />
                        <AvatarFallback>{getInitials(member.user.name)}</AvatarFallback>
                      </Avatar>
                      <span className="flex-1">{member.user.name}</span>
                      <Input
                        type="number"
                        step="0.01"
                        className="w-24"
                        placeholder="0.00"
                        value={customSplits[member.user_id] || ''}
                        onChange={(e) => setCustomSplits({
                          ...customSplits,
                          [member.user_id]: parseFloat(e.target.value) || 0
                        })}
                      />
                    </div>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="shares" className="space-y-4 mt-4">
                <p className="text-sm text-muted-foreground">
                  Assign shares to each person
                </p>
                <div className="space-y-2">
                  {members.map((member) => (
                    <div key={member.user_id} className="flex items-center gap-3">
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={member.user.profile_picture || ''} />
                        <AvatarFallback>{getInitials(member.user.name)}</AvatarFallback>
                      </Avatar>
                      <span className="flex-1">{member.user.name}</span>
                      <Input
                        type="number"
                        className="w-20"
                        placeholder="1"
                        value={customSplits[member.user_id] || ''}
                        onChange={(e) => setCustomSplits({
                          ...customSplits,
                          [member.user_id]: parseInt(e.target.value) || 0
                        })}
                      />
                      <span className="text-sm text-muted-foreground">shares</span>
                    </div>
                  ))}
                </div>
              </TabsContent>

              <TabsContent value="percentage" className="space-y-4 mt-4">
                <p className="text-sm text-muted-foreground">
                  Set percentage for each person (must total 100%)
                </p>
                <div className="space-y-2">
                  {members.map((member) => (
                    <div key={member.user_id} className="flex items-center gap-3">
                      <Avatar className="h-8 w-8">
                        <AvatarImage src={member.user.profile_picture || ''} />
                        <AvatarFallback>{getInitials(member.user.name)}</AvatarFallback>
                      </Avatar>
                      <span className="flex-1">{member.user.name}</span>
                      <Input
                        type="number"
                        className="w-20"
                        placeholder="0"
                        value={customSplits[member.user_id] || ''}
                        onChange={(e) => setCustomSplits({
                          ...customSplits,
                          [member.user_id]: parseFloat(e.target.value) || 0
                        })}
                      />
                      <span className="text-sm text-muted-foreground">%</span>
                    </div>
                  ))}
                </div>
              </TabsContent>
            </Tabs>
          </CardContent>
        </Card>

        <div className="flex gap-4 mt-6">
          <Button type="button" variant="outline" className="flex-1" onClick={() => navigate(-1)}>
            Cancel
          </Button>
          <Button type="submit" className="flex-1" disabled={createMutation.isPending}>
            {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
            Add Expense
          </Button>
        </div>
      </form>
    </div>
  );
}
