from libtera.db.Base import db, BaseModel


class TeraServiceProjectRole(db.Model, BaseModel):
    __tablename__ = 't_services_project_roles'
    id_service_project_role = db.Column(db.Integer, db.Sequence('id_service_project_role_sequence'), primary_key=True,
                                        autoincrement=True)
    id_service = db.Column(db.Integer, db.ForeignKey('t_services.id_service', ondelete='cascade'), nullable=False)
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user', ondelete='cascade'), nullable=True)
    id_device = db.Column(db.Integer, db.ForeignKey('t_devices.id_device', ondelete='cascade'), nullable=True)
    id_participant = db.Column(db.Integer, db.ForeignKey('t_participants.id_participant', ondelete='cascade'),
                               nullable=True)
    id_service_role = db.Column(db.Integer, db.ForeignKey('t_services_roles.id_service_role', ondelete='cascade'),
                                nullable=False)

    service_project_role_service = db.relationship("TeraService")
    service_project_role_project = db.relationship("TeraProject")
    service_project_role_role = db.relationship("TeraServiceRole")
    service_project_role_user = db.relationship("TeraUser")
    service_project_role_device = db.relationship("TeraDevice")
    service_project_role_participant = db.relationship("TeraParticipant")

    def __init__(self):
        pass

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['service_project_role_service', 'service_project_role_project',
                              'service_project_role_role', 'service_project_role_user', 'service_project_role_device',
                              'service_project_role_participant'])

        if minimal:
            ignore_fields.extend([])

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def create_defaults():
        from libtera.db.models.TeraService import TeraService
        from libtera.db.models.TeraProject import TeraProject
        from libtera.db.models.TeraUser import TeraUser

        project1 = TeraProject.get_project_by_projectname('Default Project #1')
        project2 = TeraProject.get_project_by_projectname('Default Project #2')

        servicebureau = TeraService.get_service_by_key('BureauActif')
        servicebureauadmin = servicebureau.service_roles[0]
        serviceviddispatch = TeraService.get_service_by_key('VideoDispatch')
        serviceviddispatchadmin = serviceviddispatch.service_roles[0]

        user = TeraUser.get_user_by_username('user')

        service_role = TeraServiceProjectRole()
        service_role.id_user = user.id_user
        service_role.id_project = project1.id_project
        service_role.id_service = servicebureau.id_service
        service_role.id_service_role = servicebureauadmin.id_service_role
        db.session.add(service_role)

        service_role = TeraServiceProjectRole()
        service_role.id_user = user.id_user
        service_role.id_project = project2.id_project
        service_role.id_service = serviceviddispatch.id_service
        service_role.id_service_role = serviceviddispatchadmin.id_service_role
        db.session.add(service_role)

        db.session.commit()
