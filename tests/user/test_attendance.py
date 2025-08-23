"""Tests for attendance functionality"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from calendar_backend.models import AttendanceStatus, Event, Group, Lecturer, Room, UserEventAttendance


def test_mark_attendance_unauthorized(client: TestClient):
    """Test marking attendance without authentication"""
    response = client.post("/event/1/attendance/", json={"status": "attending"})
    assert response.status_code == 401


def test_mark_attendance_event_not_found(client_auth: TestClient):
    """Test marking attendance for non-existent event"""
    response = client_auth.post("/event/999999/attendance/", json={"status": "attending"})
    assert response.status_code == 404
    assert "Event not found" in response.json()["detail"]


def test_mark_attendance_success(client_auth: TestClient, dbsession: Session):
    """Test successfully marking attendance"""
    # Create test data
    room = Room(name="Test Room", direction="North")
    lecturer = Lecturer(first_name="Test", middle_name="Test", last_name="Lecturer")
    group = Group(name="Test Group", number="TEST001")
    dbsession.add_all([room, lecturer, group])
    dbsession.commit()

    event = Event(
        name="Test Event",
        start_ts="2024-08-23T10:00:00",
        end_ts="2024-08-23T11:00:00",
        room=[room],
        lecturer=[lecturer],
        group=[group],
    )
    dbsession.add(event)
    dbsession.commit()

    # Mark attendance
    response = client_auth.post(f"/event/{event.id}/attendance/", json={"status": "attending"})
    assert response.status_code == 201
    data = response.json()
    assert data["status"] == "attending"
    assert data["event_id"] == event.id
    assert data["user_id"] == 1  # Default test user ID

    # Verify in database
    attendance = dbsession.query(UserEventAttendance).filter(
        UserEventAttendance.event_id == event.id,
        UserEventAttendance.user_id == 1
    ).first()
    assert attendance is not None
    assert attendance.status == AttendanceStatus.ATTENDING

    # Clean up
    dbsession.delete(attendance)
    dbsession.delete(event)
    dbsession.delete(room)
    dbsession.delete(lecturer)
    dbsession.delete(group)
    dbsession.commit()


def test_update_attendance(client_auth: TestClient, dbsession: Session):
    """Test updating existing attendance"""
    # Create test data
    room = Room(name="Test Room 2", direction="North")
    lecturer = Lecturer(first_name="Test", middle_name="Test", last_name="Lecturer")
    group = Group(name="Test Group", number="TEST002")
    dbsession.add_all([room, lecturer, group])
    dbsession.commit()

    event = Event(
        name="Test Event 2",
        start_ts="2024-08-23T10:00:00",
        end_ts="2024-08-23T11:00:00",
        room=[room],
        lecturer=[lecturer],
        group=[group],
    )
    dbsession.add(event)
    dbsession.commit()

    # First mark attendance
    response1 = client_auth.post(f"/event/{event.id}/attendance/", json={"status": "attending"})
    assert response1.status_code == 201

    # Update attendance
    response2 = client_auth.post(f"/event/{event.id}/attendance/", json={"status": "not_attending"})
    assert response2.status_code == 201
    data = response2.json()
    assert data["status"] == "not_attending"

    # Verify only one record exists in database
    attendances = dbsession.query(UserEventAttendance).filter(
        UserEventAttendance.event_id == event.id,
        UserEventAttendance.user_id == 1
    ).all()
    assert len(attendances) == 1
    assert attendances[0].status == AttendanceStatus.NOT_ATTENDING

    # Clean up
    dbsession.query(UserEventAttendance).filter(UserEventAttendance.event_id == event.id).delete()
    dbsession.delete(event)
    dbsession.delete(room)
    dbsession.delete(lecturer)
    dbsession.delete(group)
    dbsession.commit()


def test_get_my_attendance(client_auth: TestClient, dbsession: Session):
    """Test getting user's attendance for an event"""
    # Create test data
    room = Room(name="Test Room 3", direction="North")
    lecturer = Lecturer(first_name="Test", middle_name="Test", last_name="Lecturer")
    group = Group(name="Test Group", number="TEST003")
    dbsession.add_all([room, lecturer, group])
    dbsession.commit()

    event = Event(
        name="Test Event 3",
        start_ts="2024-08-23T10:00:00",
        end_ts="2024-08-23T11:00:00",
        room=[room],
        lecturer=[lecturer],
        group=[group],
    )
    dbsession.add(event)
    dbsession.commit()

    # Check attendance when none exists
    response1 = client_auth.get(f"/event/{event.id}/attendance/me")
    assert response1.status_code == 200
    assert response1.json() is None

    # Mark attendance
    client_auth.post(f"/event/{event.id}/attendance/", json={"status": "maybe"})

    # Check attendance after marking
    response2 = client_auth.get(f"/event/{event.id}/attendance/me")
    assert response2.status_code == 200
    data = response2.json()
    assert data["status"] == "maybe"
    assert data["event_id"] == event.id

    # Clean up
    dbsession.query(UserEventAttendance).filter(UserEventAttendance.event_id == event.id).delete()
    dbsession.delete(event)
    dbsession.delete(room)
    dbsession.delete(lecturer)
    dbsession.delete(group)
    dbsession.commit()


def test_remove_attendance(client_auth: TestClient, dbsession: Session):
    """Test removing attendance"""
    # Create test data
    room = Room(name="Test Room 4", direction="North")
    lecturer = Lecturer(first_name="Test", middle_name="Test", last_name="Lecturer")
    group = Group(name="Test Group", number="TEST004")
    dbsession.add_all([room, lecturer, group])
    dbsession.commit()

    event = Event(
        name="Test Event 4",
        start_ts="2024-08-23T10:00:00",
        end_ts="2024-08-23T11:00:00",
        room=[room],
        lecturer=[lecturer],
        group=[group],
    )
    dbsession.add(event)
    dbsession.commit()

    # Mark attendance first
    client_auth.post(f"/event/{event.id}/attendance/", json={"status": "attending"})

    # Remove attendance
    response = client_auth.delete(f"/event/{event.id}/attendance/")
    assert response.status_code == 204

    # Verify removed from database
    attendance = dbsession.query(UserEventAttendance).filter(
        UserEventAttendance.event_id == event.id,
        UserEventAttendance.user_id == 1
    ).first()
    assert attendance is None

    # Clean up
    dbsession.delete(event)
    dbsession.delete(room)
    dbsession.delete(lecturer)
    dbsession.delete(group)
    dbsession.commit()