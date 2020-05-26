import unittest
from modules.DatabaseModule.DBManager import DBManager
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
from libtera.db.Base import db
from libtera.ConfigManager import ConfigManager
import uuid
import os


class TeraParticipantTest(unittest.TestCase):

    filename = os.path.join(os.path.dirname(__file__), 'TeraParticipantTest.db')

    SQLITE = {
        'filename': filename
    }

    def setUp(self):
        if os.path.isfile(self.filename):
            print('removing database')
            os.remove(self.filename)

        self.config = ConfigManager()
        # Create default config
        self.config.create_defaults()
        self.db_man = DBManager(self.config)
        self.db_man.open_local(self.SQLITE)

        # Creating default users / tests.
        self.db_man.create_defaults(self.config)

    def tearDown(self):
        pass

    def test_token(self):
        return

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

        return
        participant = TeraParticipant.get_participant_by_name('Participant #1')

        json = participant.to_json()

        print(json)

