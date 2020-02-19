
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

from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from libtera.db.models.TeraSiteAccess import TeraSiteAccess


class DBManagerTeraParticipantAccess:
    def __init__(self, participant: TeraParticipant):
        self.participant = participant

    def query_session(self, session_id: int):
        sessions = []

        for session in self.participant.participant_sessions:
            if session.id_session == session_id:
                # TODO do we need to make a request to DB?
                sessions = [TeraSession.get_session_by_id(session_id)]
                return sessions
        return sessions

    def query_device(self, device_id: int):
        devices = []
        for device in self.participant.participant_devices:
            if device.id_device == device_id:
                # TODO do we need to make a request to DB?
                devices = [TeraDevice.get_device_by_id(device_id)]
                return devices
        return devices

    def query_device_data(self, filters: dict):
        # Make sure you filter results with id_participant to return TeraDeviceData
        # that are only accessible by current participant
        result = TeraDeviceData.query.filter_by(**filters).join(TeraSession).join(TeraSessionParticipants).\
            filter_by(id_participant=self.participant.id_participant).all()

        return result

