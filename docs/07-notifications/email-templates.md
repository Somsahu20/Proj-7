# Email Templates

## Overview

All email notifications follow a consistent design and include proper context, action buttons, and unsubscribe options.

---

## Email Structure

### Common Elements

```
┌─────────────────────────────────────────┐
│              App Logo                   │
├─────────────────────────────────────────┤
│                                         │
│  Subject Line                           │
│                                         │
│  Main Content                           │
│                                         │
│  [Primary Action Button]                │
│                                         │
│  Secondary links                        │
│                                         │
├─────────────────────────────────────────┤
│  Footer                                 │
│  - Unsubscribe link                     │
│  - Notification preferences             │
│  - Company info                         │
└─────────────────────────────────────────┘
```

---

## Transaction Emails

### Expense Added

**Subject**: [{group_name}] {actor_name} added a ${amount} expense

**Body**:
```html
Hi {recipient_name},

{actor_name} added a new expense in "{group_name}":

┌─────────────────────────────────────────┐
│ 🍕 {expense_description}                │
│                                         │
│ Total: ${expense_amount}                │
│ Your share: ${my_share}                 │
│ Date: {expense_date}                    │
│ Paid by: {payer_name}                   │
└─────────────────────────────────────────┘

Your new balance in this group: ${new_balance}

[View Expense]  [View Group]

---
You're receiving this because you're a member of "{group_name}".
[Unsubscribe from expense notifications]
```

### Payment Received (Needs Confirmation)

**Subject**: [{group_name}] {payer_name} recorded a ${amount} payment to you

**Body**:
```html
Hi {recipient_name},

{payer_name} has recorded a payment to you in "{group_name}":

┌─────────────────────────────────────────┐
│ 💰 Payment Details                      │
│                                         │
│ Amount: ${amount}                       │
│ From: {payer_name}                      │
│ Method: {payment_method}                │
│ Date: {payment_date}                    │
│ Note: {description}                     │
│                                         │
│ [📷 View Proof] (if attached)           │
└─────────────────────────────────────────┘

Please confirm if you received this payment:

[✓ Confirm Payment]  [✗ Reject Payment]

If you didn't receive this payment, reject it and the payer will be notified.

---
You must respond to this payment request.
```

### Payment Confirmed

**Subject**: [{group_name}] {receiver_name} confirmed your ${amount} payment

**Body**:
```html
Hi {payer_name},

Great news! {receiver_name} has confirmed receiving your payment.

┌─────────────────────────────────────────┐
│ ✅ Payment Confirmed                    │
│                                         │
│ Amount: ${amount}                       │
│ To: {receiver_name}                     │
│ Date: {confirmation_date}               │
└─────────────────────────────────────────┘

Your balance in "{group_name}" has been updated.
New balance: ${new_balance}

[View Group]

---
Keep up the good work settling your expenses!
```

### Payment Rejected

**Subject**: [{group_name}] {receiver_name} rejected your ${amount} payment

**Body**:
```html
Hi {payer_name},

{receiver_name} has rejected your recorded payment in "{group_name}".

┌─────────────────────────────────────────┐
│ ❌ Payment Rejected                     │
│                                         │
│ Amount: ${amount}                       │
│ Reason: {rejection_reason}              │
└─────────────────────────────────────────┘

If you believe this is a mistake, you can:
- Contact {receiver_name} to clarify
- Open a dispute if you have proof of payment

[View Payment]  [Open Dispute]

---
Your balance has not been affected.
```

---

## Group Emails

### Added to Group

**Subject**: You've been added to "{group_name}"

**Body**:
```html
Hi {recipient_name},

{inviter_name} has added you to "{group_name}".

┌─────────────────────────────────────────┐
│ 👥 {group_name}                         │
│                                         │
│ Category: {category}                    │
│ Members: {member_count}                 │
│ Description: {description}              │
└─────────────────────────────────────────┘

[View Group]

---
Welcome to the group! Start by adding your first expense.
```

### Group Invitation

**Subject**: {inviter_name} invited you to join "{group_name}"

**Body**:
```html
Hi!

{inviter_name} has invited you to join "{group_name}" on Expense Splitter.

┌─────────────────────────────────────────┐
│ 👥 {group_name}                         │
│                                         │
│ Category: {category}                    │
│ Description: {description}              │
│ Current members: {member_list}          │
└─────────────────────────────────────────┘

[Accept Invitation]  [Decline]

This invitation expires on {expiry_date}.

---
Don't have an account? Accepting will help you create one.
```

---

## Balance Emails

### Balance Reminder

**Subject**: [{group_name}] Reminder: You owe ${amount}

**Body**:
```html
Hi {recipient_name},

This is a friendly reminder about your outstanding balance in "{group_name}".

┌─────────────────────────────────────────┐
│ 📊 Your Balance                         │
│                                         │
│ You owe: ${total_owed}                  │
│                                         │
│ Pay to:                                 │
│   {creditor_1}: ${amount_1}             │
│   {creditor_2}: ${amount_2}             │
└─────────────────────────────────────────┘

[Settle Up Now]

---
Tip: Settling up keeps your group finances clear and relationships healthy!
```

### Debt Cleared

**Subject**: 🎉 [{group_name}] You're all settled up!

**Body**:
```html
Hi {recipient_name},

Congratulations! You've cleared all your debts in "{group_name}".

┌─────────────────────────────────────────┐
│ ✨ All Settled!                         │
│                                         │
│ Your balance: $0.00                     │
│ Group: {group_name}                     │
└─────────────────────────────────────────┘

Great job keeping your finances in order!

[View Group]

---
Keep the momentum going!
```

---

## Digest Emails

### Daily Digest

**Subject**: Your daily expense summary - {date}

**Body**:
```html
Hi {recipient_name},

Here's your expense summary for {date}:

┌─────────────────────────────────────────┐
│ 📊 Daily Summary                        │
├─────────────────────────────────────────┤
│                                         │
│ New expenses: {expense_count}           │
│ Total added: ${total_amount}            │
│ Your share: ${total_share}              │
│                                         │
│ By Group:                               │
│   Trip to Paris: {count} expenses       │
│   Apartment: {count} expenses           │
│                                         │
│ Pending payments: {payment_count}       │
│ Awaiting your confirmation: {count}     │
└─────────────────────────────────────────┘

[View Dashboard]

---
This is your daily digest. Manage frequency in settings.
```

### Weekly Digest

**Subject**: Your weekly expense summary - Week of {start_date}

**Body**:
```html
Hi {recipient_name},

Here's your expense summary for the week of {start_date}:

┌─────────────────────────────────────────┐
│ 📊 Weekly Summary                       │
├─────────────────────────────────────────┤
│                                         │
│ Total expenses: ${total_amount}         │
│ Your share: ${total_share}              │
│ Payments made: ${payments_made}         │
│ Payments received: ${payments_received} │
│                                         │
│ Current Balances:                       │
│   Trip to Paris: -${amount}             │
│   Apartment: +${amount}                 │
│   Total: ${net_balance}                 │
│                                         │
│ Top Categories:                         │
│   🍕 Food & Drinks: ${amount}           │
│   🚗 Transport: ${amount}               │
└─────────────────────────────────────────┘

[View Dashboard]

---
This is your weekly digest. Manage frequency in settings.
```

---

## Email Footer

### Standard Footer

```html
---
You're receiving this email because you have an account on Expense Splitter.

[Notification Settings] | [Unsubscribe]

Expense Splitter
© 2026 All rights reserved.
```

### Quick Unsubscribe

Each email type has a specific unsubscribe link:
- `[Unsubscribe from expense notifications]`
- `[Unsubscribe from payment notifications]`
- `[Unsubscribe from all emails]`

---

## Styling Guidelines

### Colors
- Primary: #3B82F6 (blue)
- Success: #10B981 (green)
- Warning: #F59E0B (amber)
- Error: #EF4444 (red)
- Text: #1F2937 (gray-800)

### Fonts
- Headings: System font stack (sans-serif)
- Body: 16px, line-height 1.5
- Buttons: 14px, bold

### Responsiveness
- Max width: 600px
- Mobile-friendly layout
- Large tap targets for buttons

---

## Acceptance Criteria

### Content
- [ ] Subject lines are clear and contextual
- [ ] Body contains all relevant information
- [ ] Action buttons are prominent
- [ ] Unsubscribe link present

### Styling
- [ ] Consistent branding
- [ ] Mobile responsive
- [ ] Dark mode compatible (where supported)

### Functionality
- [ ] Links work correctly
- [ ] Unsubscribe works
- [ ] Personalization is accurate
