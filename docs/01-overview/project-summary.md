# Project Summary

## Product Vision

The Expense Splitting App simplifies shared expense management for groups of any size. Whether it's roommates splitting rent, friends sharing trip costs, or couples managing household expenses, the app provides a transparent and efficient way to track who owes whom and settle debts.

## Target Users

### Primary Users
1. **Roommates/Housemates** - Sharing rent, utilities, groceries
2. **Friend Groups** - Splitting costs for outings, trips, events
3. **Couples** - Managing shared household expenses
4. **Hostel Residents** - Tracking communal expenses
5. **Travel Groups** - Managing trip expenses across multiple currencies

### User Characteristics
- Age: 18-45 primarily
- Tech-savvy, comfortable with mobile/web apps
- Value transparency in financial matters
- Prefer settling debts outside the app (cash, bank transfer, UPI)

## Core Value Propositions

### 1. Simplified Expense Tracking
- Quick expense entry with smart defaults
- Multiple split options (equal, unequal, shares, percentages)
- Receipt/image attachment for documentation

### 2. Intelligent Balance Calculation
- Real-time calculation of who owes whom
- Debt simplification to minimize number of transactions
- Circular debt resolution

### 3. Manual Payment Workflow
- Record offline payments (cash, bank transfer, etc.)
- Two-party confirmation for payment verification
- Payment proof upload for transparency

### 4. Group Flexibility
- Multiple group types (trip, apartment, couple, friends, etc.)
- Admin and member roles
- Group-specific expense categories

### 5. Trust & Transparency
- Complete audit trail of all transactions
- Dispute resolution mechanism
- Member reliability scoring

## Goals

### Business Goals
- Provide a free, reliable expense splitting solution
- Build user trust through transparency features
- Enable seamless group financial management

### User Goals
- Easily track shared expenses
- Know exactly how much they owe or are owed
- Settle debts without confusion or conflict
- Have proof of all transactions

### Technical Goals
- Fast, responsive user interface
- Real-time updates via SSE
- Offline capability for expense entry
- Secure authentication and data protection

## Success Metrics

| Metric | Description |
|--------|-------------|
| User Retention | % of users active after 30 days |
| Group Activity | Average expenses added per group per month |
| Settlement Rate | % of debts marked as settled |
| Time to Settlement | Average time from expense creation to settlement |

## Constraints

### Technical Constraints
- Local file storage (no cloud storage services)
- Email-only notifications (no push/SMS)
- Google OAuth only for social login

### Business Constraints
- No in-app payment processing
- No virtual wallet system
- Manual payment recording only

## Out of Scope

The following features are explicitly **not** included:
- Auto-payment/auto-debit functionality
- Virtual wallet with balance
- In-app payment gateway integration (Stripe, PayPal, etc.)
- Push notifications (mobile/web)
- SMS notifications
- Multiple OAuth providers (Facebook, Apple, GitHub)
