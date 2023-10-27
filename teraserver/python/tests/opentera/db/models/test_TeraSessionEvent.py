from tests.opentera.db.models.BaseModelsTest import BaseModelsTest
from opentera.db.models.TeraSessionEvent import TeraSessionEvent
import datetime


class TeraSessionEventTest(BaseModelsTest):

    def test_defaults(self):
        with self._flask_app.app_context():
            pass

    @staticmethod
    def new_test_session_event(id_session: int, id_event_type: int) -> TeraSessionEvent:
        event = TeraSessionEvent()
        event.id_session = id_session
        event.id_session_event_type = id_event_type
        event.session_event_datetime = datetime.datetime.now()
        TeraSessionEvent.insert(event)
        return event
