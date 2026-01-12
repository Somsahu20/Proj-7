import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { useNavigate } from 'react-router-dom';
import { friendsService } from '@/services/friends';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Dialog, DialogContent, DialogDescription, DialogFooter, DialogHeader, DialogTitle, DialogTrigger } from '@/components/ui/dialog';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { formatDate, getInitials, formatCurrency } from '@/lib/utils';
import { UserPlus, Users, Check, X, Loader2, Trash2, Receipt } from 'lucide-react';

export function FriendsPage() {
  const navigate = useNavigate();
  const queryClient = useQueryClient();
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [email, setEmail] = useState('');

  const { data: friendData, isLoading } = useQuery({
    queryKey: ['friends'],
    queryFn: friendsService.getFriends,
  });

  const sendRequestMutation = useMutation({
    mutationFn: friendsService.sendFriendRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['friends'] });
      setIsDialogOpen(false);
      setEmail('');
    },
  });

  const acceptMutation = useMutation({
    mutationFn: friendsService.acceptFriendRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['friends'] });
    },
  });

  const declineMutation = useMutation({
    mutationFn: friendsService.declineFriendRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['friends'] });
    },
  });

  const removeMutation = useMutation({
    mutationFn: friendsService.removeFriend,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['friends'] });
    },
  });

  const handleSendRequest = () => {
    if (!email.trim()) return;
    sendRequestMutation.mutate(email);
  };

  const handleViewExpenses = async (friendId: string) => {
    try {
      const { group_id } = await friendsService.getFriendGroup(friendId);
      navigate(`/groups/${group_id}`);
    } catch (error) {
      console.error('Failed to get friend group:', error);
    }
  };

  const friends = friendData?.friends || [];
  const pendingSent = friendData?.pending_sent || [];
  const pendingReceived = friendData?.pending_received || [];

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Friends</h1>
          <p className="text-muted-foreground">Manage your friends and direct expenses</p>
        </div>
        <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
          <DialogTrigger asChild>
            <Button>
              <UserPlus className="mr-2 h-4 w-4" />
              Add Friend
            </Button>
          </DialogTrigger>
          <DialogContent>
            <DialogHeader>
              <DialogTitle>Add a Friend</DialogTitle>
              <DialogDescription>
                Send a friend request by entering their email address.
              </DialogDescription>
            </DialogHeader>
            <div className="space-y-4 py-4">
              <div className="space-y-2">
                <Label htmlFor="email">Email Address</Label>
                <Input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="friend@example.com"
                />
              </div>
              {sendRequestMutation.isError && (
                <p className="text-sm text-destructive">
                  {(sendRequestMutation.error as Error)?.message || 'Failed to send request'}
                </p>
              )}
            </div>
            <DialogFooter>
              <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                Cancel
              </Button>
              <Button onClick={handleSendRequest} disabled={sendRequestMutation.isPending}>
                {sendRequestMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Send Request
              </Button>
            </DialogFooter>
          </DialogContent>
        </Dialog>
      </div>

      <Tabs defaultValue="friends">
        <TabsList>
          <TabsTrigger value="friends">
            Friends ({friends.length})
          </TabsTrigger>
          <TabsTrigger value="requests">
            Requests ({pendingReceived.length})
          </TabsTrigger>
          <TabsTrigger value="sent">
            Sent ({pendingSent.length})
          </TabsTrigger>
        </TabsList>

        <TabsContent value="friends" className="mt-4">
          {isLoading ? (
            <div className="space-y-4">
              {[1, 2, 3].map((i) => (
                <Card key={i} className="animate-pulse">
                  <CardHeader>
                    <div className="h-6 bg-muted rounded w-3/4" />
                  </CardHeader>
                </Card>
              ))}
            </div>
          ) : friends.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <Users className="h-16 w-16 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No friends yet</h3>
                <p className="text-muted-foreground text-center mb-4">
                  Add friends to easily split expenses directly without creating a group.
                </p>
                <Button onClick={() => setIsDialogOpen(true)}>
                  <UserPlus className="mr-2 h-4 w-4" />
                  Add Your First Friend
                </Button>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {friends.map((friend) => (
                <Card key={friend.friendship_id}>
                  <CardHeader className="flex flex-row items-center gap-4">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={friend.profile_picture || ''} />
                      <AvatarFallback>{getInitials(friend.name)}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <CardTitle className="text-lg">{friend.name}</CardTitle>
                      <CardDescription>{friend.email}</CardDescription>
                    </div>
                    <div className="text-right mr-4">
                      <p className={`text-sm font-medium ${friend.balance > 0 ? 'text-green-600' : friend.balance < 0 ? 'text-red-600' : 'text-muted-foreground'}`}>
                        {friend.balance > 0 ? `owes you ${formatCurrency(friend.balance)}` :
                         friend.balance < 0 ? `you owe ${formatCurrency(Math.abs(friend.balance))}` :
                         'settled up'}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => handleViewExpenses(friend.id)}
                      >
                        <Receipt className="mr-1 h-4 w-4" />
                        Expenses
                      </Button>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => removeMutation.mutate(friend.friendship_id)}
                        disabled={removeMutation.isPending}
                      >
                        <Trash2 className="h-4 w-4 text-destructive" />
                      </Button>
                    </div>
                  </CardHeader>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>

        <TabsContent value="requests" className="mt-4">
          {pendingReceived.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <UserPlus className="h-16 w-16 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No pending requests</h3>
                <p className="text-muted-foreground text-center">
                  Friend requests you receive will appear here.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {pendingReceived.map((request) => (
                <Card key={request.id}>
                  <CardHeader className="flex flex-row items-center gap-4">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={request.friend.profile_picture || ''} />
                      <AvatarFallback>{getInitials(request.friend.name)}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <CardTitle className="text-lg">{request.friend.name}</CardTitle>
                      <CardDescription>
                        {request.friend.email} - Sent {formatDate(request.created_at)}
                      </CardDescription>
                    </div>
                    <div className="flex gap-2">
                      <Button
                        variant="outline"
                        size="sm"
                        onClick={() => declineMutation.mutate(request.id)}
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
                        onClick={() => acceptMutation.mutate(request.id)}
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
        </TabsContent>

        <TabsContent value="sent" className="mt-4">
          {pendingSent.length === 0 ? (
            <Card>
              <CardContent className="flex flex-col items-center justify-center py-12">
                <UserPlus className="h-16 w-16 text-muted-foreground mb-4" />
                <h3 className="text-lg font-semibold mb-2">No sent requests</h3>
                <p className="text-muted-foreground text-center">
                  Friend requests you send will appear here until accepted.
                </p>
              </CardContent>
            </Card>
          ) : (
            <div className="space-y-4">
              {pendingSent.map((request) => (
                <Card key={request.id}>
                  <CardHeader className="flex flex-row items-center gap-4">
                    <Avatar className="h-12 w-12">
                      <AvatarImage src={request.friend.profile_picture || ''} />
                      <AvatarFallback>{getInitials(request.friend.name)}</AvatarFallback>
                    </Avatar>
                    <div className="flex-1">
                      <CardTitle className="text-lg">{request.friend.name}</CardTitle>
                      <CardDescription>
                        {request.friend.email} - Sent {formatDate(request.created_at)}
                      </CardDescription>
                    </div>
                    <span className="text-sm text-muted-foreground">Pending</span>
                  </CardHeader>
                </Card>
              ))}
            </div>
          )}
        </TabsContent>
      </Tabs>
    </div>
  );
}
