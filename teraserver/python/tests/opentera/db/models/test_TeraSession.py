import unittest
from modules.DatabaseModule.DBManager import DBManager
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraSession import TeraSession, TeraSessionStatus
import os
from opentera.config.ConfigManager import ConfigManager
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class TeraSessionTest(BaseModelsTest):

    filename = os.path.join(os.path.dirname(__file__), 'TeraSessionTest.db')

    SQLITE = {
        'filename': filename
    }

    def test_session_defaults(self):
        for session in TeraSession.query.all():
            my_list = [session.id_creator_device, session.id_creator_participant,
                       session.id_creator_service, session.id_creator_user]
            # Only one not None
            self.assertEqual(1, len([x for x in my_list if x is not None]))

    def test_session_new(self):
        from datetime import datetime
        from modules.DatabaseModule.DBManagerTeraDeviceAccess import DBManagerTeraDeviceAccess

        session = TeraSession()

        device = TeraDevice.get_device_by_id(1)
        access = DBManagerTeraDeviceAccess(device)
        participant1 = TeraParticipant.get_participant_by_id(1)
        participant2 = TeraParticipant.get_participant_by_id(2)

        session_types = access.get_accessible_session_types()

        session.session_name = 'TEST'
        session.session_creator_device = device
        session.session_participants.append(participant1)
        session.session_participants.append(participant2)
        session.session_start_datetime = datetime.now()
        session.session_status = TeraSessionStatus.STATUS_NOTSTARTED.value

        if len(session_types) > 0:
            session.id_session_type = session_types[0].id_session_type
            TeraSession.insert(session)

    def test_session_from_json(self):
        pass
        #
        # session = {'session': {'id_session': 0,
        #                        'session_participants': participants_id_list,
        #                        'id_session_type': session_type['id_session_type'],
        #                        'session_name': 'TEST',
        #                        'session_status': 0,
        #                        'session_start_datetime': str(datetime.now())}}
