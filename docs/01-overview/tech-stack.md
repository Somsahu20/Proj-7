# Tech Stack

## Overview

| Layer | Technology | Version |
|-------|------------|---------|
| Backend Framework | FastAPI | 0.100+ |
| Database | PostgreSQL | 15+ |
| ORM | SQLAlchemy | 2.0+ |
| Migration | Alembic | 1.12+ |
| Frontend Framework | React | 18+ |
| Build Tool | Vite | 5+ |
| State Management | Zustand | 4+ |
| Data Fetching | TanStack Query | 5+ |
| Styling | Tailwind CSS | 3+ |
| UI Components | shadcn/ui | Latest |
| Authentication | JWT + OAuth 2.0 | - |
| Real-time | Server-Sent Events | - |

---

## Backend

### FastAPI
- **Purpose**: REST API framework
- **Why**: High performance, automatic OpenAPI docs, type hints, async support
- **Key Features Used**:
  - Dependency injection
  - Pydantic models for validation
  - OAuth2 with JWT
  - SSE endpoints
  - Background tasks for email

### PostgreSQL
- **Purpose**: Primary database
- **Why**: ACID compliance, JSON support, excellent for relational data
- **Key Features Used**:
  - Foreign key constraints
  - Indexes for performance
  - JSONB for flexible data (notifications preferences)
  - Transactions for data integrity

### SQLAlchemy 2.0
- **Purpose**: ORM and database toolkit
- **Why**: Mature, well-documented, excellent PostgreSQL support
- **Key Features Used**:
  - Declarative models
  - Relationship mapping
  - Query builder
  - Connection pooling

### Alembic
- **Purpose**: Database migrations
- **Why**: Integrates with SQLAlchemy, version control for schema
- **Key Features Used**:
  - Auto-generated migrations
  - Upgrade/downgrade support
  - Migration history tracking

### Pydantic
- **Purpose**: Data validation and serialization
- **Why**: Built into FastAPI, excellent type checking
- **Key Features Used**:
  - Request/response models
  - Settings management
  - Custom validators

---

## Frontend

### React 18
- **Purpose**: UI framework
- **Why**: Component-based, large ecosystem, excellent developer experience
- **Key Features Used**:
  - Functional components
  - Hooks (useState, useEffect, useContext, custom hooks)
  - Suspense for loading states
  - Error boundaries

### Vite
- **Purpose**: Build tool and dev server
- **Why**: Fast hot module replacement, optimized builds
- **Key Features Used**:
  - Dev server with HMR
  - Production builds
  - Environment variables
  - Plugin ecosystem

### Zustand
- **Purpose**: Global state management
- **Why**: Simple API, minimal boilerplate, TypeScript support
- **Key Features Used**:
  - Store creation
  - Selectors
  - Persist middleware (for offline support)
  - DevTools integration

### TanStack Query (React Query)
- **Purpose**: Server state management and data fetching
- **Why**: Caching, background refetching, optimistic updates
- **Key Features Used**:
  - useQuery for data fetching
  - useMutation for data modification
  - Query invalidation
  - Infinite queries for pagination
  - Offline support

### Tailwind CSS
- **Purpose**: Utility-first CSS framework
- **Why**: Rapid development, consistent design, small bundle size
- **Key Features Used**:
  - Utility classes
  - Dark mode support
  - Responsive design utilities
  - Custom theme configuration

### shadcn/ui
- **Purpose**: UI component library
- **Why**: Accessible, customizable, built on Radix UI
- **Key Components Used**:
  - Button, Input, Form
  - Dialog, Sheet, Popover
  - Select, Dropdown Menu
  - Toast, Alert
  - Avatar, Card
  - Tabs, Accordion
  - DataTable

---

## Authentication

### JWT (JSON Web Tokens)
- **Purpose**: Stateless authentication
- **Implementation**:
  - Access token (short-lived, 15 minutes)
  - Refresh token (long-lived, 7 days)
  - Stored in httpOnly cookies

### Google OAuth 2.0
- **Purpose**: Social login
- **Flow**: Authorization Code flow with PKCE
- **Scopes**: email, profile

---

## Real-time Updates

### Server-Sent Events (SSE)
- **Purpose**: Real-time notifications and activity feed
- **Why**: Simpler than WebSocket, one-way is sufficient
- **Implementation**:
  - FastAPI StreamingResponse
  - EventSource API on frontend
  - Automatic reconnection

---

## File Storage

### Local Filesystem
- **Purpose**: Store receipts, profile pictures, payment proofs
- **Structure**:
  ```
  /uploads
    /profiles/{user_id}/
    /expenses/{expense_id}/
    /payments/{payment_id}/
  ```
- **Considerations**:
  - File size limits (5MB for images)
  - Allowed types: jpg, png, pdf
  - Unique filenames with UUID

---

## Email Service

### Configuration Required
- SMTP server configuration
- Options: SendGrid, Mailgun, AWS SES, or custom SMTP
- **Environment Variables**:
  ```
  SMTP_HOST=
  SMTP_PORT=
  SMTP_USER=
  SMTP_PASSWORD=
  FROM_EMAIL=
  ```

---

## Development Tools

| Tool | Purpose |
|------|---------|
| Docker | Containerization |
| Docker Compose | Local development environment |
| pytest | Backend testing |
| Vitest | Frontend testing |
| ESLint | JavaScript/TypeScript linting |
| Prettier | Code formatting |
| Ruff | Python linting |
| Black | Python formatting |

---

## Deployment Considerations

### Backend
- ASGI server: Uvicorn with Gunicorn
- Process manager: systemd or supervisor
- Reverse proxy: Nginx

### Frontend
- Static file hosting
- CDN for assets
- Nginx for serving

### Database
- PostgreSQL with regular backups
- Connection pooling via PgBouncer (optional)
