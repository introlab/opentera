
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraSession import TeraSession

from sqlalchemy import func

import datetime


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

    def query_existing_session(self, session_name: str, session_type_id: int, session_date: datetime,
                               participant_uuids: list):
        sessions = TeraSession.query.filter(TeraSession.id_creator_device == self.device.id_device).\
            filter(TeraSession.session_name == session_name).filter(TeraSession.id_session_type == session_type_id).\
            filter(func.date(TeraSession.session_start_datetime) == session_date.date()).\
            order_by(TeraSession.id_session.asc()).all()

        for session in sessions:
            sessions_participants_uuids = set([part.participant_uuid for part in session.session_participants])
            if set(participant_uuids) == sessions_participants_uuids:
                # We have a match on that session participants too
                return session
        return None

    def get_accessible_sessions(self):
        query = TeraSession.query.filter(TeraSession.id_creator_device == self.device.id_device)
        return query.all()

    def get_accessible_sessions_ids(self):
        sessions = self.get_accessible_sessions()
        return [session.id_session for session in sessions]

    def get_accessible_participants(self, admin_only=False):
        return self.device.device_participants

    def get_accessible_participants_ids(self, admin_only=False):
        parts = []

        for part in self.get_accessible_participants(admin_only=admin_only):
            parts.append(part.id_participant)

        return parts

    def get_accessible_session_types(self):

        # participants = self.get_accessible_participants()
        # project_list = []
        # Get project list
        project_list = [proj.id_project for proj in self.device.device_projects]
        # for part in participants:
        #     project_list.append(part.id_project)

        session_types = TeraSessionType.query.join(TeraSessionType.session_type_projects)\
            .filter(TeraProject.id_project.in_(project_list)).all()

        return session_types

    def get_accessible_session_types_ids(self):
        types = []
        for my_type in self.get_accessible_session_types():
            types.append(my_type.id_session_type)
        return types

    def get_accessible_assets(self, id_asset=None):
        from opentera.db.models.TeraAsset import TeraAsset
        query = TeraAsset.query.filter(TeraAsset.id_device == self.device.id_device)
        if id_asset:
            query = query.filter(TeraAsset.id_asset == id_asset)

        return query.all()
