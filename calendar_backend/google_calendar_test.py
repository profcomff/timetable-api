from google_api_utils import *
from service import get_calendar_service


def test_can_create_calendar_with_timetable():
    service = get_calendar_service(44)
    group = '116' # group is a String type in db
    create_calendar_with_timetable(service, group)


def test_can_create_empty_calendar():
    service = get_calendar_service(44)
    _id = create_calendar(service, '106')
    print('id:', _id)
    calendar = service.calendars().get(calendarId=_id).execute()
    print(calendar)


if __name__ == '__main__':
    # create_google_events_from_db('101')
    test_can_create_empty_calendar()
    # test_can_create_calendar_with_timetable()