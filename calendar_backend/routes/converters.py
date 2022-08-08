import calendar_backend.models.db
import calendar_backend.routes.models


def timetable_converter(timetable_server: calendar_backend.models.db.Timetable) -> dict:
    """
    Converting database format to user-friendly format
    """
    return {
        "start": timetable_server.start,
        "end": timetable_server.end,
        "odd": timetable_server.odd,
        "even": timetable_server.even,
        "weekday": timetable_server.weekday,
        "group": timetable_server.group,
        "subject": timetable_server.subject,
        "place": timetable_server.place,
        "teacher": timetable_server.teacher,
    }
