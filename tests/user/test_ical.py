"""Tests for iCal import/export functionality"""

import pytest
import tempfile
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from io import BytesIO

from calendar_backend.models import Event, UserCalendarSubscription, Group, Lecturer, Room


def create_test_ical_content() -> str:
    """Create a test iCal file content"""
    return """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Test Calendar//EN
CALSCALE:GREGORIAN
METHOD:PUBLISH
X-WR-CALNAME:Test Calendar
X-WR-CALDESC:Test calendar for import testing
BEGIN:VEVENT
UID:test-event-1@example.com
DTSTART:20240825T100000Z
DTEND:20240825T110000Z
DTSTAMP:20240820T120000Z
SUMMARY:Test Meeting 1
DESCRIPTION:This is a test meeting
END:VEVENT
BEGIN:VEVENT
UID:test-event-2@example.com
DTSTART:20240825T140000Z
DTEND:20240825T150000Z
DTSTAMP:20240820T120000Z
SUMMARY:Test Meeting 2
DESCRIPTION:Another test meeting
END:VEVENT
BEGIN:VEVENT
UID:invalid-event@example.com
DTSTART:20240825T160000Z
SUMMARY:Invalid Event - No End Time
END:VEVENT
END:VCALENDAR"""


def create_invalid_ical_content() -> str:
    """Create an invalid iCal file content"""
    return """BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//Test//Invalid Calendar//EN
BEGIN:VEVENT
SUMMARY:Event without proper structure
END:VEVENT
# Missing END:VCALENDAR"""


def test_ical_preview_success(client_auth: TestClient):
    """Test successful iCal preview"""
    ical_content = create_test_ical_content()
    
    # Create a temporary file-like object
    file_data = ical_content.encode('utf-8')
    
    response = client_auth.post(
        "/import/ical/preview",
        files={"file": ("test_calendar.ics", BytesIO(file_data), "text/calendar")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert len(data["errors"]) == 0
    assert data["preview"]["total_events"] == 3  # Including the invalid one
    assert len(data["preview"]["preview_events"]) <= 5  # Max preview limit
    assert data["preview"]["calendar_name"] == "Test Calendar"


def test_ical_preview_invalid_file(client_auth: TestClient):
    """Test iCal preview with invalid file"""
    invalid_content = create_invalid_ical_content()
    file_data = invalid_content.encode('utf-8')
    
    response = client_auth.post(
        "/import/ical/preview",
        files={"file": ("invalid_calendar.ics", BytesIO(file_data), "text/calendar")}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is False
    assert len(data["errors"]) > 0


def test_ical_import_success(client_auth: TestClient, dbsession: Session):
    """Test successful iCal import with detailed results"""
    ical_content = create_test_ical_content()
    file_data = ical_content.encode('utf-8')
    
    response = client_auth.post(
        "/import/ical",
        files={"file": ("test_calendar.ics", BytesIO(file_data), "text/calendar")}
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Check detailed results
    assert data["success"] is True
    assert data["events_created"] == 2  # Two valid events
    assert data["events_skipped"] == 1  # One invalid event
    assert data["total_processed"] == 3
    assert len(data["created_events"]) == 2
    assert len(data["skipped_events"]) == 1
    
    # Check that events were created in database
    events = dbsession.query(Event).filter(
        Event.creator_user_id == 1,
        Event.is_personal == True
    ).all()
    
    assert len([e for e in events if not e.is_deleted]) == 2
    
    # Clean up
    for event in events:
        dbsession.delete(event)
    dbsession.commit()


def test_ical_import_wrong_file_type(client_auth: TestClient):
    """Test iCal import with wrong file extension"""
    response = client_auth.post(
        "/import/ical",
        files={"file": ("test.txt", BytesIO(b"not an ical file"), "text/plain")}
    )
    
    assert response.status_code == 400
    assert "must be an iCal file" in response.json()["detail"]


def test_ical_import_admin_success(client_auth: TestClient, dbsession: Session):
    """Test successful admin iCal import"""
    ical_content = create_test_ical_content()
    file_data = ical_content.encode('utf-8')
    
    response = client_auth.post(
        "/import/ical/admin",
        files={"file": ("admin_calendar.ics", BytesIO(file_data), "text/calendar")}
    )
    
    assert response.status_code == 201
    data = response.json()
    
    # Check results
    assert data["success"] is True
    assert data["events_created"] == 2
    
    # Check that events were created as institutional (not personal)
    events = dbsession.query(Event).filter(
        Event.creator_user_id.is_(None),
        Event.is_personal == False
    ).all()
    
    institutional_events = [e for e in events if not e.is_deleted and e.name.startswith("Test Meeting")]
    assert len(institutional_events) >= 2
    
    # Clean up
    for event in institutional_events:
        dbsession.delete(event)
    dbsession.commit()


def test_personal_calendar_ics_export(client_auth: TestClient, dbsession: Session):
    """Test personal calendar iCal export"""
    # Create a personal event first
    personal_event = Event(
        name="My Personal Event",
        start_ts="2024-08-25T10:00:00",
        end_ts="2024-08-25T11:00:00",
        creator_user_id=1,
        is_personal=True,
    )
    dbsession.add(personal_event)
    dbsession.commit()
    
    # Export calendar
    response = client_auth.get("/user/calendar.ics")
    
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/calendar"
    
    # Check that the file contains our event
    content = response.content.decode('utf-8')
    assert "My Personal Event" in content
    assert "BEGIN:VCALENDAR" in content
    assert "END:VCALENDAR" in content
    
    # Clean up
    dbsession.delete(personal_event)
    dbsession.commit()


def test_personal_calendar_with_subscriptions_export(client_auth: TestClient, dbsession: Session):
    """Test personal calendar export including subscription events"""
    # Create test data
    group = Group(name="Test Group", number="TEST123")
    lecturer = Lecturer(first_name="Test", middle_name="T", last_name="Lecturer")
    room = Room(name="Test Room", direction="North")
    dbsession.add_all([group, lecturer, room])
    dbsession.commit()
    
    # Create a group event
    group_event = Event(
        name="Group Lecture",
        start_ts="2024-08-25T14:00:00",
        end_ts="2024-08-25T15:00:00",
        group=[group],
        lecturer=[lecturer],
        room=[room],
    )
    dbsession.add(group_event)
    dbsession.commit()
    
    # Create a subscription
    subscription = UserCalendarSubscription(
        user_id=1,
        subscription_type="group",
        target_id=group.id,
        is_active=True,
    )
    dbsession.add(subscription)
    dbsession.commit()
    
    # Export calendar with subscriptions
    response = client_auth.get("/user/calendar.ics?include_subscribed=true")
    
    assert response.status_code == 200
    content = response.content.decode('utf-8')
    assert "Group Lecture" in content
    assert "BEGIN:VCALENDAR" in content
    
    # Clean up
    dbsession.delete(subscription)
    dbsession.delete(group_event)
    dbsession.delete(room)
    dbsession.delete(lecturer)
    dbsession.delete(group)
    dbsession.commit()