from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSession import TeraSession
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraAsset import TeraAsset


from sqlalchemy import func

import datetime

class DBManagerTeraParticipantAccess:
    def __init__(self, participant: TeraParticipant):
        self.participant = participant

    def query_device(self, filters: dict) -> list[TeraDevice]:
        # Make sure you filter results with id_participant to return TeraDevices
        # that are accessible by current participant
        result = TeraDevice.query.filter_by(**filters).join(TeraDeviceParticipant).\
            filter_by(id_participant=self.participant.id_participant).all()
        return result

    def get_accessible_assets(self, id_asset: int = None, uuid_asset: str = None, session_id: int = None) -> list[TeraAsset]:
        # A participant can only have access to assets that are directly assigned to them (where id_participant is set
        # to their value)
        query = TeraAsset.query.filter(TeraAsset.id_participant == self.participant.id_participant)
        if id_asset:
            query = query.filter(TeraAsset.id_asset == id_asset)
        elif uuid_asset:
            query = query.filter(TeraAsset.asset_uuid == uuid_asset)
        elif session_id:
            query = query.filter(TeraAsset.id_session == session_id)

        return query.all()

    def get_accessible_services(self) -> list[TeraService]:
        service_projects = TeraServiceProject.get_services_for_project(id_project=self.participant.id_project)
        return [service_project.service_project_service for service_project in service_projects]

    def get_accessible_session_types(self) -> list[TeraSessionType]:
        session_types = TeraSessionType.query.join(TeraSessionType.session_type_projects)\
            .filter_by(id_project=self.participant.id_project).all()
        return session_types

    def get_accessible_session_types_ids(self) -> list[int]:
        types = []
        for my_type in self.get_accessible_session_types():
            types.append(my_type.id_session_type)
        return types

    def query_existing_session(self, session_name: str, session_type_id: int, session_date: datetime,
                               participant_uuids: list) -> TeraSession | None:
        sessions = TeraSession.query.filter(TeraSession.id_creator_participant == self.participant.id_participant).\
            filter(TeraSession.session_name == session_name).filter(TeraSession.id_session_type == session_type_id).\
            filter(func.date(TeraSession.session_start_datetime) == session_date.date()).\
            order_by(TeraSession.id_session.asc()).all()

        for session in sessions:
            sessions_participants_uuids = set([part.participant_uuid for part in session.session_participants])
            if set(participant_uuids) == sessions_participants_uuids:
                # We have a match on that session participants too
                return session
        return None

    def get_accessible_sessions(self) -> list[TeraSession]:
        query = TeraSession.query.filter(TeraSession.id_creator_participant == self.participant.id_participant)
        return query.all()

    def get_accessible_sessions_ids(self) -> list[int]:
        sessions = self.get_accessible_sessions()
        return [session.id_session for session in sessions]

    def get_accessible_tests_types(self) -> list[TeraTestType]:
        test_types = TeraTestType.query.join(TeraTestTypeProject).filter_by(id_project=self.participant.id_project).all()
        return test_types

    def get_accessible_tests_types_ids(self) -> list[int]:
        test_types = self.get_accessible_tests_types()
        return [test_type.id_test_type for test_type in test_types]
