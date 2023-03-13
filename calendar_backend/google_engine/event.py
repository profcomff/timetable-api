from pydantic import BaseModel

from calendar_backend.methods import utils


class Event(BaseModel):
    summary: str
    location: str | None
    description: str | None
    start: dict[str, str]
    end: dict[str, str]
    recurrence: list[str]
    attendees: list[str]
    reminders: dict[str, bool]


def create_google_calendar_event(
    summary: str, start_time: str, end_time: str, location: str, description: str
) -> Event:
    """
    Creates a dict with a Google calendar params
    """
    end_sem_date = str(utils.get_end_of_semester_date()).replace('-', '')
    end_sem_date_format = f"{end_sem_date}T235900Z"
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
        recurrence=[f"RRULE:FREQ=WEEKLY;UNTIL={end_sem_date_format};INTERVAL=2"],
        attendees=[],
        reminders={"useDefault": False},
    )
    return event
