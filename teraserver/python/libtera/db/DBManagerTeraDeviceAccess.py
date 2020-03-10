
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
from libtera.db.models.TeraDeviceType import TeraDeviceType
from libtera.db.models.TeraSessionType import TeraSessionType
from libtera.db.models.TeraDevice import TeraDevice
from libtera.db.models.TeraSession import TeraSession

from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from libtera.db.models.TeraSiteAccess import TeraSiteAccess


class DBManagerTeraDeviceAccess:
    def __init__(self, device: TeraDevice):
        self.device = device

    def query_session(self, session_id: int):
        sessions = []
        for part in self.device.device_participants:
            for ses in part.participant_sessions:
                if ses.id_session == session_id:
                    sessions = [TeraSession.get_session_by_id(session_id)]
                    return sessions
        return sessions

    def get_accessible_participants(self, admin_only=False):
        return self.device.device_participants

    def get_accessible_participants_ids(self, admin_only=False):
        parts = []

        for part in self.get_accessible_participants(admin_only=admin_only):
            parts.append(part.id_participant)

        return parts

    def get_accessible_session_types(self):
        from libtera.db.models.TeraSessionTypeDeviceType import TeraSessionTypeDeviceType

        participants = self.get_accessible_participants()
        project_list = []
        # Fetch all projects for all participants
        for part in participants:
            project_list.append(part.id_project)

        session_types = TeraSessionType.query.join(TeraSessionType.session_type_projects).join(
            TeraSessionType.session_type_devices_types).filter(TeraProject.id_project.in_(project_list))\
            .filter(TeraSessionTypeDeviceType.id_device_type == self.device.device_type).all()

        return session_types

    def get_accessible_session_types_ids(self):
        types = []
        for my_type in self.get_accessible_session_types():
            types.append(my_type.id_session_type)
        return types

    def get_accessible_assets(self, id_asset=None):
        from libtera.db.models.TeraAsset import TeraAsset
        query = TeraAsset.query.filter(TeraAsset.id_device == self.device.id_device)
        if id_asset:
            query = query.filter(TeraAsset.id_asset == id_asset)

        return query.all()
