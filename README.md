# MoneyByte - Expense Splitting Application

A full-stack expense splitting application built with FastAPI (backend) and React (frontend), with Docker support for easy deployment.

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **PostgreSQL 15** - Database
- **SQLAlchemy 2.0** - Async ORM
- **JWT + bcrypt** - Authentication
- **Google OAuth 2.0** - Social login
- **SSE** - Real-time notifications

### Frontend
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **shadcn/ui (Radix)** - Component library
- **Zustand** - State management
- **TanStack Query** - Data fetching
- **React Router** - Routing
- **Recharts** - Data visualization

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
- Friends management
- Analytics dashboard

## Getting Started

### Option 1: Docker (Recommended)

The easiest way to run the application:

```bash
# Clone the repository
git clone <repository-url>
cd Proj

# Create .env file with your settings
cp backend/.env.example .env

# Update .env with your configuration (especially SECRET_KEY and Google OAuth)

# Start all services
docker-compose up -d
```

The application will be available at:
- Frontend: `http://localhost`
- Backend API: `http://localhost:8000`
- API Docs: `http://localhost:8000/api/v1/docs`

#### Docker Services
| Service | Container | Port |
|---------|-----------|------|
| PostgreSQL | moneybyte-db | 5432 |
| FastAPI Backend | moneybyte-backend | 8000 |
| React Frontend (nginx) | moneybyte-frontend | 80 |

### Option 2: Local Development

#### Prerequisites
- Python 3.11+
- Node.js 20+
- PostgreSQL 15+

#### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Update .env with your settings

# Create database
createdb moneybyte

# Run the backend
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`
API docs: `http://localhost:8000/api/v1/docs`

#### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will be available at `http://localhost:5173`

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (min 32 chars) | Required |
| `DATABASE_URL` | PostgreSQL connection string | Required |
| `GOOGLE_CLIENT_ID` | Google OAuth client ID | Optional |
| `GOOGLE_CLIENT_SECRET` | Google OAuth secret | Optional |
| `GOOGLE_REDIRECT_URI` | OAuth callback URL | `http://localhost:8000/api/v1/auth/google/callback` |
| `FRONTEND_URL` | Frontend URL for CORS | `http://localhost:5173` |
| `SMTP_HOST` | Email server host | `smtp.gmail.com` |
| `SMTP_PORT` | Email server port | `587` |
| `SMTP_USER` | Email username | Optional |
| `SMTP_PASSWORD` | Email password | Optional |
| `MAX_FILE_SIZE` | Max upload size in bytes | `10485760` (10MB) |

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
- `GET /api/v1/users/me/invitations` - Get pending invitations

### Groups
- `GET /api/v1/groups` - List user's groups
- `POST /api/v1/groups` - Create group
- `GET /api/v1/groups/{id}` - Get group details
- `PATCH /api/v1/groups/{id}` - Update group
- `DELETE /api/v1/groups/{id}` - Delete group
- `POST /api/v1/groups/{id}/invitations` - Invite member
- `POST /api/v1/groups/{id}/image` - Upload group image

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

### Disputes
- `POST /api/v1/disputes` - Raise a dispute
- `GET /api/v1/disputes/{id}` - Get dispute details
- `POST /api/v1/disputes/{id}/vote` - Vote on dispute
- `POST /api/v1/disputes/{id}/resolve` - Resolve dispute

### Friends
- `GET /api/v1/friends` - List friends
- `POST /api/v1/friends/request` - Send friend request
- `POST /api/v1/friends/{id}/accept` - Accept request
- `DELETE /api/v1/friends/{id}` - Remove friend

### Analytics
- `GET /api/v1/analytics/spending` - Get spending analytics
- `GET /api/v1/analytics/categories` - Category breakdown

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── endpoints/       # API endpoints
│   │   │   │   ├── auth.py
│   │   │   │   ├── users.py
│   │   │   │   ├── groups.py
│   │   │   │   ├── expenses.py
│   │   │   │   ├── payments.py
│   │   │   │   ├── balances.py
│   │   │   │   ├── notifications.py
│   │   │   │   ├── social.py
│   │   │   │   ├── disputes.py
│   │   │   │   ├── friends.py
│   │   │   │   └── analytics.py
│   │   │   ├── deps.py          # Dependencies
│   │   │   └── router.py        # API router
│   │   ├── core/
│   │   │   ├── config.py        # Settings
│   │   │   └── security.py      # JWT/Password
│   │   ├── db/
│   │   │   └── database.py      # Database setup
│   │   ├── models/              # SQLAlchemy models
│   │   ├── schemas/             # Pydantic schemas
│   │   └── main.py              # FastAPI app
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── components/          # React components
│   │   ├── pages/               # Page components
│   │   ├── services/            # API services
│   │   ├── store/               # Zustand stores
│   │   ├── types/               # TypeScript types
│   │   └── lib/                 # Utilities
│   ├── Dockerfile
│   ├── nginx.conf
│   └── package.json
│
├── docs/                        # PRD documentation
├── docker-compose.yml
└── README.md
```

## Development

### Running Tests
```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run lint
```

### Building for Production
```bash
# Using Docker
docker-compose up -d --build

# Or manually
cd frontend && npm run build
cd backend && uvicorn app.main:app
```

## License

MIT
