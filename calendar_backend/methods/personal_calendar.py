"""Enhanced iCal functionality for personal calendars"""

import logging
from datetime import date, datetime
from typing import List

import pytz
from icalendar import Calendar, Event as ICalEvent, vText
from sqlalchemy.orm import Session

from calendar_backend.models import Event, UserCalendarSubscription, SubscriptionType, Group, Lecturer, Room

logger = logging.getLogger(__name__)


async def create_personal_calendar_ical(
    user_id: int, 
    session: Session, 
    start_date: date | None = None, 
    end_date: date | None = None,
    include_subscriptions: bool = True
) -> Calendar:
    """Create an iCal calendar for a user's personal events and subscriptions"""
    
    calendar = Calendar()
    calendar.add('prodid', f'-//Profcomff Timetable API//Personal Calendar {user_id}//EN')
    calendar.add('version', '2.0')
    calendar.add('calscale', 'GREGORIAN')
    calendar.add('method', 'PUBLISH')
    calendar.add('x-wr-calname', f'Personal Calendar - User {user_id}')
    calendar.add('x-wr-caldesc', 'Personal calendar with events and subscriptions')

    # Get personal events
    personal_events_query = session.query(Event).filter(
        Event.creator_user_id == user_id,
        Event.is_personal == True,
        Event.is_deleted == False
    )
    
    if start_date:
        personal_events_query = personal_events_query.filter(Event.start_ts >= start_date)
    if end_date:
        personal_events_query = personal_events_query.filter(Event.end_ts <= end_date)
    
    personal_events = personal_events_query.all()
    
    # Add personal events to calendar
    for event in personal_events:
        ical_event = ICalEvent()
        ical_event.add('uid', f'personal-{event.id}@profcomff.com')
        ical_event.add('summary', event.name)
        ical_event.add('dtstart', event.start_ts.replace(tzinfo=pytz.UTC))
        ical_event.add('dtend', event.end_ts.replace(tzinfo=pytz.UTC))
        ical_event.add('dtstamp', event.create_ts.replace(tzinfo=pytz.UTC))
        ical_event.add('description', 'Personal event')
        ical_event.add('categories', 'Personal')
        calendar.add_component(ical_event)
    
    # Include subscription events if requested
    if include_subscriptions:
        subscriptions = session.query(UserCalendarSubscription).filter(
            UserCalendarSubscription.user_id == user_id,
            UserCalendarSubscription.is_active == True
        ).all()
        
        for subscription in subscriptions:
            events = []
            
            if subscription.subscription_type == SubscriptionType.GROUP:
                events_query = session.query(Event).filter(
                    Event.group.any(Group.id == subscription.target_id),
                    Event.is_deleted == False
                )
                if start_date:
                    events_query = events_query.filter(Event.start_ts >= start_date)
                if end_date:
                    events_query = events_query.filter(Event.end_ts <= end_date)
                events = events_query.all()
                
            elif subscription.subscription_type == SubscriptionType.LECTURER:
                events_query = session.query(Event).filter(
                    Event.lecturer.any(Lecturer.id == subscription.target_id),
                    Event.is_deleted == False
                )
                if start_date:
                    events_query = events_query.filter(Event.start_ts >= start_date)
                if end_date:
                    events_query = events_query.filter(Event.end_ts <= end_date)
                events = events_query.all()
                
            elif subscription.subscription_type == SubscriptionType.ROOM:
                events_query = session.query(Event).filter(
                    Event.room.any(Room.id == subscription.target_id),
                    Event.is_deleted == False
                )
                if start_date:
                    events_query = events_query.filter(Event.start_ts >= start_date)
                if end_date:
                    events_query = events_query.filter(Event.end_ts <= end_date)
                events = events_query.all()
            
            # Add subscription events to calendar
            for event in events:
                ical_event = ICalEvent()
                ical_event.add('uid', f'subscription-{event.id}-{subscription.id}@profcomff.com')
                ical_event.add('summary', event.name)
                ical_event.add('dtstart', event.start_ts.replace(tzinfo=pytz.UTC))
                ical_event.add('dtend', event.end_ts.replace(tzinfo=pytz.UTC))
                ical_event.add('dtstamp', event.create_ts.replace(tzinfo=pytz.UTC))
                
                # Add more detailed description for subscribed events
                description_parts = []
                if event.group:
                    groups = ", ".join([f"{g.name} ({g.number})" for g in event.group])
                    description_parts.append(f"Groups: {groups}")
                if event.lecturer:
                    lecturers = ", ".join([f"{l.first_name} {l.last_name}" for l in event.lecturer])
                    description_parts.append(f"Lecturers: {lecturers}")
                if event.room:
                    rooms = ", ".join([r.name for r in event.room])
                    description_parts.append(f"Rooms: {rooms}")
                
                ical_event.add('description', " | ".join(description_parts))
                
                # Add location information
                if event.room:
                    location = ", ".join([r.name for r in event.room])
                    ical_event.add('location', vText(location))
                
                # Add categories based on subscription type
                ical_event.add('categories', f'Subscription-{subscription.subscription_type.value.title()}')
                
                calendar.add_component(ical_event)
    
    logger.info(f"Generated personal calendar for user {user_id} with {len(calendar.subcomponents)} events")
    return calendar


async def create_personal_calendar_file(user_id: int, calendar: Calendar) -> str:
    """Create and save personal calendar iCal file"""
    from calendar_backend.settings import get_settings
    import os
    
    settings = get_settings()
    
    # Ensure cache directory exists
    cache_dir = f"{settings.STATIC_PATH}/cache"
    os.makedirs(cache_dir, exist_ok=True)
    
    filename = f"personal_calendar_user_{user_id}.ics"
    filepath = f"{cache_dir}/{filename}"
    
    try:
        with open(filepath, "wb") as f:
            f.write(calendar.to_ical())
        logger.info(f"Created personal calendar file: {filepath}")
        return filepath
    except OSError as e:
        logger.error(f"Failed to create personal calendar file: {e}")
        raise