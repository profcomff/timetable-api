"""Personal calendar routes"""

import logging
from datetime import date, timedelta

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import FileResponse
from fastapi_sqlalchemy import db
from sqlalchemy.orm import joinedload

from calendar_backend.methods import list_calendar
from calendar_backend.models import Event, Group, Lecturer, Room, SubscriptionType, UserCalendarSubscription
from calendar_backend.routes.models import PersonalEventGet, PersonalEventPost, UserCalendarGet

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/user", tags=["Personal Calendar"])


def get_user_id_from_auth(auth_result: dict | None) -> int:
    """Extract user ID from auth result - placeholder implementation"""
    # TODO: Implement proper user ID extraction from auth system
    # For now, return a placeholder user ID
    if auth_result and isinstance(auth_result, dict):
        return auth_result.get('user_id', 1)
    return 1  # Default user ID for testing


@router.post("/events", response_model=PersonalEventGet, status_code=status.HTTP_201_CREATED)
async def create_personal_event(
    event: PersonalEventPost,
    auth_result = Depends(UnionAuth(scopes=["timetable.calendar.personal.create"])),
) -> PersonalEventGet:
    """Create a personal event"""
    user_id = get_user_id_from_auth(auth_result)
    new_event = Event.create(
        name=event.name,
        start_ts=event.start_ts,
        end_ts=event.end_ts,
        creator_user_id=user_id,
        is_personal=True,
        session=db.session,
    )
    db.session.commit()
    return PersonalEventGet.model_validate(new_event)


@router.get("/events", response_model=list[PersonalEventGet])
async def get_personal_events(
    start: date | None = Query(default=None, description="Start date filter"),
    end: date | None = Query(default=None, description="End date filter"),
    auth_result = Depends(UnionAuth(scopes=["timetable.calendar.personal.read"])),
) -> list[PersonalEventGet]:
    """Get user's personal events"""
    user_id = get_user_id_from_auth(auth_result)
    query = db.session.query(Event).filter(
        Event.creator_user_id == user_id,
        Event.is_personal == True,
        Event.is_deleted == False,
    )

    if start:
        query = query.filter(Event.start_ts >= start)
    if end:
        query = query.filter(Event.end_ts <= end)

    events = query.order_by(Event.start_ts).all()
    return [PersonalEventGet.model_validate(event) for event in events]


@router.get("/calendar", response_model=UserCalendarGet)
async def get_user_calendar(
    start: date | None = Query(default=None, description="Start date filter"),
    end: date | None = Query(default=None, description="End date filter"),
    include_subscribed: bool = Query(default=True, description="Include subscribed calendars"),
    auth_result = Depends(UnionAuth(scopes=["timetable.calendar.personal.read"])),
) -> UserCalendarGet:
    """Get user's complete calendar including personal events and subscriptions"""
    user_id = get_user_id_from_auth(auth_result)
    start = start or date.today()
    end = end or date.today() + timedelta(days=30)

    # Get personal events
    personal_events = (
        db.session.query(Event)
        .filter(
            Event.creator_user_id == user_id,
            Event.is_personal == True,
            Event.is_deleted == False,
            Event.start_ts >= start,
            Event.end_ts <= end,
        )
        .order_by(Event.start_ts)
        .all()
    )

    subscribed_events = []
    if include_subscribed:
        # Get user's subscriptions
        subscriptions = (
            db.session.query(UserCalendarSubscription)
            .filter(
                UserCalendarSubscription.user_id == user_id,
                UserCalendarSubscription.is_active == True,
            )
            .all()
        )

        # Get events from subscriptions
        for subscription in subscriptions:
            if subscription.subscription_type == SubscriptionType.GROUP:
                events = (
                    db.session.query(Event)
                    .options(joinedload(Event.group), joinedload(Event.lecturer), joinedload(Event.room))
                    .filter(
                        Event.group.any(Group.id == subscription.target_id),
                        Event.is_deleted == False,
                        Event.start_ts >= start,
                        Event.end_ts <= end,
                    )
                    .all()
                )
                subscribed_events.extend([
                    {
                        "id": event.id,
                        "name": event.name,
                        "start_ts": event.start_ts,
                        "end_ts": event.end_ts,
                        "source_type": "group",
                        "source_id": subscription.target_id,
                        "groups": [{"id": g.id, "name": g.name, "number": g.number} for g in event.group],
                        "lecturers": [{"id": l.id, "first_name": l.first_name, "last_name": l.last_name} for l in event.lecturer],
                        "rooms": [{"id": r.id, "name": r.name} for r in event.room],
                    }
                    for event in events
                ])
            elif subscription.subscription_type == SubscriptionType.LECTURER:
                events = (
                    db.session.query(Event)
                    .options(joinedload(Event.group), joinedload(Event.lecturer), joinedload(Event.room))
                    .filter(
                        Event.lecturer.any(Lecturer.id == subscription.target_id),
                        Event.is_deleted == False,
                        Event.start_ts >= start,
                        Event.end_ts <= end,
                    )
                    .all()
                )
                subscribed_events.extend([
                    {
                        "id": event.id,
                        "name": event.name,
                        "start_ts": event.start_ts,
                        "end_ts": event.end_ts,
                        "source_type": "lecturer",
                        "source_id": subscription.target_id,
                        "groups": [{"id": g.id, "name": g.name, "number": g.number} for g in event.group],
                        "lecturers": [{"id": l.id, "first_name": l.first_name, "last_name": l.last_name} for l in event.lecturer],
                        "rooms": [{"id": r.id, "name": r.name} for r in event.room],
                    }
                    for event in events
                ])
            elif subscription.subscription_type == SubscriptionType.ROOM:
                events = (
                    db.session.query(Event)
                    .options(joinedload(Event.group), joinedload(Event.lecturer), joinedload(Event.room))
                    .filter(
                        Event.room.any(Room.id == subscription.target_id),
                        Event.is_deleted == False,
                        Event.start_ts >= start,
                        Event.end_ts <= end,
                    )
                    .all()
                )
                subscribed_events.extend([
                    {
                        "id": event.id,
                        "name": event.name,
                        "start_ts": event.start_ts,
                        "end_ts": event.end_ts,
                        "source_type": "room",
                        "source_id": subscription.target_id,
                        "groups": [{"id": g.id, "name": g.name, "number": g.number} for g in event.group],
                        "lecturers": [{"id": l.id, "first_name": l.first_name, "last_name": l.last_name} for l in event.lecturer],
                        "rooms": [{"id": r.id, "name": r.name} for r in event.room],
                    }
                    for event in events
                ])

    return UserCalendarGet(
        user_id=user_id,
        events=[PersonalEventGet.model_validate(event) for event in personal_events],
        subscribed_events=subscribed_events,
    )


@router.get("/calendar.ics")
async def export_user_calendar_ics(
    start: date | None = Query(default=None, description="Start date filter"),
    end: date | None = Query(default=None, description="End date filter"),
    include_subscribed: bool = Query(default=True, description="Include subscribed calendars"),
    auth_result = Depends(UnionAuth(scopes=["timetable.calendar.personal.read"])),
) -> FileResponse:
    """Export user's calendar as iCal file"""
    from calendar_backend.methods.personal_calendar import create_personal_calendar_ical, create_personal_calendar_file
    
    user_id = get_user_id_from_auth(auth_result)
    start = start or date.today()
    end = end or date.today() + timedelta(days=365)

    try:
        # Generate personal calendar
        calendar_data = await create_personal_calendar_ical(
            user_id=user_id,
            session=db.session, 
            start_date=start,
            end_date=end,
            include_subscriptions=include_subscribed
        )
        
        # Create file and return
        filepath = await create_personal_calendar_file(user_id, calendar_data)
        return FileResponse(
            filepath, 
            media_type='text/calendar',
            filename=f'personal_calendar_user_{user_id}.ics'
        )
    except Exception as e:
        logger.error(f"Failed to export personal calendar for user {user_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate personal calendar")


@router.delete("/events/{event_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_personal_event(
    event_id: int,
    auth_result = Depends(UnionAuth(scopes=["timetable.calendar.personal.delete"])),
) -> None:
    """Delete a personal event"""
    user_id = get_user_id_from_auth(auth_result)
    event = Event.get(event_id, session=db.session)
    if not event or event.creator_user_id != user_id or not event.is_personal:
        raise HTTPException(status_code=404, detail="Personal event not found")

    event.is_deleted = True
    db.session.commit()