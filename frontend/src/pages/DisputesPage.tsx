import { useEffect, useMemo, useRef, useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { disputeService, type CreateDisputeData } from '@/services/disputes';
import { useAuthStore } from '@/store/authStore';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Textarea } from '@/components/ui/textarea';
import { formatDate } from '@/lib/utils';
import { AlertCircle, CheckCircle2, Gavel, Loader2, MinusCircle, Plus, ThumbsDown, ThumbsUp, XCircle } from 'lucide-react';
import type { Dispute } from '@/types';

type StatusFilter = 'all' | 'open' | 'voting' | 'resolved';
type VoteValue = 'approve' | 'reject' | 'abstain';
type ResolutionValue = 'upheld' | 'dismissed' | 'modified';

const STATUS_STYLES: Record<'open' | 'voting' | 'resolved', string> = {
  open: 'bg-blue-100 text-blue-800',
  voting: 'bg-yellow-100 text-yellow-800',
  resolved: 'bg-green-100 text-green-800',
};

const RESOLUTION_STYLES: Record<ResolutionValue, string> = {
  upheld: 'bg-green-100 text-green-800',
  dismissed: 'bg-red-100 text-red-800',
  modified: 'bg-yellow-100 text-yellow-800',
};

const DEFAULT_CREATE_STATE = {
  targetType: 'expense' as 'expense' | 'payment',
  targetId: '',
  reason: '',
  description: '',
  evidenceUrlInput: '',
  evidenceUrls: [] as string[],
};

type DisputesPanelProps = {
  groupId?: string;
  hideHeader?: boolean;
  prefill?: { openCreate?: boolean; targetType?: 'expense' | 'payment'; targetId?: string } | null;
};

export function DisputesPanel({ groupId, hideHeader, prefill }: DisputesPanelProps) {
  const queryClient = useQueryClient();
  const { user } = useAuthStore();
  const location = useLocation();
  const prefillHandled = useRef(false);
  const [statusFilter, setStatusFilter] = useState<StatusFilter>('all');
  const [createState, setCreateState] = useState(DEFAULT_CREATE_STATE);
  const [isCreateOpen, setIsCreateOpen] = useState(false);
  const [selectedDispute, setSelectedDispute] = useState<Dispute | null>(null);
  const [voteValue, setVoteValue] = useState<VoteValue>('approve');
  const [voteComment, setVoteComment] = useState('');
  const [isVoteOpen, setIsVoteOpen] = useState(false);
  const [resolutionValue, setResolutionValue] = useState<ResolutionValue>('upheld');
  const [resolutionNotes, setResolutionNotes] = useState('');
  const [isResolveOpen, setIsResolveOpen] = useState(false);

  const { data: disputes = [], isLoading } = useQuery({
    queryKey: ['disputes', statusFilter, groupId],
    queryFn: () => disputeService.getDisputes(statusFilter === 'all' ? undefined : statusFilter, groupId),
  });

  useEffect(() => {
    if (prefillHandled.current) return;
    const state = prefill || (location.state as
      | { openCreate?: boolean; targetType?: 'expense' | 'payment'; targetId?: string }
      | null);
    if (state?.openCreate && state.targetType && state.targetId) {
      setCreateState({ ...DEFAULT_CREATE_STATE, targetType: state.targetType, targetId: state.targetId });
      setIsCreateOpen(true);
      prefillHandled.current = true;
    }
  }, [location.state, prefill]);

  const createMutation = useMutation({
    mutationFn: (payload: CreateDisputeData) => disputeService.createDispute(payload),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['disputes'] });
      setIsCreateOpen(false);
      setCreateState(DEFAULT_CREATE_STATE);
    },
  });

  const voteMutation = useMutation({
    mutationFn: ({ disputeId, vote, comment }: { disputeId: string; vote: VoteValue; comment?: string }) =>
      disputeService.voteOnDispute(disputeId, { vote, comment }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['disputes'] });
      setIsVoteOpen(false);
      setSelectedDispute(null);
      setVoteComment('');
    },
  });

  const resolveMutation = useMutation({
    mutationFn: ({ disputeId, resolution, notes }: { disputeId: string; resolution: ResolutionValue; notes?: string }) =>
      disputeService.resolveDispute(disputeId, { resolution, resolution_notes: notes }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['disputes'] });
      setIsResolveOpen(false);
      setSelectedDispute(null);
      setResolutionNotes('');
      setResolutionValue('upheld');
    },
  });

  const isCreateValid = useMemo(() => {
    return createState.targetId.trim() &&
      createState.reason.trim().length > 0 &&
      createState.description.trim().length >= 10;
  }, [createState]);

  const handleCreateOpenChange = (open: boolean) => {
    setIsCreateOpen(open);
    if (!open) {
      setCreateState(DEFAULT_CREATE_STATE);
    }
  };

  const handleAddEvidenceUrl = () => {
    if (!createState.evidenceUrlInput.trim()) return;
    setCreateState((prev) => ({
      ...prev,
      evidenceUrls: [...prev.evidenceUrls, prev.evidenceUrlInput.trim()],
      evidenceUrlInput: '',
    }));
  };

  const handleRemoveEvidenceUrl = (url: string) => {
    setCreateState((prev) => ({
      ...prev,
      evidenceUrls: prev.evidenceUrls.filter((item) => item !== url),
    }));
  };

  const handleCreateDispute = () => {
    if (!isCreateValid) return;
    const payload: CreateDisputeData = {
      reason: createState.reason.trim(),
      description: createState.description.trim(),
      evidence_urls: createState.evidenceUrls,
    };
    if (createState.targetType === 'expense') {
      payload.expense_id = createState.targetId.trim();
    } else {
      payload.payment_id = createState.targetId.trim();
    }
    createMutation.mutate(payload);
  };

  const handleVoteClick = (dispute: Dispute, vote: VoteValue) => {
    setSelectedDispute(dispute);
    setVoteValue(vote);
    setVoteComment('');
    setIsVoteOpen(true);
  };

  const handleResolveClick = (dispute: Dispute) => {
    setSelectedDispute(dispute);
    setResolutionValue('upheld');
    setResolutionNotes('');
    setIsResolveOpen(true);
  };

  const handleSubmitVote = () => {
    if (!selectedDispute) return;
    voteMutation.mutate({
      disputeId: selectedDispute.id,
      vote: voteValue,
      comment: voteComment.trim() ? voteComment.trim() : undefined,
    });
  };

  const handleResolve = () => {
    if (!selectedDispute) return;
    resolveMutation.mutate({
      disputeId: selectedDispute.id,
      resolution: resolutionValue,
      notes: resolutionNotes.trim() ? resolutionNotes.trim() : undefined,
    });
  };

  return (
    <div className="space-y-6">
      {!hideHeader && (
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Disputes</h1>
            <p className="text-muted-foreground">Open disputes, vote, and resolve outcomes</p>
          </div>
          <Dialog open={isCreateOpen} onOpenChange={handleCreateOpenChange}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Open Dispute
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Open a Dispute</DialogTitle>
                <DialogDescription>
                  Dispute an expense or payment by providing the reason and details.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-2">
                <div className="space-y-2">
                  <Label htmlFor="targetType">Dispute Target</Label>
                  <Select
                    value={createState.targetType}
                    onValueChange={(value: 'expense' | 'payment') =>
                      setCreateState((prev) => ({ ...prev, targetType: value }))
                    }
                  >
                    <SelectTrigger id="targetType">
                      <SelectValue placeholder="Choose a target" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="expense">Expense</SelectItem>
                      <SelectItem value="payment">Payment</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="targetId">{createState.targetType === 'expense' ? 'Expense ID' : 'Payment ID'}</Label>
                  <Input
                    id="targetId"
                    value={createState.targetId}
                    onChange={(event) => setCreateState((prev) => ({ ...prev, targetId: event.target.value }))}
                    placeholder="Paste the ID here"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reason">Reason</Label>
                  <Input
                    id="reason"
                    maxLength={50}
                    value={createState.reason}
                    onChange={(event) => setCreateState((prev) => ({ ...prev, reason: event.target.value }))}
                    placeholder="e.g., Amount seems incorrect"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    maxLength={2000}
                    value={createState.description}
                    onChange={(event) => setCreateState((prev) => ({ ...prev, description: event.target.value }))}
                    placeholder="Share the context and what you think should change"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="evidence">Evidence URL</Label>
                  <div className="flex gap-2">
                    <Input
                      id="evidence"
                      value={createState.evidenceUrlInput}
                      onChange={(event) => setCreateState((prev) => ({ ...prev, evidenceUrlInput: event.target.value }))}
                      placeholder="https://example.com/receipt.jpg"
                    />
                    <Button type="button" variant="outline" onClick={handleAddEvidenceUrl}>
                      Add
                    </Button>
                  </div>
                  {createState.evidenceUrls.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {createState.evidenceUrls.map((url) => (
                        <span key={url} className="flex items-center gap-2 rounded-full bg-muted px-3 py-1 text-xs">
                          {url}
                          <button type="button" className="text-muted-foreground hover:text-foreground" onClick={() => handleRemoveEvidenceUrl(url)}>
                            <XCircle className="h-4 w-4" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateDispute} disabled={!isCreateValid || createMutation.isPending}>
                  {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Submit Dispute
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      )}

      {hideHeader && (
        <div className="flex items-center justify-end">
          <Dialog open={isCreateOpen} onOpenChange={handleCreateOpenChange}>
            <DialogTrigger asChild>
              <Button>
                <Plus className="mr-2 h-4 w-4" />
                Open Dispute
              </Button>
            </DialogTrigger>
            <DialogContent>
              <DialogHeader>
                <DialogTitle>Open a Dispute</DialogTitle>
                <DialogDescription>
                  Dispute an expense or payment by providing the reason and details.
                </DialogDescription>
              </DialogHeader>
              <div className="space-y-4 py-2">
                <div className="space-y-2">
                  <Label htmlFor="targetType">Dispute Target</Label>
                  <Select
                    value={createState.targetType}
                    onValueChange={(value: 'expense' | 'payment') =>
                      setCreateState((prev) => ({ ...prev, targetType: value }))
                    }
                  >
                    <SelectTrigger id="targetType">
                      <SelectValue placeholder="Choose a target" />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="expense">Expense</SelectItem>
                      <SelectItem value="payment">Payment</SelectItem>
                    </SelectContent>
                  </Select>
                </div>
                <div className="space-y-2">
                  <Label htmlFor="targetId">{createState.targetType === 'expense' ? 'Expense ID' : 'Payment ID'}</Label>
                  <Input
                    id="targetId"
                    value={createState.targetId}
                    onChange={(event) => setCreateState((prev) => ({ ...prev, targetId: event.target.value }))}
                    placeholder="Paste the ID here"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="reason">Reason</Label>
                  <Input
                    id="reason"
                    maxLength={50}
                    value={createState.reason}
                    onChange={(event) => setCreateState((prev) => ({ ...prev, reason: event.target.value }))}
                    placeholder="e.g., Amount seems incorrect"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="description">Description</Label>
                  <Textarea
                    id="description"
                    maxLength={2000}
                    value={createState.description}
                    onChange={(event) => setCreateState((prev) => ({ ...prev, description: event.target.value }))}
                    placeholder="Share the context and what you think should change"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="evidence">Evidence URL</Label>
                  <div className="flex gap-2">
                    <Input
                      id="evidence"
                      value={createState.evidenceUrlInput}
                      onChange={(event) => setCreateState((prev) => ({ ...prev, evidenceUrlInput: event.target.value }))}
                      placeholder="https://example.com/receipt.jpg"
                    />
                    <Button type="button" variant="outline" onClick={handleAddEvidenceUrl}>
                      Add
                    </Button>
                  </div>
                  {createState.evidenceUrls.length > 0 && (
                    <div className="flex flex-wrap gap-2">
                      {createState.evidenceUrls.map((url) => (
                        <span key={url} className="flex items-center gap-2 rounded-full bg-muted px-3 py-1 text-xs">
                          {url}
                          <button type="button" className="text-muted-foreground hover:text-foreground" onClick={() => handleRemoveEvidenceUrl(url)}>
                            <XCircle className="h-4 w-4" />
                          </button>
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              </div>
              <DialogFooter>
                <Button variant="outline" onClick={() => setIsCreateOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={handleCreateDispute} disabled={!isCreateValid || createMutation.isPending}>
                  {createMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Submit Dispute
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      )}

      <Tabs value={statusFilter} onValueChange={(value) => setStatusFilter(value as StatusFilter)} className="space-y-4">
        <TabsList>
          <TabsTrigger value="all">All</TabsTrigger>
          <TabsTrigger value="open">Open</TabsTrigger>
          <TabsTrigger value="voting">Voting</TabsTrigger>
          <TabsTrigger value="resolved">Resolved</TabsTrigger>
        </TabsList>

        <TabsContent value="all">
          <DisputeList
            disputes={disputes}
            isLoading={isLoading}
            userId={user?.id}
            onVote={handleVoteClick}
            onResolve={handleResolveClick}
          />
        </TabsContent>
        <TabsContent value="open">
          <DisputeList
            disputes={disputes}
            isLoading={isLoading}
            userId={user?.id}
            onVote={handleVoteClick}
            onResolve={handleResolveClick}
          />
        </TabsContent>
        <TabsContent value="voting">
          <DisputeList
            disputes={disputes}
            isLoading={isLoading}
            userId={user?.id}
            onVote={handleVoteClick}
            onResolve={handleResolveClick}
          />
        </TabsContent>
        <TabsContent value="resolved">
          <DisputeList
            disputes={disputes}
            isLoading={isLoading}
            userId={user?.id}
            onVote={handleVoteClick}
            onResolve={handleResolveClick}
          />
        </TabsContent>
      </Tabs>

      <Dialog open={isVoteOpen} onOpenChange={setIsVoteOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Cast your vote</DialogTitle>
            <DialogDescription>
              {selectedDispute?.reason} - {selectedDispute ? selectedDispute.id : ''}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="flex items-center gap-2 text-sm">
              {voteValue === 'approve' && <CheckCircle2 className="h-4 w-4 text-green-500" />}
              {voteValue === 'reject' && <XCircle className="h-4 w-4 text-red-500" />}
              {voteValue === 'abstain' && <MinusCircle className="h-4 w-4 text-muted-foreground" />}
              <span className="capitalize">{voteValue}</span>
            </div>
            <div className="space-y-2">
              <Label htmlFor="voteComment">Comment (optional)</Label>
              <Textarea
                id="voteComment"
                maxLength={500}
                value={voteComment}
                onChange={(event) => setVoteComment(event.target.value)}
                placeholder="Add context for your vote"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsVoteOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleSubmitVote} disabled={voteMutation.isPending}>
              {voteMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Submit Vote
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>

      <Dialog open={isResolveOpen} onOpenChange={setIsResolveOpen}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Resolve dispute</DialogTitle>
            <DialogDescription>
              Finalize the dispute outcome (admin only).
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div className="space-y-2">
              <Label htmlFor="resolution">Resolution</Label>
              <Select value={resolutionValue} onValueChange={(value: ResolutionValue) => setResolutionValue(value)}>
                <SelectTrigger id="resolution">
                  <SelectValue placeholder="Select a resolution" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="upheld">Upheld</SelectItem>
                  <SelectItem value="dismissed">Dismissed</SelectItem>
                  <SelectItem value="modified">Modified</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-2">
              <Label htmlFor="resolutionNotes">Resolution notes (optional)</Label>
              <Textarea
                id="resolutionNotes"
                maxLength={2000}
                value={resolutionNotes}
                onChange={(event) => setResolutionNotes(event.target.value)}
                placeholder="Add any notes or changes to record"
              />
            </div>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setIsResolveOpen(false)}>
              Cancel
            </Button>
            <Button onClick={handleResolve} disabled={resolveMutation.isPending}>
              {resolveMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
              Resolve Dispute
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  );
}

export function DisputesPage() {
  return <DisputesPanel />;
}

function getVoteSummary(dispute: Dispute) {
  if (dispute.vote_summary) {
    return dispute.vote_summary;
  }
  return dispute.votes.reduce(
    (acc, vote) => {
      acc[vote.vote] += 1;
      return acc;
    },
    { approve: 0, reject: 0, abstain: 0 }
  );
}

function DisputeList({
  disputes,
  isLoading,
  userId,
  onVote,
  onResolve,
}: {
  disputes: Dispute[];
  isLoading: boolean;
  userId?: string;
  onVote: (dispute: Dispute, vote: VoteValue) => void;
  onResolve: (dispute: Dispute) => void;
}) {
  if (isLoading) {
    return (
      <div className="space-y-3">
        {[1, 2, 3].map((item) => (
          <Card key={item} className="animate-pulse">
            <CardContent className="h-24" />
          </Card>
        ))}
      </div>
    );
  }

  if (disputes.length === 0) {
    return (
      <Card>
        <CardContent className="py-12 text-center">
          <Gavel className="mx-auto h-12 w-12 text-muted-foreground mb-4" />
          <p className="text-muted-foreground">No disputes found</p>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {disputes.map((dispute) => {
        const summary = getVoteSummary(dispute);
        const totalVotes = summary.approve + summary.reject + summary.abstain;
        const userVote = dispute.votes.find((vote) => vote.user_id === userId);
        const targetLabel = dispute.expense_id ? 'Expense' : 'Payment';
        const targetId = dispute.expense_id || dispute.payment_id;

        return (
          <Card key={dispute.id}>
            <CardHeader className="flex flex-row items-start justify-between gap-4">
              <div className="space-y-1">
                <CardTitle className="text-lg">{dispute.reason}</CardTitle>
                <CardDescription className="flex flex-wrap items-center gap-2">
                  <span className="text-xs font-mono text-muted-foreground">{targetLabel} ID: {targetId}</span>
                  {dispute.expense_id && (
                    <Link to={`/expenses/${dispute.expense_id}`} className="text-xs text-primary hover:underline">
                      View expense
                    </Link>
                  )}
                </CardDescription>
              </div>
              <span className={`inline-flex items-center gap-1 rounded-full px-2 py-1 text-xs ${STATUS_STYLES[dispute.status]}`}>
                {dispute.status === 'open' && <AlertCircle className="h-3 w-3" />}
                {dispute.status === 'voting' && <MinusCircle className="h-3 w-3" />}
                {dispute.status === 'resolved' && <CheckCircle2 className="h-3 w-3" />}
                {dispute.status}
              </span>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-1 text-sm text-muted-foreground">
                <p>Opened {formatDate(dispute.created_at)} {dispute.opened_by_id === userId ? 'by you' : `by ${dispute.opened_by_id}`}</p>
                {dispute.voting_ends_at && (
                  <p>Voting ends {formatDate(dispute.voting_ends_at)}</p>
                )}
              </div>
              <div className="text-sm">{dispute.description}</div>

              {dispute.evidence_urls.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium">Evidence</p>
                  <div className="space-y-1 text-sm text-muted-foreground">
                    {dispute.evidence_urls.map((url) => (
                      <a key={url} href={url} target="_blank" rel="noreferrer" className="block hover:underline">
                        {url}
                      </a>
                    ))}
                  </div>
                </div>
              )}

              {dispute.status === 'resolved' && dispute.resolution && (
                <div className="space-y-2">
                  <p className="text-sm font-medium">Resolution</p>
                  <div className="flex flex-wrap items-center gap-2 text-sm">
                    <span className={`rounded-full px-2 py-1 text-xs ${RESOLUTION_STYLES[dispute.resolution]}`}>
                      {dispute.resolution}
                    </span>
                    {dispute.resolved_at && (
                      <span className="text-muted-foreground">Resolved {formatDate(dispute.resolved_at)}</span>
                    )}
                  </div>
                  {dispute.resolution_notes && (
                    <p className="text-sm text-muted-foreground">{dispute.resolution_notes}</p>
                  )}
                </div>
              )}

              {totalVotes > 0 && (
                <div className="flex flex-wrap gap-2 text-xs">
                  <span className="rounded-full bg-green-100 px-2 py-1 text-green-800">Approve {summary.approve}</span>
                  <span className="rounded-full bg-red-100 px-2 py-1 text-red-800">Reject {summary.reject}</span>
                  <span className="rounded-full bg-gray-100 px-2 py-1 text-gray-800">Abstain {summary.abstain}</span>
                </div>
              )}

              {dispute.votes.length > 0 && (
                <div className="space-y-2">
                  <p className="text-sm font-medium">Votes</p>
                  <div className="space-y-2">
                    {dispute.votes.map((vote) => (
                      <div key={vote.id} className="rounded-lg border bg-muted/40 p-3 text-sm">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <span className="font-medium capitalize">{vote.vote}</span>
                          <span className="text-xs text-muted-foreground">{formatDate(vote.created_at)}</span>
                        </div>
                        <p className="text-xs text-muted-foreground">Voter: {vote.user_id}</p>
                        {vote.comment && <p className="mt-2 text-sm">{vote.comment}</p>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {dispute.status !== 'resolved' && (
                <div className="flex flex-wrap items-center gap-2">
                  <Button size="sm" variant="outline" disabled={!!userVote} onClick={() => onVote(dispute, 'approve')}>
                    <ThumbsUp className="mr-2 h-4 w-4" />
                    Approve
                  </Button>
                  <Button size="sm" variant="outline" disabled={!!userVote} onClick={() => onVote(dispute, 'reject')}>
                    <ThumbsDown className="mr-2 h-4 w-4" />
                    Reject
                  </Button>
                  <Button size="sm" variant="outline" disabled={!!userVote} onClick={() => onVote(dispute, 'abstain')}>
                    <MinusCircle className="mr-2 h-4 w-4" />
                    Abstain
                  </Button>
                  <Button size="sm" variant="secondary" onClick={() => onResolve(dispute)}>
                    Resolve (admin)
                  </Button>
                  {userVote && (
                    <span className="text-xs text-muted-foreground">You voted {userVote.vote}</span>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
