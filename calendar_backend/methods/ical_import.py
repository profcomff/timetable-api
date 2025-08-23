"""iCal import functionality"""

import logging
from datetime import datetime
from typing import BinaryIO

from icalendar import Calendar
from sqlalchemy.orm import Session

from calendar_backend.models import Event

logger = logging.getLogger(__name__)


async def import_ical_file(file_content: BinaryIO, user_id: int | None, session: Session) -> list[Event]:
    """Import events from an iCal file"""
    try:
        # Parse the iCal content
        calendar = Calendar.from_ical(file_content.read())
        events_created = []

        for component in calendar.walk():
            if component.name == "VEVENT":
                # Extract event data
                summary = str(component.get('summary', ''))
                start_dt = component.get('dtstart')
                end_dt = component.get('dtend')
                description = str(component.get('description', ''))

                if not start_dt or not end_dt:
                    logger.warning(f"Skipping event '{summary}' due to missing start/end time")
                    continue

                # Convert to datetime if needed
                if hasattr(start_dt.dt, 'date'):
                    # It's a datetime object
                    start_ts = start_dt.dt
                    end_ts = end_dt.dt
                else:
                    # It's a date object, convert to datetime
                    start_ts = datetime.combine(start_dt.dt, datetime.min.time())
                    end_ts = datetime.combine(end_dt.dt, datetime.min.time())

                # Create event
                event_data = {
                    'name': summary,
                    'start_ts': start_ts,
                    'end_ts': end_ts,
                    'is_personal': user_id is not None,
                    'creator_user_id': user_id,
                }

                try:
                    event = Event.create(session=session, **event_data)
                    events_created.append(event)
                    logger.info(f"Created event: {summary}")
                except Exception as e:
                    logger.error(f"Failed to create event '{summary}': {e}")
                    continue

        session.commit()
        return events_created

    except Exception as e:
        logger.error(f"Failed to import iCal file: {e}")
        session.rollback()
        raise ValueError(f"Failed to parse iCal file: {str(e)}")


def validate_ical_file(file_content: BinaryIO) -> bool:
    """Validate if the file is a valid iCal file"""
    try:
        file_content.seek(0)
        content = file_content.read()
        file_content.seek(0)  # Reset for later use
        
        # Basic validation - check if it contains iCal markers
        content_str = content.decode('utf-8', errors='ignore')
        return 'BEGIN:VCALENDAR' in content_str and 'BEGIN:VEVENT' in content_str
    except Exception:
        return False