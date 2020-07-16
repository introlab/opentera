
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraSessionParticipants import TeraSessionParticipants
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
from libtera.db.models.TeraDeviceType import TeraDeviceType
from libtera.db.models.TeraSessionType import TeraSessionType
from libtera.db.models.TeraDevice import TeraDevice
from libtera.db.models.TeraDeviceData import TeraDeviceData
from libtera.db.models.TeraDeviceProject import TeraDeviceProject
from libtera.db.models.TeraSession import TeraSession
from libtera.db.models.TeraDeviceParticipant import TeraDeviceParticipant


class DBManagerTeraParticipantAccess:
    def __init__(self, participant: TeraParticipant):
        self.participant = participant

    def query_session(self, filters: dict):
        # Make sure you filter results with id_participant to return TeraDevices
        # that are accessible by current participant
        result = TeraSession.query.filter_by(**filters).join(TeraSessionParticipants). \
            filter_by(id_participant=self.participant.id_participant).all()
        return result

    def query_device(self, filters: dict):
        # Make sure you filter results with id_participant to return TeraDevices
        # that are accessible by current participant
        result = TeraDevice.query.filter_by(**filters).join(TeraDeviceParticipant).\
            filter_by(id_participant=self.participant.id_participant).all()
        return result

    def query_device_data(self, filters: dict):
        # Make sure you filter results with id_participant to return TeraDeviceData
        # that are accessible by current participant
        result = TeraDeviceData.query.filter_by(**filters).join(TeraSession).join(TeraSessionParticipants).\
            filter_by(id_participant=self.participant.id_participant).all()
        return result

