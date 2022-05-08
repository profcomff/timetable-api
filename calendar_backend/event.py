from dataclasses import dataclass, asdict
from settings import Settings
import datetime
from list_calendar import get_end_of_semester_date



@dataclass()
class Event:
    summary: str
    location: str
    description: str
    start: dict
    end: dict
    recurrence: list
    attendees: list
    reminders: dict


def create_google_calendar_event(summary: str,
                                 start_time: str,
                                 end_time: str,
                                 location: str,
                                 description: str) -> dict:
    """
    Creates a dict with a Google calendar params
    """
    end_sem_date = f"{str(get_end_of_semester_date()).replace('-', '')}T235900Z"
    event = Event(summary=summary,
                  location=location,
                  description=description,
                  start={
                      'dateTime': start_time,
                      'timeZone': 'Europe/Moscow',
                  },
                  end={
                      'dateTime': end_time,
                      'timeZone': 'Europe/Moscow',
                  },
                  recurrence=[
                      f"RRULE:FREQ=WEEKLY;UNTIL={end_sem_date};INTERVAL=2"
                  ],
                  attendees=[],
                  reminders={'useDefault': False}
                  )
    return asdict(event)
