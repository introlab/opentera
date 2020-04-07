import unittest
from libtera.db.Base import db
from libtera.db.DBManager import DBManager
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from libtera.db.Base import db
from libtera.ConfigManager import ConfigManager
import uuid
import os
from passlib.hash import bcrypt


class TeraParticipantTest(unittest.TestCase):

    filename = 'TeraParticipantTest.db'

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

    def tearDown(self):
        pass

    def test_token(self):

        participantGroup = TeraParticipantGroup()
        participantGroup.participant_group_name = 'participants'
        participantGroup.id_project = 1

        participant = TeraParticipant()
        participant.participant_name = 'Test Participant'
        participant.participant_uuid = str(uuid.uuid4())
        participant.participant_participant_group = participantGroup

        token = participant.create_token()

        self.assertNotEqual(token, "")
        db.session.add(participantGroup)
        db.session.add(participant)

        db.session.commit()

        # Load participant from invalid token
        loadedParticipant = TeraParticipant.get_participant_by_token('rien')
        self.assertEqual(loadedParticipant, None)

        # Load participant from valid token
        loadedParticipant = TeraParticipant.get_participant_by_token(token)
        self.assertEqual(loadedParticipant.participant_uuid, participant.participant_uuid)

    def test_json(self):
        participant = TeraParticipant.get_participant_by_name('Participant #1')

        json = participant.to_json()

        print(json)

