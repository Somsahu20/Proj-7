# Expense Splitting App - Product Requirements Document

## Overview

This document serves as the comprehensive Product Requirements Document (PRD) for the Expense Splitting App. The app enables users to track shared expenses within groups, calculate balances, and manage settlements through a manual payment approval workflow.

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | FastAPI (Python) |
| Database | PostgreSQL |
| Frontend | React 18+ |
| State Management | Zustand |
| Styling | Tailwind CSS |
| UI Components | shadcn/ui |
| Data Fetching | TanStack Query |
| Authentication | OAuth 2.0 (Google) + JWT |
| Real-time | Server-Sent Events (SSE) |
| File Storage | Local Filesystem |
| Notifications | Email Only |

## Document Structure

### [01. Overview](./01-overview/README.md)
- Project Summary
- Tech Stack Details
- System Architecture

### [02. User Management](./02-user-management/README.md)
- Authentication (Google OAuth + Email/Password)
- Profile Management
- Notification Preferences

### [03. Group Management](./03-group-management/README.md)
- Group Creation & Categories
- Member Management & Roles
- Group Settings & Statistics

### [04. Expense Management](./04-expense-management/README.md)
- Expense Creation
- Split Options (Equal, Unequal, Shares, Percentages)
- Expense Categories
- Expense Operations (View, Filter, Edit, Delete)

### [05. Payment Recording](./05-payment-recording/README.md)
- Manual Payment Recording
- Payment Approval Flow
- Payment Proof Upload
- Payment History

### [06. Balance & Settlement](./06-balance-settlement/README.md)
- Balance Calculation
- Debt Simplification Algorithm
- Circular Debt Resolution
- Settlement Flow & Optimization

### [07. Notifications](./07-notifications/README.md)
- Notification Types & Triggers
- Email Templates
- Smart Reminders

### [08. Social & Collaboration](./08-social-collaboration/README.md)
- Comments & Reactions
- Activity Feed (Real-time)
- Expense Approval Workflow

### [09. Trust & Transparency](./09-trust-transparency/README.md)
- Audit Trail
- Dispute Resolution
- Reliability Score
- Payment Confirmation

### [10. Convenience Features](./10-convenience-features/README.md)
- Offline Mode
- Voice Input
- Quick Actions & Shortcuts
- Export History

### [11. UI/UX Design](./11-ui-ux/README.md)
- Design System
- Page Specifications

### [12. API Specifications](./12-api-specifications/README.md)
- REST Endpoints
- SSE Events

### [13. Data Models](./13-data-models/README.md)
- Pydantic Models for FastAPI

### [14. Database Schema](./14-database-schema/README.md)
- PostgreSQL Tables & Relationships

---

## Key Design Decisions

### Payment Flow
The app uses a **manual payment approval** workflow:
1. User A pays User B offline (cash, bank transfer, UPI, etc.)
2. User A records the payment in the app
3. User B receives notification and approves/confirms the payment
4. The debt is marked as settled

### No Auto-Payment
The app does **not** include:
- Virtual wallet system
- Auto-payment/auto-debit functionality
- In-app payment processing
- Credit/debit card integration

### Notification Channels
- Email notifications only
- No push notifications
- No SMS notifications

### Authentication
- Google OAuth for social login
- Email/password for traditional signup
- JWT for session management

---

## Version History

| Version | Date | Description |
|---------|------|-------------|
| 1.0.0 | 2026-01-11 | Initial PRD |
