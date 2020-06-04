from libtera.db.Base import db, BaseModel


class TeraServiceRole(db.Model, BaseModel):
    __tablename__ = 't_services_roles'
    id_service_role = db.Column(db.Integer, db.Sequence('id_service_role_sequence'), primary_key=True,
                                autoincrement=True)
    id_service = db.Column(db.Integer, db.ForeignKey('t_services.id_service', ondelete='cascade'), nullable=False)
    service_role_name = db.Column(db.String(100), nullable=False)

    service_role_service = db.relationship("TeraService")

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

        ignore_fields.extend(['service_role_service'])

        if minimal:
            ignore_fields.extend([])

        return super().to_json(ignore_fields=ignore_fields)

    @staticmethod
    def get_service_roles(service_id: int):
        return TeraServiceRole.query.filter_by(id_service=service_id).all()

    @staticmethod
    def get_service_role_by_id(role_id: int):
        return TeraServiceRole.query.filter_by(id_service_role=role_id).first()

    @staticmethod
    def create_defaults():
        from libtera.db.models.TeraService import TeraService

        for service in TeraService.query.all():
            new_role = TeraServiceRole()
            new_role.id_service = service.id_service
            new_role.service_role_name = 'admin'
            db.session.add(new_role)

            new_role = TeraServiceRole()
            new_role.id_service = service.id_service
            new_role.service_role_name = 'user'
            db.session.add(new_role)

        db.session.commit()
