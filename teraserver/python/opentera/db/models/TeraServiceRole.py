from opentera.db.Base import BaseModel
from opentera.db.SoftDeleteMixin import SoftDeleteMixin
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence, Boolean, TIMESTAMP
from sqlalchemy.orm import relationship


class TeraServiceRole(BaseModel, SoftDeleteMixin):
    __tablename__ = 't_services_roles'
    id_service_role = Column(Integer, Sequence('id_service_role_sequence'), primary_key=True, autoincrement=True)
    id_service = Column(Integer, ForeignKey('t_services.id_service', ondelete='cascade'), nullable=False)
    # Specific project role for a project, used mostly with OpenTera service for project access
    id_project = Column(Integer, ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=True)
    # Specific site role for a site, used mostly with OpenTera service for site access
    id_site = Column(Integer, ForeignKey('t_sites.id_site', ondelete='cascade'), nullable=True)
    service_role_name = Column(String(100), nullable=False)

    service_role_service = relationship("TeraService", viewonly=True)
    service_role_project = relationship('TeraProject', viewonly=True)
    service_role_site = relationship('TeraSite', viewonly=True)

    service_role_user_groups = relationship("TeraUserGroup", secondary="t_services_access",
                                            back_populates="user_group_services_roles",  lazy='selectin')

    def __init__(self):
        pass

    def __str__(self):
        return '<TeraServiceRole Service = ' + str(self.service_role_service.service_name) + ', Role = ' + \
               str(self.service_role_name) + ' >'

    def __repr__(self):
        return self.__str__()

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['service_role_service', 'service_role_project', 'service_role_site',
                              'service_role_user_group'])

        if minimal:
            ignore_fields.extend([])

        json_val = super().to_json(ignore_fields=ignore_fields)

        # Remove null values
        if not json_val['id_project']:
            del json_val['id_project']
        else:
            if not minimal:
                json_val['project_name'] = self.service_role_project.project_name

        if not json_val['id_site']:
            del json_val['id_site']
        else:
            if not minimal:
                json_val['site_name'] = self.service_role_site.site_name

        if not minimal:
            json_val['service_name'] = self.service_role_service.service_name
        return json_val

    @staticmethod
    def get_service_roles(service_id: int, globals_only: bool = False, with_deleted: bool = False):
        query = TeraServiceRole.query.execution_options(include_deleted=with_deleted).filter_by(id_service=service_id)

        if globals_only:
            query = query.filter_by(id_site=None).filter_by(id_project=None)

        return query.all()

    @staticmethod
    def get_service_roles_for_site(service_id: int, site_id: int, with_deleted: bool = False):
        return TeraServiceRole.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_service=service_id, id_site=site_id).all()

    @staticmethod
    def get_service_roles_for_project(service_id: int, project_id: int, with_deleted: bool = False):
        return TeraServiceRole.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_service=service_id, id_project=project_id).all()

    @staticmethod
    def get_service_role_by_id(role_id: int, with_deleted: bool = False):
        return TeraServiceRole.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_service_role=role_id).first()

    @staticmethod
    def get_service_role_by_name(service_id: int, rolename: str, site_id: int | None = None,
                                 project_id: int | None = None, with_deleted: bool = False):

        query = TeraServiceRole.query.execution_options(include_deleted=with_deleted)\
            .filter_by(id_service=service_id, service_role_name=rolename)

        if site_id:
            query = query.filter_by(id_site=site_id)

        if project_id:
            query = query.filter_by(id_project=project_id)

        return query.first()

    @staticmethod
    def create_defaults(test=False):
        from opentera.db.models.TeraService import TeraService

        for service in TeraService.query.all():
            if service.service_key != 'OpenTeraServer':  # Don't add global roles for TeraServer
                new_role = TeraServiceRole()
                new_role.id_service = service.id_service
                new_role.service_role_name = 'admin'
                TeraServiceRole.db().session.add(new_role)

                new_role = TeraServiceRole()
                new_role.id_service = service.id_service
                new_role.service_role_name = 'user'
                TeraServiceRole.db().session.add(new_role)
            else:
                pass  # TODO: do what we did in Project and Site Access

        TeraServiceRole.db().session.commit()
