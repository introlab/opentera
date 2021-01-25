from opentera.db.Base import db, BaseModel


class TeraServiceRole(db.Model, BaseModel):
    __tablename__ = 't_services_roles'
    id_service_role = db.Column(db.Integer, db.Sequence('id_service_role_sequence'), primary_key=True,
                                autoincrement=True)
    id_service = db.Column(db.Integer, db.ForeignKey('t_services.id_service', ondelete='cascade'), nullable=False)
    # Specific project role for a project, used mostly with OpenTera service for project access
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=True)
    # Specific site role for a site, used mostly with OpenTera service for site access
    id_site = db.Column(db.Integer, db.ForeignKey('t_sites.id_site', ondelete='cascade'), nullable=True)
    service_role_name = db.Column(db.String(100), nullable=False)

    service_role_service = db.relationship("TeraService")
    service_role_project = db.relationship('TeraProject')
    service_role_site = db.relationship('TeraSite')

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

        ignore_fields.extend(['service_role_service', 'service_role_project', 'service_role_site'])

        if minimal:
            ignore_fields.extend([])

        json_val = super().to_json(ignore_fields=ignore_fields)

        # Remove null values
        if not json_val['id_project']:
            del json_val['id_project']
        if not json_val['id_site']:
            del json_val['id_site']
        else:
            if not minimal:
                json_val['site_name'] = self.service_role_site.site_name

        return json_val

    @staticmethod
    def get_service_roles(service_id: int):
        return TeraServiceRole.query.filter_by(id_service=service_id).all()

    @staticmethod
    def get_service_roles_for_site(service_id: int, site_id: int):
        return TeraServiceRole.query.filter_by(id_service=service_id, id_site=site_id).all()

    @staticmethod
    def get_specific_service_role_for_site(service_id: int, site_id: int, rolename: str):
        return TeraServiceRole.query.filter_by(id_service=service_id, id_site=site_id, service_role_name=rolename)\
            .first()

    @staticmethod
    def get_service_roles_for_project(service_id: int, project_id: int):
        return TeraServiceRole.query.filter_by(id_service=service_id, id_project=project_id).all()

    @staticmethod
    def get_specific_service_role_for_project(service_id: int, project_id: int, rolename: str):
        return TeraServiceRole.query.filter_by(id_service=service_id, id_project=project_id,
                                               service_role_name=rolename).first()

    @staticmethod
    def get_service_role_by_id(role_id: int):
        return TeraServiceRole.query.filter_by(id_service_role=role_id).first()

    @staticmethod
    def create_defaults(test=False):
        from opentera.db.models.TeraService import TeraService

        for service in TeraService.query.all():
            if service.service_key != 'OpenTeraServer':  # Don't add global roles for TeraServer
                new_role = TeraServiceRole()
                new_role.id_service = service.id_service
                new_role.service_role_name = 'admin'
                db.session.add(new_role)

                new_role = TeraServiceRole()
                new_role.id_service = service.id_service
                new_role.service_role_name = 'user'
                db.session.add(new_role)
            else:
                pass  # TODO: do what we did in Project and Site Access

        db.session.commit()
