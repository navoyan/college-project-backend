from contextlib import asynccontextmanager

from src import mongo
from src.config import settings
from src.users import service as users_service
from src.users.schemas import UserDetails, UserRole


@asynccontextmanager
async def lifespan(_):
    print("Init setups")

    if not await mongo.users_collection.find_one({"email": settings.root_user_email}):
        root_user_details = UserDetails(
            email=settings.root_user_email,
            full_name=settings.root_user_full_name,
            password=settings.root_user_password,
        )

        await users_service.create_user_using_details(root_user_details, role=UserRole.admin)

    yield
