
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSite import TeraSite
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
from libtera.db.models.TeraDeviceType import TeraDeviceType
from libtera.db.models.TeraSessionType import TeraSessionType
from libtera.db.models.TeraDevice import TeraDevice
from libtera.db.models.TeraKit import TeraKit
from libtera.db.models.TeraSession import TeraSession

from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from libtera.db.models.TeraSiteAccess import TeraSiteAccess


class DBManagerTeraDeviceAccess:
    def __init__(self, device: TeraDevice):
        self.device = device

    def query_session(self, session_id: int):
        sessions = []
        for kit in self.device.device_kits:
            for part in kit.kit_participants:
                for ses in part.participant_sessions:
                    if ses.id_session == session_id:
                        sessions = [TeraSession.get_session_by_id(session_id)]
                        return sessions
        return sessions

    def get_accessible_participants(self, admin_only=False):
        participant_list = []
        for kit_device in self.device.device_kits:
            for part in kit_device.kit_device_kit.kit_participants:
                participant_list.append(part)
        return participant_list

    def get_accessible_participants_ids(self, admin_only=False):
        parts = []

        for part in self.get_accessible_participants(admin_only=admin_only):
            parts.append(part.id_participant)

        return parts

    def get_accessible_session_types(self):
        participants = self.get_accessible_participants()
        project_list = []
        # Fetch all projects for all participants
        for part in participants:
            project_list.append(part.participant_participant_group.id_project)

        session_types = TeraSessionType.query.join(TeraSessionType.session_type_projects).filter(
            TeraProject.id_project.in_(project_list)).all()

        return session_types

    def get_accessible_session_types_ids(self):
        types = []
        for my_type in self.get_accessible_session_types():
            types.append(my_type.id_session_type)
        return types

