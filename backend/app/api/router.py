from fastapi import APIRouter

from app.api.endpoints import auth, users, groups, expenses, payments, balances, notifications, social, disputes, friends

api_router = APIRouter()

api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(groups.router)
api_router.include_router(expenses.router)
api_router.include_router(payments.router)
api_router.include_router(balances.router)
api_router.include_router(notifications.router)
api_router.include_router(social.router)
api_router.include_router(disputes.router)
api_router.include_router(friends.router)
