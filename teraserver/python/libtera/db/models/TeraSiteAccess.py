from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSite import TeraSite


class TeraSiteAccess(db.Model, BaseModel):
    __tablename__ = 't_sites_access'
    id_site_access = db.Column(db.Integer, db.Sequence('id_site_access_sequence'), primary_key=True, autoincrement=True)
    id_site = db.Column(db.Integer, db.ForeignKey('t_sites.id_site'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user'), nullable=False)
    site_access_role = db.Column(db.String(100), nullable=False, unique=False)

    site_access_site = db.relationship('TeraSite')

    @staticmethod
    def get_site_role_for_user(user: TeraUser, site: TeraSite):
        if user.user_superadmin:
            # SuperAdmin is always admin.
            return 'admin'

        role = TeraSiteAccess.query.filter_by(id_user=user.id_user, id_site=site.id_site).first()
        if role is not None:
            role_name = role.site_access_role
        else:
            role_name = None
        return role_name

    @staticmethod
    def get_accessible_sites_for_user(user: TeraUser):
        if user.user_superadmin:
            site_list = TeraSite.query.all()
        else:
            site_list = []
            for site_access in user.user_sites_access:
                site_list.append(site_access.site_access_site)

        return site_list

    @staticmethod
    def get_accessible_sites_ids_for_user(user: TeraUser):
        sites_ids = []

        for site in TeraSiteAccess.get_accessible_sites_for_user(user):
            sites_ids.append(site.id_site)

        return sites_ids

    @staticmethod
    def get_sites_roles_for_user(user: TeraUser):
        sites_roles = {}

        for site in TeraSiteAccess.get_accessible_sites_for_user(user):
            sites_roles[site] = TeraSiteAccess.get_site_role_for_user(user, site)

        return sites_roles

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
    def get_count():
        count = db.session.query(db.func.count(TeraSiteAccess.id_site_access))
        return count.first()[0]

    @staticmethod
    def create_defaults():
        admin_access = TeraSiteAccess()
        admin_access.id_user = TeraUser.get_user_by_username('siteadmin').id_user
        admin_access.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
        admin_access.site_access_role = 'admin'
        db.session.add(admin_access)

        user_access = TeraSiteAccess()
        user_access.id_user = TeraUser.get_user_by_username('user').id_user
        user_access.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
        user_access.site_access_role = 'user'
        db.session.add(user_access)

        user2_access = TeraSiteAccess()
        user2_access.id_user = TeraUser.get_user_by_username('user2').id_user
        user2_access.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
        user2_access.site_access_role = 'user'
        db.session.add(user2_access)

        db.session.commit()
