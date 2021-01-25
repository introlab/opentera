import unittest
from modules.DatabaseModule.DBManager import DBManager
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.Base import db
from opentera.config.ConfigManager import ConfigManager
import uuid
import os
from tests.opentera.db.models.BaseModelsTest import BaseModelsTest


class TeraParticipantTest(BaseModelsTest):

    filename = os.path.join(os.path.dirname(__file__), 'TeraParticipantTest.db')

    SQLITE = {
        'filename': filename
    }


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

