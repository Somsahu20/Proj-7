# System Architecture

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                            │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    React Frontend                        │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │   │
│  │  │ Zustand  │  │ TanStack │  │  shadcn  │  │Tailwind │  │   │
│  │  │  Store   │  │  Query   │  │    UI    │  │   CSS   │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ HTTP/SSE
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                         API LAYER                               │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    FastAPI Backend                       │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌─────────┐  │   │
│  │  │  Routes  │  │ Services │  │  Models  │  │  Auth   │  │   │
│  │  │(Routers) │  │ (Logic)  │  │(Pydantic)│  │  (JWT)  │  │   │
│  │  └──────────┘  └──────────┘  └──────────┘  └─────────┘  │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
                              │
                              │ SQLAlchemy
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                        DATA LAYER                               │
│  ┌───────────────────────┐  ┌────────────────────────────────┐ │
│  │      PostgreSQL       │  │      Local File System         │ │
│  │  ┌─────┐ ┌─────────┐  │  │  ┌─────────┐ ┌─────────────┐  │ │
│  │  │Users│ │ Groups  │  │  │  │Profiles │ │  Receipts   │  │ │
│  │  │     │ │Expenses │  │  │  │ Images  │ │Payment Proof│  │ │
│  │  └─────┘ └─────────┘  │  │  └─────────┘ └─────────────┘  │ │
│  └───────────────────────┘  └────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

## Component Architecture

### Frontend Structure

```
src/
├── components/           # Reusable UI components
│   ├── ui/              # shadcn/ui components
│   ├── forms/           # Form components
│   ├── layouts/         # Layout components
│   └── shared/          # Shared components
├── pages/               # Page components
│   ├── auth/            # Login, Signup, Reset
│   ├── dashboard/       # Main dashboard
│   ├── groups/          # Group pages
│   ├── expenses/        # Expense pages
│   ├── balances/        # Balance pages
│   ├── settings/        # Settings pages
│   └── notifications/   # Notification pages
├── hooks/               # Custom React hooks
├── stores/              # Zustand stores
├── services/            # API service functions
├── lib/                 # Utility functions
├── types/               # TypeScript types
└── styles/              # Global styles
```

### Backend Structure

```
app/
├── api/                 # API routes
│   ├── v1/
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── groups.py
│   │   ├── expenses.py
│   │   ├── payments.py
│   │   ├── balances.py
│   │   ├── notifications.py
│   │   └── sse.py
│   └── deps.py          # Dependencies
├── core/                # Core functionality
│   ├── config.py        # Settings
│   ├── security.py      # JWT, hashing
│   └── email.py         # Email sending
├── models/              # SQLAlchemy models
│   ├── user.py
│   ├── group.py
│   ├── expense.py
│   ├── payment.py
│   └── notification.py
├── schemas/             # Pydantic schemas
│   ├── user.py
│   ├── group.py
│   ├── expense.py
│   ├── payment.py
│   └── notification.py
├── services/            # Business logic
│   ├── user_service.py
│   ├── group_service.py
│   ├── expense_service.py
│   ├── payment_service.py
│   ├── balance_service.py
│   └── notification_service.py
├── db/                  # Database
│   ├── session.py
│   └── base.py
└── main.py              # Application entry
```

## Data Flow

### Expense Creation Flow

```
┌────────┐    ┌────────┐    ┌────────┐    ┌──────────┐    ┌────────┐
│  User  │───▶│ React  │───▶│FastAPI │───▶│ Service  │───▶│Postgres│
│        │    │  Form  │    │ Route  │    │  Layer   │    │   DB   │
└────────┘    └────────┘    └────────┘    └──────────┘    └────────┘
                                               │
                                               ▼
                                         ┌──────────┐
                                         │  Email   │
                                         │Notifier  │
                                         └──────────┘
                                               │
                                               ▼
                                         ┌──────────┐
                                         │   SSE    │
                                         │ Broadcast│
                                         └──────────┘
```

### Payment Approval Flow

```
┌─────────┐     ┌─────────┐     ┌─────────┐     ┌─────────┐
│ Payer   │     │Receiver │     │ Backend │     │Database │
└────┬────┘     └────┬────┘     └────┬────┘     └────┬────┘
     │               │               │               │
     │ Record Payment│               │               │
     │──────────────────────────────▶│               │
     │               │               │  Save Payment │
     │               │               │  (PENDING)    │
     │               │               │──────────────▶│
     │               │               │               │
     │               │ Email + SSE   │               │
     │               │◀──────────────│               │
     │               │               │               │
     │               │ Approve       │               │
     │               │──────────────▶│               │
     │               │               │Update Payment │
     │               │               │ (CONFIRMED)   │
     │               │               │──────────────▶│
     │               │               │               │
     │ Email + SSE   │               │               │
     │◀──────────────────────────────│               │
     │               │               │               │
```

## Authentication Flow

### Login with Google OAuth

```
┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐    ┌────────┐
│  User  │───▶│ React  │───▶│ Google │───▶│FastAPI │───▶│  JWT   │
│        │    │  App   │    │ OAuth  │    │Callback│    │ Issued │
└────────┘    └────────┘    └────────┘    └────────┘    └────────┘
```

1. User clicks "Login with Google"
2. React redirects to Google OAuth consent screen
3. User authorizes the app
4. Google redirects back with authorization code
5. FastAPI exchanges code for tokens
6. FastAPI creates/updates user in database
7. FastAPI issues JWT access + refresh tokens
8. Tokens stored in httpOnly cookies
9. User redirected to dashboard

### JWT Token Refresh

```
┌────────┐    ┌────────┐    ┌────────┐
│ React  │───▶│FastAPI │───▶│  New   │
│  App   │    │/refresh│    │ Tokens │
└────────┘    └────────┘    └────────┘
```

## Real-time Architecture (SSE)

```
┌─────────────────────────────────────────────────────────────┐
│                     FastAPI Server                          │
│  ┌───────────────────────────────────────────────────────┐  │
│  │                  SSE Manager                          │  │
│  │  ┌─────────────────────────────────────────────────┐  │  │
│  │  │           Connection Registry                   │  │  │
│  │  │  user_123: [connection_1, connection_2]        │  │  │
│  │  │  user_456: [connection_3]                      │  │  │
│  │  └─────────────────────────────────────────────────┘  │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
        ┌──────────┐   ┌──────────┐    ┌──────────┐
        │ Browser  │   │ Browser  │    │ Browser  │
        │  Tab 1   │   │  Tab 2   │    │  Tab 3   │
        └──────────┘   └──────────┘    └──────────┘
```

### Event Types

| Event | Payload | Recipients |
|-------|---------|------------|
| `expense:created` | Expense data | Group members |
| `expense:updated` | Expense data | Group members |
| `expense:deleted` | Expense ID | Group members |
| `payment:recorded` | Payment data | Payer + Receiver |
| `payment:approved` | Payment data | Payer + Receiver |
| `balance:updated` | Balance data | Affected users |
| `notification:new` | Notification | Target user |

## Database Architecture

### Entity Relationship Overview

```
┌─────────┐       ┌────────────┐       ┌─────────┐
│  User   │◀─────▶│ Membership │◀─────▶│  Group  │
└────┬────┘       └────────────┘       └────┬────┘
     │                                      │
     │            ┌─────────────┐           │
     └───────────▶│   Expense   │◀──────────┘
                  └──────┬──────┘
                         │
                  ┌──────┴──────┐
                  ▼             ▼
            ┌──────────┐  ┌──────────┐
            │  Split   │  │ Receipt  │
            └──────────┘  └──────────┘
                  │
                  ▼
            ┌──────────┐
            │ Payment  │
            └──────────┘
```

## Security Architecture

### Authentication Layers

1. **Transport Security**: HTTPS only
2. **JWT Validation**: Every protected endpoint
3. **CORS Configuration**: Allowed origins list
4. **Rate Limiting**: Per-user request limits
5. **Input Validation**: Pydantic models

### Authorization Model

```
┌─────────────────────────────────────────────────────────────┐
│                    Authorization Check                       │
│  ┌─────────────────────────────────────────────────────┐    │
│  │ 1. Is user authenticated? (JWT valid)               │    │
│  │ 2. Is user a member of the group?                   │    │
│  │ 3. Does user have required role? (admin/member)     │    │
│  │ 4. Is user the owner of the resource? (for edit)    │    │
│  └─────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────┘
```

## Offline Architecture

### Sync Strategy

```
┌─────────────────────────────────────────────────────────────┐
│                     Offline Mode                            │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              IndexedDB (Browser)                     │   │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────────┐   │   │
│  │  │  Pending  │  │   Local   │  │    Cached     │   │   │
│  │  │  Actions  │  │   Data    │  │   Responses   │   │   │
│  │  └───────────┘  └───────────┘  └───────────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                           │                                 │
│                           ▼                                 │
│  ┌─────────────────────────────────────────────────────┐   │
│  │            Background Sync (on reconnect)           │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

1. User creates expense while offline
2. Expense saved to IndexedDB with `pending` flag
3. When online, background sync uploads pending expenses
4. Server validates and saves
5. Local storage updated with server response
6. Conflicts resolved (server wins for same expense)
