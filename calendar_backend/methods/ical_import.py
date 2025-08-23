"""iCal import functionality"""

import logging
from datetime import datetime
from typing import BinaryIO, Dict, List, Tuple

from icalendar import Calendar
from sqlalchemy.orm import Session

from calendar_backend.models import Event

logger = logging.getLogger(__name__)


class ICalImportResult:
    """Result of iCal import operation"""
    def __init__(self):
        self.events_created: List[Event] = []
        self.events_skipped: List[Dict] = []
        self.errors: List[str] = []
        self.total_events_processed: int = 0


async def import_ical_file(file_content: BinaryIO, user_id: int | None, session: Session) -> ICalImportResult:
    """Import events from an iCal file with detailed results"""
    result = ICalImportResult()
    
    try:
        # Parse the iCal content
        calendar = Calendar.from_ical(file_content.read())
        
        for component in calendar.walk():
            if component.name == "VEVENT":
                result.total_events_processed += 1
                
                try:
                    # Extract event data
                    summary = str(component.get('summary', 'Untitled Event'))
                    start_dt = component.get('dtstart')
                    end_dt = component.get('dtend')
                    description = str(component.get('description', ''))
                    uid = str(component.get('uid', ''))

                    # Validate required fields
                    if not start_dt or not end_dt:
                        error_msg = f"Event '{summary}' missing start or end time"
                        logger.warning(error_msg)
                        result.events_skipped.append({
                            'summary': summary,
                            'reason': 'Missing start or end time',
                            'uid': uid
                        })
                        continue

                    # Convert to datetime objects
                    try:
                        if hasattr(start_dt.dt, 'date'):
                            # It's a datetime object
                            start_ts = start_dt.dt
                            end_ts = end_dt.dt
                        else:
                            # It's a date object, convert to datetime
                            start_ts = datetime.combine(start_dt.dt, datetime.min.time())
                            end_ts = datetime.combine(end_dt.dt, datetime.min.time())
                        
                        # Ensure timezone-naive datetime for database storage
                        if start_ts.tzinfo:
                            start_ts = start_ts.replace(tzinfo=None)
                        if end_ts.tzinfo:
                            end_ts = end_ts.replace(tzinfo=None)
                            
                    except Exception as e:
                        error_msg = f"Event '{summary}' has invalid date format: {e}"
                        logger.warning(error_msg)
                        result.events_skipped.append({
                            'summary': summary,
                            'reason': f'Invalid date format: {e}',
                            'uid': uid
                        })
                        continue

                    # Validate event duration
                    if start_ts >= end_ts:
                        error_msg = f"Event '{summary}' has invalid duration (start >= end)"
                        logger.warning(error_msg)
                        result.events_skipped.append({
                            'summary': summary,
                            'reason': 'Invalid duration (start >= end)',
                            'uid': uid
                        })
                        continue

                    # Create event data
                    event_data = {
                        'name': summary[:255],  # Truncate to fit database field
                        'start_ts': start_ts,
                        'end_ts': end_ts,
                        'is_personal': user_id is not None,
                        'creator_user_id': user_id,
                    }

                    # Create event
                    try:
                        event = Event.create(session=session, **event_data)
                        result.events_created.append(event)
                        logger.info(f"Successfully imported event: {summary}")
                    except Exception as e:
                        error_msg = f"Failed to create event '{summary}': {e}"
                        logger.error(error_msg)
                        result.events_skipped.append({
                            'summary': summary,
                            'reason': f'Database error: {e}',
                            'uid': uid
                        })
                        
                except Exception as e:
                    error_msg = f"Error processing event component: {e}"
                    logger.error(error_msg)
                    result.errors.append(error_msg)

        # Commit successful events
        if result.events_created:
            session.commit()
            logger.info(f"Successfully imported {len(result.events_created)} events")
        
        return result

    except Exception as e:
        error_msg = f"Failed to parse iCal file: {e}"
        logger.error(error_msg)
        result.errors.append(error_msg)
        session.rollback()
        return result


def validate_ical_file(file_content: BinaryIO) -> Tuple[bool, List[str]]:
    """Validate if the file is a valid iCal file with detailed error reporting"""
    errors = []
    
    try:
        file_content.seek(0)
        content = file_content.read()
        file_content.seek(0)  # Reset for later use
        
        # Check file size (max 10MB)
        if len(content) > 10 * 1024 * 1024:
            errors.append("File too large (max 10MB)")
            return False, errors
        
        # Basic validation - check if it contains iCal markers
        try:
            content_str = content.decode('utf-8', errors='replace')
        except Exception as e:
            errors.append(f"File encoding error: {e}")
            return False, errors
        
        # Check for required iCal structure
        if 'BEGIN:VCALENDAR' not in content_str:
            errors.append("Missing VCALENDAR block")
            
        if 'BEGIN:VEVENT' not in content_str:
            errors.append("No events found in calendar file")
        
        if 'END:VCALENDAR' not in content_str:
            errors.append("Incomplete VCALENDAR block")
            
        # Try to parse with icalendar library
        try:
            Calendar.from_ical(content)
        except Exception as e:
            errors.append(f"iCal parsing error: {e}")
            
        return len(errors) == 0, errors
        
    except Exception as e:
        errors.append(f"File validation error: {e}")
        return False, errors


def get_ical_preview(file_content: BinaryIO, max_events: int = 5) -> Dict:
    """Get a preview of events in the iCal file without importing"""
    try:
        file_content.seek(0)
        calendar = Calendar.from_ical(file_content.read())
        file_content.seek(0)  # Reset for later use
        
        events = []
        total_count = 0
        
        for component in calendar.walk():
            if component.name == "VEVENT":
                total_count += 1
                
                if len(events) < max_events:
                    summary = str(component.get('summary', 'Untitled Event'))
                    start_dt = component.get('dtstart')
                    end_dt = component.get('dtend')
                    
                    start_str = str(start_dt.dt) if start_dt else 'Unknown'
                    end_str = str(end_dt.dt) if end_dt else 'Unknown'
                    
                    events.append({
                        'summary': summary,
                        'start': start_str,
                        'end': end_str,
                    })
        
        return {
            'total_events': total_count,
            'preview_events': events,
            'calendar_name': str(calendar.get('x-wr-calname', 'Imported Calendar')),
        }
        
    except Exception as e:
        return {
            'error': f"Failed to preview calendar: {e}",
            'total_events': 0,
            'preview_events': [],
        }