"""User attendance routes"""

import logging

from auth_lib.fastapi import UnionAuth
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi_sqlalchemy import db

from calendar_backend.models import AttendanceStatus, Event, UserEventAttendance
from calendar_backend.routes.models import AttendanceGet, AttendanceListGet, AttendancePost

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/event/{event_id}/attendance", tags=["Event Attendance"])


def get_user_id_from_auth(auth_result: dict | None) -> int:
    """Extract user ID from auth result - placeholder implementation"""
    # TODO: Implement proper user ID extraction from auth system
    # For now, return a placeholder user ID
    if auth_result and isinstance(auth_result, dict):
        return auth_result.get('user_id', 1)
    return 1  # Default user ID for testing


@router.post("/", response_model=AttendanceGet, status_code=status.HTTP_201_CREATED)
async def mark_attendance(
    event_id: int,
    attendance: AttendancePost,
    request: Request,
    auth_result = Depends(UnionAuth(scopes=["timetable.event.attend"])),
) -> AttendanceGet:
    """Mark user attendance for an event"""
    user_id = get_user_id_from_auth(auth_result)
    
    # Check if event exists
    event = Event.get(event_id, session=db.session)
    if not event or event.is_deleted:
        raise HTTPException(status_code=404, detail="Event not found")

    # Check if attendance already exists
    existing_attendance = (
        db.session.query(UserEventAttendance)
        .filter(UserEventAttendance.user_id == user_id, UserEventAttendance.event_id == event_id)
        .first()
    )

    if existing_attendance:
        # Update existing attendance
        existing_attendance.status = AttendanceStatus(attendance.status)
        db.session.commit()
        return AttendanceGet.model_validate(existing_attendance)
    else:
        # Create new attendance
        new_attendance = UserEventAttendance.create(
            user_id=user_id,
            event_id=event_id,
            status=AttendanceStatus(attendance.status),
            session=db.session,
        )
        db.session.commit()
        return AttendanceGet.model_validate(new_attendance)


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def remove_attendance(
    event_id: int,
    auth_result = Depends(UnionAuth(scopes=["timetable.event.attend"])),
) -> None:
    """Remove user attendance for an event"""
    user_id = get_user_id_from_auth(auth_result)
    
    # Check if event exists
    event = Event.get(event_id, session=db.session)
    if not event or event.is_deleted:
        raise HTTPException(status_code=404, detail="Event not found")

    # Find and delete attendance
    attendance = (
        db.session.query(UserEventAttendance)
        .filter(UserEventAttendance.user_id == user_id, UserEventAttendance.event_id == event_id)
        .first()
    )

    if attendance:
        db.session.delete(attendance)
        db.session.commit()


@router.get("/list", response_model=AttendanceListGet)
async def get_event_attendees(
    event_id: int,
    auth_result = Depends(UnionAuth(scopes=["timetable.event.read"])),
) -> AttendanceListGet:
    """Get list of attendees for an event"""
    # Check if event exists
    event = Event.get(event_id, session=db.session)
    if not event or event.is_deleted:
        raise HTTPException(status_code=404, detail="Event not found")

    # Get all attendances for this event
    attendances = (
        db.session.query(UserEventAttendance)
        .filter(UserEventAttendance.event_id == event_id)
        .all()
    )

    return AttendanceListGet(
        event_id=event_id,
        total_attendees=len([a for a in attendances if a.status == AttendanceStatus.ATTENDING]),
        attendances=[AttendanceGet.model_validate(a) for a in attendances]
    )


@router.get("/me", response_model=AttendanceGet | None)
async def get_my_attendance(
    event_id: int,
    auth_result = Depends(UnionAuth(scopes=["timetable.event.read"])),
) -> AttendanceGet | None:
    """Get current user's attendance for an event"""
    user_id = get_user_id_from_auth(auth_result)
    
    # Check if event exists
    event = Event.get(event_id, session=db.session)
    if not event or event.is_deleted:
        raise HTTPException(status_code=404, detail="Event not found")

    # Get user's attendance
    attendance = (
        db.session.query(UserEventAttendance)
        .filter(UserEventAttendance.user_id == user_id, UserEventAttendance.event_id == event_id)
        .first()
    )

    if attendance:
        return AttendanceGet.model_validate(attendance)
    else:
        return None