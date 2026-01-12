import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { groupService } from '@/services/groups';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { formatDate, getInitials } from '@/lib/utils';
import { Mail, Check, X, Loader2 } from 'lucide-react';

export function InvitationsPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();

  const { data: invitations = [], isLoading } = useQuery({
    queryKey: ['my-invitations'],
    queryFn: groupService.getMyInvitations,
  });

  const acceptMutation = useMutation({
    mutationFn: groupService.acceptInvitationById,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['my-invitations'] });
      queryClient.invalidateQueries({ queryKey: ['groups'] });
      navigate(`/groups/${data.group_id}`);
    },
  });

  const declineMutation = useMutation({
    mutationFn: groupService.declineInvitation,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['my-invitations'] });
    },
  });

  const pendingInvitations = invitations.filter((inv) => inv.status === 'pending');

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold">Group Invitations</h1>
        <p className="text-muted-foreground">Accept or decline invitations to join groups</p>
      </div>

      {isLoading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <Card key={i} className="animate-pulse">
              <CardHeader>
                <div className="h-6 bg-muted rounded w-3/4" />
                <div className="h-4 bg-muted rounded w-1/2 mt-2" />
              </CardHeader>
            </Card>
          ))}
        </div>
      ) : pendingInvitations.length === 0 ? (
        <Card>
          <CardContent className="flex flex-col items-center justify-center py-12">
            <Mail className="h-16 w-16 text-muted-foreground mb-4" />
            <h3 className="text-lg font-semibold mb-2">No pending invitations</h3>
            <p className="text-muted-foreground text-center">
              When someone invites you to a group, you'll see it here.
            </p>
          </CardContent>
        </Card>
      ) : (
        <div className="space-y-4">
          {pendingInvitations.map((invitation) => (
            <Card key={invitation.id}>
              <CardHeader className="flex flex-row items-center gap-4">
                <Avatar className="h-12 w-12">
                  <AvatarImage src={invitation.group?.image_url || ''} />
                  <AvatarFallback>
                    {getInitials(invitation.group?.name || 'Group')}
                  </AvatarFallback>
                </Avatar>
                <div className="flex-1">
                  <CardTitle className="text-lg">{invitation.group?.name || 'Unknown Group'}</CardTitle>
                  <CardDescription>
                    Invited by {invitation.invited_by?.name || invitation.invited_by?.email || 'Someone'} on {formatDate(invitation.created_at)}
                  </CardDescription>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => declineMutation.mutate(invitation.id)}
                    disabled={declineMutation.isPending || acceptMutation.isPending}
                  >
                    {declineMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        <X className="mr-1 h-4 w-4" />
                        Decline
                      </>
                    )}
                  </Button>
                  <Button
                    size="sm"
                    onClick={() => acceptMutation.mutate(invitation.id)}
                    disabled={acceptMutation.isPending || declineMutation.isPending}
                  >
                    {acceptMutation.isPending ? (
                      <Loader2 className="h-4 w-4 animate-spin" />
                    ) : (
                      <>
                        <Check className="mr-1 h-4 w-4" />
                        Accept
                      </>
                    )}
                  </Button>
                </div>
              </CardHeader>
            </Card>
          ))}
        </div>
      )}
    </div>
  );
}
