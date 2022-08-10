from ..methods import get_end_of_semester_date
from dataclasses import asdict
from pydantic.dataclasses import dataclass


@dataclass
class Event:
    summary: str
    location: str
    description: str
    start: dict[str, str]
    end: dict[str, str]
    recurrence: list[str]
    attendees: list[str]
    reminders: dict[str, bool]


def create_google_calendar_event(summary: str, start_time: str, end_time: str, location: str, description: str) -> Event:
    """
    Creates a dict with a Google calendar params
    """
    end_sem_date = f"{str(get_end_of_semester_date()).replace('-', '')}T235900Z"
    event = Event(
        summary=summary,
        location=location,
        description=description,
        start={
            "dateTime": start_time,
            "timeZone": "Europe/Moscow",
        },
        end={
            "dateTime": end_time,
            "timeZone": "Europe/Moscow",
        },
        recurrence=[f"RRULE:FREQ=WEEKLY;UNTIL={end_sem_date};INTERVAL=2"],
        attendees=[],
        reminders={"useDefault": False},
    )
    return event
