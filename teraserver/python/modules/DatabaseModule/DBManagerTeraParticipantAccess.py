
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraSite import TeraSite
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraSessionParticipants import TeraSessionParticipants
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraDeviceType import TeraDeviceType
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraDevice import TeraDevice
#from opentera.db.models.TeraDeviceData import TeraDeviceData
from opentera.db.models.TeraDeviceProject import TeraDeviceProject
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant


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

    # def query_device_data(self, filters: dict):
    #     # Make sure you filter results with id_participant to return TeraDeviceData
    #     # that are accessible by current participant
    #     result = TeraDeviceData.query.filter_by(**filters).join(TeraSession).join(TeraSessionParticipants).\
    #         filter_by(id_participant=self.participant.id_participant).all()
    #     return result

