# MoneyByte - Expense Splitting Application

A full-stack expense splitting application built with FastAPI (backend) and React (frontend).

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL** - Database
- **SQLAlchemy** - ORM with async support
- **JWT** - Authentication
- **Google OAuth 2.0** - Social login

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui** - Component library
- **Zustand** - State management
- **TanStack Query** - Data fetching
- **React Router** - Routing

## Features

- User authentication (Email/Password + Google OAuth)
- Group management with roles (Admin/Member)
- Expense tracking with multiple split types (Equal, Unequal, Shares, Percentage)
- Manual payment recording with approval workflow
- Real-time balance calculation
- Debt simplification algorithm
- Notifications with SSE support
- Comments and reactions on expenses
- Activity feed
- Dispute resolution with voting

## Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- PostgreSQL 14+

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file from example:
```bash
cp .env.example .env
```

5. Update `.env` with your settings (database URL, Google OAuth credentials, etc.)

6. Create PostgreSQL database:
```bash
createdb moneybyte
```

7. Run the backend:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API docs: `http://localhost:8000/api/v1/docs`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Start development server:
```bash
npm run dev
```

The frontend will be available at `http://localhost:5173`

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login with email/password
- `GET /api/v1/auth/google` - Initiate Google OAuth
- `GET /api/v1/auth/google/callback` - Google OAuth callback

### Users
- `GET /api/v1/users/me` - Get current user profile
- `PATCH /api/v1/users/me` - Update profile
- `POST /api/v1/users/me/avatar` - Upload avatar
- `POST /api/v1/users/me/change-password` - Change password

### Groups
- `GET /api/v1/groups` - List user's groups
- `POST /api/v1/groups` - Create group
- `GET /api/v1/groups/{id}` - Get group details
- `PATCH /api/v1/groups/{id}` - Update group
- `DELETE /api/v1/groups/{id}` - Delete group
- `POST /api/v1/groups/{id}/invitations` - Invite member
- `POST /api/v1/groups/invitations/accept` - Accept invitation

### Expenses
- `GET /api/v1/expenses` - List expenses (with filters)
- `POST /api/v1/expenses` - Create expense
- `GET /api/v1/expenses/{id}` - Get expense details
- `PATCH /api/v1/expenses/{id}` - Update expense
- `DELETE /api/v1/expenses/{id}` - Delete expense
- `POST /api/v1/expenses/{id}/receipt` - Upload receipt

### Payments
- `GET /api/v1/payments` - List payments
- `GET /api/v1/payments/pending` - List pending confirmations
- `POST /api/v1/payments` - Record payment
- `POST /api/v1/payments/{id}/confirm` - Confirm payment
- `POST /api/v1/payments/{id}/reject` - Reject payment
- `POST /api/v1/payments/{id}/proof` - Upload payment proof

### Balances
- `GET /api/v1/balances` - Get overall balances
- `GET /api/v1/balances/group/{id}` - Get group balances
- `GET /api/v1/balances/group/{id}/settlements` - Get settlement suggestions

### Notifications
- `GET /api/v1/notifications` - List notifications
- `GET /api/v1/notifications/unread-count` - Get unread count
- `POST /api/v1/notifications/mark-read` - Mark as read
- `GET /api/v1/notifications/stream/events` - SSE stream

### Social
- `GET /api/v1/expenses/{id}/comments` - List comments
- `POST /api/v1/expenses/{id}/comments` - Add comment
- `GET /api/v1/expenses/{id}/reactions` - List reactions
- `POST /api/v1/expenses/{id}/reactions` - Add reaction

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/      # API endpoints
│   │   │   ├── deps.py         # Dependencies
│   │   │   └── router.py       # API router
│   │   ├── core/
│   │   │   ├── config.py       # Settings
│   │   │   └── security.py     # JWT/Password
│   │   ├── db/
│   │   │   └── database.py     # Database setup
│   │   ├── models/
│   │   │   └── models.py       # SQLAlchemy models
│   │   ├── schemas/            # Pydantic schemas
│   │   └── main.py             # FastAPI app
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/         # React components
│   │   ├── pages/              # Page components
│   │   ├── services/           # API services
│   │   ├── store/              # Zustand stores
│   │   ├── types/              # TypeScript types
│   │   └── lib/                # Utilities
│   └── package.json
│
└── docs/                       # PRD documentation
```

## License

MIT
