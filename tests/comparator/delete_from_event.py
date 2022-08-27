from calendar_backend.models import Event

def test_compatator_event(event_path, dbsession):
    event_id = int(event_path.split("/")[-1])
    event = Event.get(event_id, session=dbsession)
    rooms = event.room
    for room in rooms:
        room = str(room)
        pass
