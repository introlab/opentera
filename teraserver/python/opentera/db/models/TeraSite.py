from opentera.db.Base import db, BaseModel
from flask_sqlalchemy import event


class TeraSite(db.Model, BaseModel):
    __tablename__ = 't_sites'
    id_site = db.Column(db.Integer, db.Sequence('id_site_sequence'), primary_key=True, autoincrement=True)
    site_name = db.Column(db.String, nullable=False, unique=True)

    # site_devices = db.relationship("TeraDeviceSite")
    site_projects = db.relationship("TeraProject", cascade="delete", passive_deletes=True)

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['site_projects'])

        return super().to_json(ignore_fields=ignore_fields)

    def to_json_create_event(self):
        return self.to_json(minimal=True)

    def to_json_update_event(self):
        return self.to_json(minimal=True)

    def to_json_delete_event(self):
        # Minimal information, delete can not be filtered
        return {'id_site': self.id_site}

    @staticmethod
    def create_defaults(test=False):
        base_site = TeraSite()
        base_site.site_name = 'Default Site'
        TeraSite.insert(base_site)

        if test:
            base_site = TeraSite()
            base_site.site_name = 'Top Secret Site'
            TeraSite.insert(base_site)

    @staticmethod
    def get_site_by_sitename(sitename):
        return TeraSite.query.filter_by(site_name=sitename).first()

    @staticmethod
    def get_site_by_id(site_id: int):
        return TeraSite.query.filter_by(id_site=site_id).first()

    @staticmethod
    def query_data(filter_args):
        if isinstance(filter_args, tuple):
            return TeraSite.query.filter_by(*filter_args).all()
        if isinstance(filter_args, dict):
            return TeraSite.query.filter_by(**filter_args).all()
        return None

    @classmethod
    def delete(cls, id_todel):
        super().delete(id_todel)

        # from opentera.db.models.TeraSession import TeraSession
        # TeraSession.delete_orphaned_sessions()

    @classmethod
    def insert(cls, site):
        # Creates admin and user roles for that site
        super().insert(site)

        from opentera.db.models.TeraServiceRole import TeraServiceRole
        from opentera.db.models.TeraService import TeraService
        opentera_service_id = TeraService.get_openteraserver_service().id_service
        access_role = TeraServiceRole()
        access_role.id_service = opentera_service_id
        access_role.id_site = site.id_site
        access_role.service_role_name = 'admin'
        db.session.add(access_role)

        access_role = TeraServiceRole()
        access_role.id_service = opentera_service_id
        access_role.id_site = site.id_site
        access_role.service_role_name = 'user'
        db.session.add(access_role)

        db.session.commit()

#
# @event.listens_for(TeraSite, 'after_insert')
# def site_inserted(mapper, connection, target):
#     # By default, creates user and admin roles after a site has been added
#     from opentera.db.models.TeraServiceRole import TeraServiceRole
#     from opentera.db.models.TeraService import TeraService
#
#     access_role = TeraServiceRole()
#     access_role.id_service = Globals.opentera_service_id
#     access_role.id_site = target.id_site
#     access_role.service_role_name = 'admin'
#     db.session.add(access_role)
#
#     access_role = TeraServiceRole()
#     access_role.id_service = Globals.opentera_service_id
#     access_role.id_site = target.id_site
#     access_role.service_role_name = 'user'
#     db.session.add(access_role)
