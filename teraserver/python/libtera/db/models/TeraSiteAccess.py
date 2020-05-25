from libtera.db.Base import db, BaseModel


class TeraSiteAccess(db.Model, BaseModel):
    __tablename__ = 't_sites_access'
    id_site_access = db.Column(db.Integer, db.Sequence('id_site_access_sequence'), primary_key=True, autoincrement=True)
    id_site = db.Column(db.Integer, db.ForeignKey('t_sites.id_site', ondelete='cascade'), nullable=False)
    id_user_group = db.Column(db.Integer, db.ForeignKey('t_users_groups.id_user_group', ondelete='cascade'),
                              nullable=False)
    site_access_role = db.Column(db.String(100), nullable=False, unique=False)

    site_access_site = db.relationship('TeraSite')
    site_access_user_group = db.relationship('TeraUserGroup')

    def __init__(self):
        self.site_access_inherited = False

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['id_site_access', 'site_access_site', 'site_access_user_group'])
        rval = super().to_json(ignore_fields=ignore_fields)

        rval['site_name'] = self.site_access_site.site_name
        if self.site_access_user_group:
            rval['user_group_name'] = self.site_access_user_group.user_group_name
        else:
            rval['user_group_name'] = None
        return rval

    @staticmethod
    def build_user_access_object(site_id: int, user_group_id: int, role: str):
        from libtera.db.models.TeraSite import TeraSite
        from libtera.db.models.TeraUserGroup import TeraUserGroup
        user_access = TeraSiteAccess()
        user_access.id_user_group = user_group_id
        user_access.id_site = site_id
        user_access.site_access_role = role
        user_access.site_access_inherited = True
        user_access.site_access_user_group = TeraUserGroup.get_user_group_by_id(user_group_id)
        user_access.site_access_site = TeraSite.get_site_by_id(site_id)
        return user_access

    @staticmethod
    def update_site_access(id_user_group: int, id_site: int, rolename: str):
        # Check if access already exists
        access = TeraSiteAccess.get_specific_site_access(id_user_group=id_user_group, id_site=id_site)
        if access is None:
            # No access already present for that user and site - create new one
            return TeraSiteAccess.insert_site_access(id_user_group=id_user_group, id_site=id_site, rolename=rolename)
        else:
            # Update it
            if rolename == '':
                # No role anymore - delete it from the database
                db.session.delete(access)
                db.session.commit()
                return None
            else:
                access.site_access_role = rolename

            db.session.commit()
            return access

    @staticmethod
    def insert_site_access(id_user_group: int, id_site: int, rolename: str):
        # No role - don't insert anything!
        if rolename == '':
            return

        new_access = TeraSiteAccess()
        new_access.site_access_role = rolename
        new_access.id_site = id_site
        new_access.id_user_group = id_user_group

        db.session.add(new_access)
        db.session.commit()

        return new_access

    @staticmethod
    def get_specific_site_access(id_user_group: int, id_site: int):
        access = TeraSiteAccess.query.filter_by(id_user_group=id_user_group, id_site=id_site).first()
        return access

    @staticmethod
    def get_sites_access_for_user_group(id_user_group: int):
        return TeraSiteAccess.query.filter_by(id_user_group=id_user_group).all()

    @staticmethod
    def get_sites_access_for_site(id_site: int):
        return TeraSiteAccess.query.filter_by(id_site=id_site).all()

    @staticmethod
    def create_defaults():
        pass
