"""Calendar subscription routes"""

import logging

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_sqlalchemy import db

from calendar_backend.models import Group, Lecturer, Room, SubscriptionType, UserCalendarSubscription
from calendar_backend.routes.models import SubscriptionGet, SubscriptionPost, UserSubscriptionsGet

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/subscriptions", tags=["Calendar Subscriptions"])


def get_user_id_from_auth(auth_result: dict | None) -> int:
    """Extract user ID from auth result - placeholder implementation"""
    # TODO: Implement proper user ID extraction from auth system
    # For now, return a placeholder user ID
    if auth_result and isinstance(auth_result, dict):
        return auth_result.get('user_id', 1)
    return 1  # Default user ID for testing


@router.post("/", response_model=SubscriptionGet, status_code=status.HTTP_201_CREATED)
async def create_subscription(
    subscription: SubscriptionPost,
    auth_result = Depends(UnionAuth(scopes=["timetable.subscription.create"])),
) -> SubscriptionGet:
    """Create a calendar subscription"""
    user_id = get_user_id_from_auth(auth_result)
    # Validate target exists
    sub_type = SubscriptionType(subscription.subscription_type)
    if sub_type == SubscriptionType.GROUP:
        target = Group.get(subscription.target_id, session=db.session)
    elif sub_type == SubscriptionType.LECTURER:
        target = Lecturer.get(subscription.target_id, session=db.session)
    elif sub_type == SubscriptionType.ROOM:
        target = Room.get(subscription.target_id, session=db.session)
    else:
        raise HTTPException(status_code=400, detail="Invalid subscription type")

    if not target or target.is_deleted:
        raise HTTPException(status_code=404, detail=f"{subscription.subscription_type.title()} not found")

    # Check if subscription already exists
    existing_subscription = (
        db.session.query(UserCalendarSubscription)
        .filter(
            UserCalendarSubscription.user_id == user_id,
            UserCalendarSubscription.subscription_type == sub_type,
            UserCalendarSubscription.target_id == subscription.target_id,
        )
        .first()
    )

    if existing_subscription:
        if existing_subscription.is_active:
            raise HTTPException(status_code=409, detail="Subscription already exists")
        else:
            # Reactivate existing subscription
            existing_subscription.is_active = True
            db.session.commit()
            return SubscriptionGet.model_validate(existing_subscription)

    # Create new subscription
    new_subscription = UserCalendarSubscription.create(
        user_id=user_id,
        subscription_type=sub_type,
        target_id=subscription.target_id,
        session=db.session,
    )
    db.session.commit()
    return SubscriptionGet.model_validate(new_subscription)


@router.delete("/{subscription_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_subscription(
    subscription_id: int,
    auth_result = Depends(UnionAuth(scopes=["timetable.subscription.delete"])),
) -> None:
    """Delete a calendar subscription"""
    user_id = get_user_id_from_auth(auth_result)
    subscription = UserCalendarSubscription.get(subscription_id, session=db.session)
    if not subscription or subscription.user_id != user_id:
        raise HTTPException(status_code=404, detail="Subscription not found")

    subscription.is_active = False
    db.session.commit()


@router.get("/", response_model=UserSubscriptionsGet)
async def get_user_subscriptions(
    auth_result = Depends(UnionAuth(scopes=["timetable.subscription.read"])),
) -> UserSubscriptionsGet:
    """Get current user's calendar subscriptions"""
    user_id = get_user_id_from_auth(auth_result)
    subscriptions = (
        db.session.query(UserCalendarSubscription)
        .filter(
            UserCalendarSubscription.user_id == user_id,
            UserCalendarSubscription.is_active == True,
        )
        .all()
    )

    return UserSubscriptionsGet(
        user_id=user_id,
        subscriptions=[SubscriptionGet.model_validate(sub) for sub in subscriptions]
    )


@router.get("/{subscription_id}", response_model=SubscriptionGet)
async def get_subscription(
    subscription_id: int,
    auth_result = Depends(UnionAuth(scopes=["timetable.subscription.read"])),
) -> SubscriptionGet:
    """Get a specific subscription"""
    user_id = get_user_id_from_auth(auth_result)
    subscription = UserCalendarSubscription.get(subscription_id, session=db.session)
    if not subscription or subscription.user_id != user_id:
        raise HTTPException(status_code=404, detail="Subscription not found")

    return SubscriptionGet.model_validate(subscription)


# Convenience endpoints for creating specific subscription types
@router.post("/group/{group_id}", response_model=SubscriptionGet, status_code=status.HTTP_201_CREATED)
async def subscribe_to_group(
    group_id: int,
    auth_result = Depends(UnionAuth(scopes=["timetable.subscription.create"])),
) -> SubscriptionGet:
    """Subscribe to a group's calendar"""
    subscription_data = SubscriptionPost(subscription_type="group", target_id=group_id)
    return await create_subscription(subscription_data, auth_result)


@router.post("/lecturer/{lecturer_id}", response_model=SubscriptionGet, status_code=status.HTTP_201_CREATED)
async def subscribe_to_lecturer(
    lecturer_id: int,
    auth_result = Depends(UnionAuth(scopes=["timetable.subscription.create"])),
) -> SubscriptionGet:
    """Subscribe to a lecturer's calendar"""
    subscription_data = SubscriptionPost(subscription_type="lecturer", target_id=lecturer_id)
    return await create_subscription(subscription_data, auth_result)


@router.post("/room/{room_id}", response_model=SubscriptionGet, status_code=status.HTTP_201_CREATED)
async def subscribe_to_room(
    room_id: int,
    auth_result = Depends(UnionAuth(scopes=["timetable.subscription.create"])),
) -> SubscriptionGet:
    """Subscribe to a room's calendar"""
    subscription_data = SubscriptionPost(subscription_type="room", target_id=room_id)
    return await create_subscription(subscription_data, auth_result)