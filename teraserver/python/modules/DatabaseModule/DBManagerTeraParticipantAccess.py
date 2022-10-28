from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant


class DBManagerTeraParticipantAccess:
    def __init__(self, participant: TeraParticipant):
        self.participant = participant

    # def query_session(self, limit: int = None, offset: int = None):
        # Make sure you filter results with id_participant to return TeraDevices
        # that are accessible by current participant
        # query = TeraSession.query().filter_by(**filters).join(TeraSessionParticipants). \
        #     filter_by(id_participant=self.participant.id_participant)
        # if limit:
        #     query = query.limit(limit)
        #
        # if offset:
        #     query = query.offset(offset)
        #
        # return query.all()

    def query_device(self, filters: dict):
        # Make sure you filter results with id_participant to return TeraDevices
        # that are accessible by current participant
        result = TeraDevice.query().filter_by(**filters).join(TeraDeviceParticipant).\
            filter_by(id_participant=self.participant.id_participant).all()
        return result

    def get_accessible_assets(self, id_asset: int = None, uuid_asset: str = None):
        from opentera.db.models.TeraAsset import TeraAsset

        # A participant can only have access to assets that are directly assigned to them (where id_participant is set
        # to their value)
        query = TeraAsset.query().filter(TeraAsset.id_participant == self.participant.id_participant)
        if id_asset:
            query = query.filter(TeraAsset.id_asset == id_asset)
        elif uuid_asset:
            query = query.filter(TeraAsset.asset_uuid == uuid_asset)

        return query.all()

    def get_accessible_services(self):
        from opentera.db.models.TeraServiceProject import TeraServiceProject
        service_projects = TeraServiceProject.get_services_for_project(id_project=self.participant.id_project)

        return [service_project.service_project_service for service_project in service_projects]

