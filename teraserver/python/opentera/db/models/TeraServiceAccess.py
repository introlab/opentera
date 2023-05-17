from opentera.db.Base import BaseModel
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from opentera.db.SoftInsertMixin import SoftInsertMixin
from sqlalchemy import Column, ForeignKey, Integer, Sequence
from sqlalchemy.orm import relationship
from opentera.db.models.TeraServiceRole import TeraServiceRole
import modules.Globals as Globals


class TeraServiceAccess(BaseModel, SoftDeleteMixin, SoftInsertMixin):
    __tablename__ = 't_services_access'
    id_service_access = Column(Integer, Sequence('id_service_project_role_sequence'), primary_key=True,
                               autoincrement=True)
    id_user_group = Column(Integer, ForeignKey('t_users_groups.id_user_group', ondelete='cascade'),
                           nullable=True)
    id_device = Column(Integer, ForeignKey('t_devices.id_device', ondelete='cascade'), nullable=True)
    id_participant_group = Column(Integer, ForeignKey('t_participants_groups.id_participant_group', ondelete='cascade'),
                                  nullable=True)
    id_service_role = Column(Integer, ForeignKey('t_services_roles.id_service_role', ondelete='cascade'),
                             nullable=False)

    service_access_role = relationship("TeraServiceRole", viewonly=True)
    service_access_user_group = relationship("TeraUserGroup", viewonly=True)
    service_access_device = relationship("TeraDevice", viewonly=True)
    service_access_participant_group = relationship("TeraParticipantGroup", viewonly=True)

    def __init__(self):
        pass

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['service_access_role', 'service_access_user_group',
                              'service_access_device', 'service_access_participant_group', 'id_service_role'])

        if minimal:
            ignore_fields.extend([])

        json_val = super().to_json(ignore_fields=ignore_fields)

        # Also expands with service_role infos
        if self.service_access_role:
            json_val.update(self.service_access_role.to_json(minimal=minimal))

        # Remove null values
        if not json_val['id_device']:
            del json_val['id_device']
        if not json_val['id_participant_group']:
            del json_val['id_participant_group']
        if not json_val['id_user_group']:
            del json_val['id_user_group']

        # Complete information if not minimal
        if not minimal:
            if self.service_access_role:
                json_val['service_name'] = self.service_access_role.service_role_service.service_name
                json_val['service_key'] = self.service_access_role.service_role_service.service_key
                json_val['id_service'] = self.service_access_role.service_role_service.id_service
                json_val['service_access_role_name'] = self.service_access_role.service_role_name
            # else:
            #     # This happens on transient objects
            #     from opentera.db.models.TeraService import TeraService
            #     service = TeraService.get_service_by_id(self.id_service)
            #     if service:
            #         json_val['service_name'] = service.service_name
            if self.id_user_group:
                if self.service_access_user_group:
                    json_val['user_group_name'] = self.service_access_user_group.user_group_name
                else:
                    # This happens on transient objects
                    from opentera.db.models.TeraUserGroup import TeraUserGroup
                    ug = TeraUserGroup.get_user_group_by_id(self.id_user_group)
                    if ug:
                        json_val['user_group_name'] = ug.user_group_name
            if self.id_device:
                json_val['device_name'] = self.service_access_device.device_name
            if self.id_participant_group:
                json_val['participant_group_name'] = self.service_access_participant_group.participant_group_name
        return json_val

    @staticmethod
    def get_service_access_by_id(service_access_id: int, with_deleted: bool = False):
        return TeraServiceAccess.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_service_access=service_access_id).first()

    @staticmethod
    def update_service_access_for_user_group(id_service: int, id_user_group: int, id_service_role: int,
                                             id_site: int | None = None, id_project: int | None = None):
        # Check if access already exists
        access = TeraServiceAccess.get_service_access_for_user_group(id_service=id_service,
                                                                     id_user_group=id_user_group,
                                                                     id_site=id_site,
                                                                     id_project=id_project,
                                                                     id_service_role=id_service_role)

        if not access:
            # No access already present for that user group - create new one
            access = TeraServiceAccess()
            access.id_user_group = id_user_group
            access.id_service_role = id_service_role
            TeraServiceAccess.insert(access)
            return access
        else:
            # Update it
            access[0].id_service_role = id_service_role
            TeraServiceAccess.db().session.commit()
            return access[0]

    @staticmethod
    def get_service_access_for_user_group(id_user_group: int, id_service: int, id_project: int | None = None,
                                          id_site: int | None = None, id_service_role: int | None = None,
                                          with_deleted: bool = False):
        query = TeraServiceAccess.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_user_group=id_user_group).join(TeraServiceRole).filter_by(id_service=id_service)

        if id_project:
            query = query.filter_by(id_project=id_project)

        if id_site:
            query = query.filter_by(id_site=id_site)

        if id_service_role and not id_site and not id_project:  # We search with id_service_role only if no project/site
            query = query.filter_by(id_service_role=id_service_role)

        return query.all()

    @staticmethod
    # Returns all access related to a service
    def get_service_access(id_service: int, id_project: int | None = None, id_site: int | None = None,
                           with_deleted: bool = False):
        query = TeraServiceAccess.query.execution_options(include_deleted=with_deleted) \
            .join(TeraServiceRole).filter_by(id_service=id_service)\

        if id_site:
            query = query.filter_by(id_site=id_site)
        if id_project:
            query = query.filter_by(id_project=id_project)

        return query.all()

    @staticmethod
    def delete_service_access_for_user_group(id_service: int, id_user_group: int, id_site: int | None = None,
                                             id_project: int | None = None, id_service_role: int | None = None):

        for service_access in TeraServiceAccess.get_service_access_for_user_group(id_service=id_service,
                                                                                  id_user_group=id_user_group,
                                                                                  id_site=id_site,
                                                                                  id_project=id_project):
            if id_service_role and service_access.id_service_role == id_service_role:
                TeraServiceAccess.delete(service_access.id_service_access)
                return

            if id_site and service_access.service_access_role.id_site == id_site:
                TeraServiceAccess.delete(service_access.id_service_access)
                return

            if id_project and service_access.service_access_role.id_project == id_project:
                TeraServiceAccess.delete(service_access.id_service_access)
                return

    # TODO: Delete those methods (replaced by the generic one)
    @staticmethod
    def delete_service_access_for_user_group_for_site(id_site: int, id_user_group: int):
        for service_access in TeraServiceAccess.get_service_access_for_user_group(
                id_service=Globals.opentera_service_id, id_user_group=id_user_group):
            if service_access.service_access_role.id_site == id_site:
                TeraServiceAccess.delete(service_access.id_service_access)
                break

    @staticmethod
    def delete_service_access_for_user_group_for_project(id_project: int, id_user_group: int):
        for service_access in TeraServiceAccess.get_service_access_for_user_group(
                id_service=Globals.opentera_service_id, id_user_group=id_user_group):
            if service_access.service_access_role.id_project == id_project:
                TeraServiceAccess.delete(service_access.id_service_access)
                break

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraService import TeraService
            from opentera.db.models.TeraUserGroup import TeraUserGroup
            from opentera.db.models.TeraDevice import TeraDevice
            from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup

            device = TeraDevice.get_device_by_name('Apple Watch #W05P1')
            group = TeraParticipantGroup.get_participant_group_by_group_name('Default Participant Group A')

            service_bureau = TeraService.get_service_by_key('BureauActif')
            service_bureau_admin = service_bureau.service_roles[0]
            service_bureau_user = service_bureau.service_roles[1]

            service_logging = TeraService.get_service_by_key('LoggingService')
            service_logging_admin = service_logging.service_roles[0]
            service_logging_user = service_logging.service_roles[1]

            user_group1 = TeraUserGroup.get_user_group_by_group_name('Users - Project 1')
            user_group2 = TeraUserGroup.get_user_group_by_group_name('Admins - Project 1')

            service_role = TeraServiceAccess()
            service_role.id_user_group = user_group1.id_user_group
            service_role.id_service_role = service_bureau_admin.id_service_role
            TeraServiceAccess.db().session.add(service_role)

            service_role = TeraServiceAccess()
            service_role.id_user_group = user_group2.id_user_group
            service_role.id_service_role = service_logging_admin.id_service_role
            TeraServiceAccess.db().session.add(service_role)

            service_role = TeraServiceAccess()
            service_role.id_device = device.id_device
            service_role.id_service_role = service_bureau_user.id_service_role
            TeraServiceAccess.db().session.add(service_role)

            service_role = TeraServiceAccess()
            service_role.id_participant_group = group.id_participant_group
            service_role.id_service_role = service_logging_user.id_service_role
            TeraServiceAccess.db().session.add(service_role)

            TeraServiceAccess.db().session.commit()
