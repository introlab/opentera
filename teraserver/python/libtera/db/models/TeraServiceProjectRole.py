from libtera.db.Base import db, BaseModel


class TeraServiceProjectRole(db.Model, BaseModel):
    __tablename__ = 't_services_project_roles'
    id_service_project_role = db.Column(db.Integer, db.Sequence('id_service_project_role_sequence'), primary_key=True,
                                        autoincrement=True)
    id_service = db.Column(db.Integer, db.ForeignKey('t_services.id_service', ondelete='cascade'), nullable=False)
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=False)
    id_user_group = db.Column(db.Integer, db.ForeignKey('t_users_groups.id_user_group', ondelete='cascade'),
                              nullable=True)
    id_device = db.Column(db.Integer, db.ForeignKey('t_devices.id_device', ondelete='cascade'), nullable=True)
    id_participant = db.Column(db.Integer, db.ForeignKey('t_participants.id_participant', ondelete='cascade'),
                               nullable=True)
    id_service_role = db.Column(db.Integer, db.ForeignKey('t_services_roles.id_service_role', ondelete='cascade'),
                                nullable=False)

    service_project_role_service = db.relationship("TeraService")
    service_project_role_project = db.relationship("TeraProject")
    service_project_role_role = db.relationship("TeraServiceRole")
    service_project_role_user_group = db.relationship("TeraUserGroup")
    service_project_role_device = db.relationship("TeraDevice")
    service_project_role_participant = db.relationship("TeraParticipant")

    def __init__(self):
        pass

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['service_project_role_service', 'service_project_role_project',
                              'service_project_role_role', 'service_project_role_user_group',
                              'service_project_role_device', 'service_project_role_participant'])

        if minimal:
            ignore_fields.extend([])

        json_val = super().to_json(ignore_fields=ignore_fields)

        # Remove null values
        if not json_val['id_device']:
            del json_val['id_device']
        if not json_val['id_participant']:
            del json_val['id_participant']
        if not json_val['id_user_group']:
            del json_val['id_user_group']

        # Complete information if not minimal
        if not minimal:
            if self.service_project_role_service:
                json_val['service_name'] = self.service_project_role_service.service_name
            else:
                # This happens on transient objects
                from libtera.db.models.TeraService import TeraService
                service = TeraService.get_service_by_id(self.id_service)
                if service:
                    json_val['service_name'] = service.service_name
            if self.id_user_group:
                if self.service_project_role_user_group:
                    json_val['user_group_name'] = self.service_project_role_user_group.user_group_name
                else:
                    # This happens on transient objects
                    from libtera.db.models.TeraUserGroup import TeraUserGroup
                    ug = TeraUserGroup.get_user_group_by_id(self.id_user_group)
                    if ug:
                        json_val['user_group_name'] = ug.user_group_name
            if self.id_device:
                json_val['device_name'] = self.service_project_role_device.device_name
            if self.id_participant:
                json_val['participant_name'] = self.service_project_role_participant.participant_name
        return json_val

    @staticmethod
    def get_service_project_role_by_id(service_project_role_id: int):
        return TeraServiceProjectRole.query.filter_by(id_service_project_role=service_project_role_id).first()

    @staticmethod
    def create_defaults():
        from libtera.db.models.TeraService import TeraService
        from libtera.db.models.TeraProject import TeraProject
        from libtera.db.models.TeraUserGroup import TeraUserGroup

        project1 = TeraProject.get_project_by_projectname('Default Project #1')
        project2 = TeraProject.get_project_by_projectname('Default Project #2')

        servicebureau = TeraService.get_service_by_key('BureauActif')
        servicebureauadmin = servicebureau.service_roles[0]
        serviceviddispatch = TeraService.get_service_by_key('VideoDispatch')
        serviceviddispatchadmin = serviceviddispatch.service_roles[0]

        user_group1 = TeraUserGroup.get_user_group_by_group_name('Users - Project 1')
        user_group2 = TeraUserGroup.get_user_group_by_group_name('Admins - Project 1')

        service_role = TeraServiceProjectRole()
        service_role.id_user_group = user_group1.id_user_group
        service_role.id_project = project1.id_project
        service_role.id_service = servicebureau.id_service
        service_role.id_service_role = servicebureauadmin.id_service_role
        db.session.add(service_role)

        service_role = TeraServiceProjectRole()
        service_role.id_user_group = user_group2.id_user_group
        service_role.id_project = project1.id_project
        service_role.id_service = serviceviddispatch.id_service
        service_role.id_service_role = serviceviddispatchadmin.id_service_role
        db.session.add(service_role)

        db.session.commit()
