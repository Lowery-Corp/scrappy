from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from models.user import User
from schemas.user import UserCreate, DeleteUser
from auth.dependencies import get_current_active_user
from repositories.user import (
    create_user,
    check_user_exists,
    deactivate_user,
    delete_user,
    get_user_by_email,
    make_user_admin,
)
from db.dependencies import get_session
from core.security import hash_password

router = APIRouter(tags=["users"])

@router.get("/me")
async def read_me_route(
    current_user: User = Depends(get_current_active_user),
) -> dict[str, str | bool | int]:
    return {
        "id": current_user.id,
        "email": current_user.email,
        "is_active": current_user.is_active,
        "is_admin": current_user.is_admin,
    }


@router.post("/create")
async def create_new_user_route(
    new_user: UserCreate,
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:

    if await check_user_exists(session, new_user.email):
        return {"message": "User with this email already exists"}

    new_user.password = hash_password(new_user.password)
    assert new_user.password, "Password hashing failed, got empty string"

    newly_created_user = await create_user(
        session,
        email=new_user.email,
        hashed_password=new_user.password,
    )

    return {"message": f"User {newly_created_user.email} created successfully"}


@router.delete("/delete")
async def delete_user_route(
    subject_user: DeleteUser,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    if current_user.is_admin:
        subject_user_profile = await get_user_by_email(session, subject_user.email)
        if subject_user_profile is not None:
            await delete_user(session, subject_user_profile)
            return {"message": f"User {subject_user.email} has been deleted"}
    else:
        return {"message": "User with this email does not exist"}
    raise HTTPException(status_code=403, detail="Only admins can delete other users")


@router.post("/deactivate")
async def deactivate_user_route(
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    deactivated_user = await deactivate_user(session, current_user)
    return {"message": f"User {deactivated_user.email} is being deleted..."}


@router.post("/make-admin")
async def make_admin_route(
    subject_user: DeleteUser,
    current_user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_session),
) -> dict[str, str]:
    if current_user.is_admin:
        subject_user_profile = await get_user_by_email(session, subject_user.email)
        if subject_user_profile is not None:
            updated_user = await make_user_admin(session, subject_user_profile)
            return {"message": f"User {updated_user.email} is now an admin"}
        elif subject_user_profile is None:
            return {"message": "User with this email does not exist"}
    raise HTTPException(status_code=403, detail="Only admins can make other users admins")
