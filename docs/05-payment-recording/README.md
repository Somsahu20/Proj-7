# 05. Payment Recording

This section covers the manual payment workflow where users record offline payments and receivers approve them.

## Section Contents

| Document | Description |
|----------|-------------|
| [Record Payment](./record-payment.md) | How users record offline payments |
| [Payment Approval](./payment-approval.md) | Receiver confirmation/rejection flow |
| [Payment Proof](./payment-proof.md) | Uploading receipts and screenshots |
| [Payment History](./payment-history.md) | Viewing payment records and status |

## Payment Flow Overview

```
┌─────────┐     ┌─────────────┐     ┌─────────────┐     ┌──────────┐
│ Payer   │────▶│ Pays Offline│────▶│Records in   │────▶│ Receiver │
│         │     │ (Cash/Bank) │     │    App      │     │ Approves │
└─────────┘     └─────────────┘     └─────────────┘     └──────────┘
```

## Key Concepts

### No In-App Payments
- Users pay each other outside the app (cash, bank transfer, UPI, etc.)
- App only records and tracks these payments
- No virtual wallet or auto-debit

### Two-Party Confirmation
- Payer records the payment
- Receiver must approve/confirm
- Both parties agree before debt is settled

### Payment States

| State | Description |
|-------|-------------|
| `pending` | Payment recorded, awaiting receiver confirmation |
| `confirmed` | Receiver has approved the payment |
| `rejected` | Receiver has rejected the payment |
| `cancelled` | Payer has cancelled the payment |
