export interface User {
  id: string;
  email: string;
  name: string;
  phone?: string;
  profile_picture?: string;
  is_active: boolean;
  is_verified: boolean;
  reliability_score: number;
  created_at: string;
  notification_preferences?: NotificationPreferences;
  last_login_at?: string;
  google_id?: string;
  hashed_password?: string;
}

export interface NotificationPreferences {
  expense_added: boolean;
  expense_edited: boolean;
  expense_deleted: boolean;
  payment_received: boolean;
  payment_confirmed: boolean;
  added_to_group: boolean;
  balance_reminder: boolean;
  weekly_digest: boolean;
  digest_day: string;
}

export interface Group {
  id: string;
  name: string;
  description?: string;
  category: string;
  image_url?: string;
  created_by_id: string;
  is_archived: boolean;
  settings: Record<string, unknown>;
  created_at: string;
  member_count?: number;
}

export interface GroupDetail extends Group {
  creator: User;
  members: Member[];
  total_expenses: number;
  your_balance: number;
}

export interface Member {
  id: string;
  user_id: string;
  group_id: string;
  role: 'admin' | 'member';
  joined_at: string;
  is_active: boolean;
  user: User;
}

export interface Expense {
  id: string;
  group_id: string;
  description: string;
  amount: number;
  date: string;
  payer_id: string;
  split_type: 'equal' | 'unequal' | 'shares' | 'percentage';
  category?: string;
  notes?: string;
  receipt_url?: string;
  created_by_id: string;
  is_deleted: boolean;
  approval_status: string;
  created_at: string;
  updated_at?: string;
  payer?: User;
  splits: ExpenseSplit[];
  comment_count?: number;
  reaction_count?: number;
}

export interface ExpenseSplit {
  id: string;
  expense_id: string;
  user_id: string;
  amount: number;
  shares?: number;
  percentage?: number;
  is_settled: boolean;
  user?: User;
}

export interface Payment {
  id: string;
  group_id: string;
  payer_id: string;
  receiver_id: string;
  amount: number;
  description?: string;
  payment_method?: string;
  date: string;
  status: 'pending' | 'confirmed' | 'rejected' | 'cancelled' | 'disputed';
  confirmed_at?: string;
  rejected_at?: string;
  rejected_reason?: string;
  created_at: string;
  payer?: User;
  receiver?: User;
  proofs: PaymentProof[];
}

export interface PaymentProof {
  id: string;
  payment_id: string;
  file_url: string;
  file_type: string;
  file_size: number;
  uploaded_at: string;
}

export interface Notification {
  id: string;
  type: string;
  title: string;
  body: string;
  data: Record<string, unknown>;
  action_url?: string;
  is_read: boolean;
  created_at: string;
}

export interface Balance {
  user_id: string;
  user_name: string;
  user_email: string;
  balance: number;
  profile_picture?: string;
}

export interface GroupBalance {
  group_id: string;
  group_name: string;
  your_total_balance: number;
  balances: Balance[];
}

export interface BalanceOverview {
  total_balance: number;
  you_are_owed: number;
  you_owe: number;
  group_balances: GroupBalance[];
}

export interface SettlementSuggestion {
  from_user_id: string;
  from_user_name: string;
  to_user_id: string;
  to_user_name: string;
  amount: number;
}

export interface Comment {
  id: string;
  expense_id: string;
  user_id: string;
  parent_id?: string;
  content: string;
  mentions: string[];
  is_deleted: boolean;
  created_at: string;
  updated_at?: string;
  user?: User;
  replies: Comment[];
}

export interface Reaction {
  emoji: string;
  count: number;
  users: User[];
}

export interface Activity {
  id: string;
  group_id?: string;
  user_id?: string;
  action: string;
  entity_type: string;
  entity_id?: string;
  data: Record<string, unknown>;
  created_at: string;
  user?: User;
}

export interface Invitation {
  id: string;
  group_id: string;
  email: string;
  status: string;
  expires_at: string;
  created_at: string;
  group_name?: string;
  invited_by_name?: string;
  group?: {
    id: string;
    name: string;
    image_url?: string;
  };
  invited_by?: {
    id: string;
    name: string;
    email: string;
  };
}

export interface Friend {
  id: string;
  email: string;
  name: string;
  profile_picture?: string;
  friendship_id: string;
  friend_group_id?: string;
  balance: number;
}

export interface Friendship {
  id: string;
  requester_id: string;
  addressee_id: string;
  status: 'pending' | 'accepted' | 'declined' | 'blocked';
  friend_group_id?: string;
  created_at: string;
  accepted_at?: string;
  friend: User;
}

export interface FriendList {
  friends: Friend[];
  pending_sent: Friendship[];
  pending_received: Friendship[];
}

export interface DisputeVote {
  id: string;
  dispute_id: string;
  user_id: string;
  vote: 'approve' | 'reject' | 'abstain';
  comment?: string;
  created_at: string;
}

export interface Dispute {
  id: string;
  expense_id?: string;
  payment_id?: string;
  opened_by_id: string;
  reason: string;
  description: string;
  evidence_urls: string[];
  status: 'open' | 'voting' | 'resolved';
  resolution?: 'upheld' | 'dismissed' | 'modified';
  resolved_by_id?: string;
  resolved_at?: string;
  resolution_notes?: string;
  voting_ends_at?: string;
  created_at: string;
  votes: DisputeVote[];
  vote_summary?: {
    approve: number;
    reject: number;
    abstain: number;
  } | null;
}
