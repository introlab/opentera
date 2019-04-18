from libtera.db.Base import db, BaseModel


class TeraSiteAccess(db.Model, BaseModel):
    __tablename__ = 't_sites_access'
    id_site_access = db.Column(db.Integer, db.Sequence('id_site_access_sequence'), primary_key=True, autoincrement=True)
    id_site = db.Column(db.Integer, db.ForeignKey('t_sites.id_site', ondelete='cascade'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user', ondelete='cascade'), nullable=False)
    site_access_role = db.Column(db.String(100), nullable=False, unique=False)

    site_access_site = db.relationship('TeraSite')
    site_access_user = db.relationship('TeraUser')

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['id_site_access', 'site_access_site', 'site_access_user'])
        rval = super().to_json(ignore_fields=ignore_fields)

        rval['site_name'] = self.site_access_site.site_name
        rval['user_name'] = self.site_access_user.get_fullname()
        return rval

    @staticmethod
    def build_superadmin_access_object(site_id: int, user_id: int):
        from libtera.db.models.TeraSite import TeraSite
        from libtera.db.models.TeraUser import TeraUser
        super_admin = TeraSiteAccess()
        super_admin.id_user = user_id
        super_admin.id_site = site_id
        super_admin.site_access_role = 'admin'
        super_admin.site_access_user = TeraUser.get_user_by_id(user_id)
        super_admin.site_access_site = TeraSite.get_site_by_id(site_id)

        return super_admin

    @staticmethod
    def query_access_for_site(current_user, site_id: int):
        users = current_user.get_accessible_users();
        users_ids = []
        super_admins = []
        for user in users:
            if user.id_user not in users_ids:
                users_ids.append(user.id_user)
            if user.user_superadmin:
                # Super admin access = admin in all site
                super_admin = TeraSiteAccess.build_superadmin_access_object(site_id=site_id, user_id=user.id_user)
                super_admins.append(super_admin)

        access = TeraSiteAccess.query.filter_by(id_site=site_id).filter(TeraSiteAccess.id_user.in_(users_ids)).all()

        # Add super admins to list, if needed
        for super_access in super_admins:
            if not any(x.id_user == super_access.id_user for x in access):
                access.append(super_access)

        return access

    @staticmethod
    def query_access_for_user(current_user, user_id: int):
        from libtera.db.models.TeraUser import TeraUser
        user = TeraUser.get_user_by_id(user_id)
        if not user.user_superadmin:
            access = TeraSiteAccess.query.filter_by(id_user=user_id).all()
        else:
            # User is super admin, set roles to admin for all accessible sites
            sites = current_user.get_accessible_sites()
            access = []
            for site in sites:
                access.append(TeraSiteAccess.build_superadmin_access_object(site_id=site.id_site, user_id=user_id))

        return access

    @staticmethod
    def update_site_access(id_user: int, id_site: int, rolename: str):
        # Check if access already exists
        access = TeraSiteAccess.get_specific_site_access(id_user=id_user, id_site=id_site)
        if access is None:
            # No access already present for that user and site - create new one
            return TeraSiteAccess.insert_site_access(id_user=id_user, id_site=id_site, rolename=rolename)
        else:
            # Update it
            if rolename == '':
                # No role anymore - delete it from the database
                db.session.delete(access)
            else:
                access.site_access_role = rolename

            db.session.commit()
            return access

    @staticmethod
    def insert_site_access(id_user: int, id_site: int, rolename: str):
        # No role - don't insert anything!
        if rolename == '':
            return

        new_access = TeraSiteAccess()
        new_access.site_access_role = rolename
        new_access.id_site = id_site
        new_access.id_user = id_user

        db.session.add(new_access)
        db.session.commit()

        return new_access

    @staticmethod
    def get_specific_site_access(id_user: int, id_site: int):
        access = TeraSiteAccess.query.filter_by(id_user=id_user, id_site=id_site).first()
        return access

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraSiteAccess.id_site_access))
        return count.first()[0]

    # def to_json(self, ignore_fields=[]):
    #     if ignore_fields is None:
    #         ignore_fields = []
    #     rval = super().to_json(ignore_fields=ignore_fields)
    #
    #     # Add access in json format, if needed
    #     if 'access_sitegroups' in rval:
    #         access_list = []
    #         for group in self.access_usergroups:
    #             access_list.append(group.to_json(ignore_fields=['sitegroup_access']))
    #         rval['access_sitegroups'] = access_list
    #
    #     return rval
    #
    # def __str__(self):
    #     return self.to_json()

    @staticmethod
    def create_defaults():
        pass
