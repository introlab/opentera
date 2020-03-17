import unittest
from libtera.db.DBManager import DBManager
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraDevice import TeraDevice
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraSession import TeraSession, TeraSessionStatus
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from libtera.db.Base import db
import uuid
import os
from passlib.hash import bcrypt
from libtera.ConfigManager import ConfigManager


class TeraUserTest(unittest.TestCase):

    filename = 'TeraSessionTest.db'

    SQLITE = {
        'filename': filename
    }

    db_man = DBManager()

    config = ConfigManager()

    def setUp(self):
        if os.path.isfile(self.filename):
            print('removing database')
            os.remove(self.filename)

        self.db_man.open_local(self.SQLITE)

        # Create default config
        self.config.create_defaults()

        # Creating default users / tests.
        self.db_man.create_defaults(self.config)

    def test_Session_new(self):
        from datetime import datetime
        from libtera.db.DBManagerTeraDeviceAccess import DBManagerTeraDeviceAccess

        session = TeraSession()

        device = TeraDevice.get_device_by_id(1)
        access = DBManagerTeraDeviceAccess(device)
        participant = TeraParticipant.get_participant_by_id(1)

        session_types = access.get_accessible_session_types()

        session.session_name = 'TEST'
        session.session_creator_device = device
        session.session_participants.append(participant)
        session.session_start_datetime = datetime.now()
        session.session_status = TeraSessionStatus.STATUS_NOTSTARTED.value

        if len(session_types) > 0:
            session.id_session_type = session_types[0].id_session_type
            TeraSession.insert(session)
