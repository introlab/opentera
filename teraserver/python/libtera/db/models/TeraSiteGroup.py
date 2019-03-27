from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.models.TeraSite import TeraSite

users_sitegroups_table = db.Table('t_users_sites_groups', db.Column('id_user', db.Integer,
                                                                    db.ForeignKey('t_users.id_user')),
                                  db.Column('id_sitegroup', db.Integer, db.ForeignKey('t_sites_groups.id_sitegroup')))


class TeraSiteGroup(db.Model, BaseModel):
    __tablename__ = 't_sites_groups'
    id_sitegroup = db.Column(db.Integer, db.Sequence('id_sitegroup_sequence'), primary_key=True, autoincrement=True)
    id_site = db.Column(db.Integer, db.ForeignKey('t_sites.id_site'), nullable=False)
    sitegroup_name = db.Column(db.String, nullable=False, unique=True)

    sitegroup_users = db.relationship("TeraUser", secondary=users_sitegroups_table, back_populates="user_sitegroups",
                                      cascade="all,delete")
    sitegroup_access = db.relationship('TeraSiteAccess', back_populates='access_sitegroups')

    def __str__(self):
        return '<TeraSiteGroup name="' + self.sitegroup_name + '">'

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraSiteGroup.id_sitegroup))
        return count.first()[0]

    @staticmethod
    def get_sitegroup_by_name(name):
        return TeraSiteGroup.query.filter_by(sitegroup_name=name).first()

    @staticmethod
    def create_defaults():
        admin_default_sitegroup = TeraSiteGroup()
        admin_default_sitegroup.sitegroup_name = 'Admin - Default Site'
        admin_default_sitegroup.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
        admin_default_sitegroup.sitegroup_access = TeraSiteAccess.create_defaults()
        for access in admin_default_sitegroup.sitegroup_access:
            access.set_access(True, True, True, True)
        db.session.add(admin_default_sitegroup)

        user_default_sitegroup = TeraSiteGroup()
        user_default_sitegroup.sitegroup_name = 'User - Default Site'
        user_default_sitegroup.id_site = TeraSite.get_site_by_sitename('Default Site').id_site
        user_default_sitegroup.sitegroup_access = TeraSiteAccess.create_defaults()
        for access in user_default_sitegroup.sitegroup_access:
            access.set_access(False, True, False, False)
        db.session.add(user_default_sitegroup)

        db.session.commit()

    def has_create_access(self, access_name):
        for access in self.sitegroup_access:
            if access.access_name == access_name and access.access_create:
                return True
        return False

    def has_read_access(self, access_name):
        for access in self.sitegroup_access:
            if access.access_name == access_name and access.access_read:
                return True
        return False

    def has_update_access(self, access_name):
        for access in self.sitegroup_access:
            if access.access_name == access_name and access.access_update:
                return True
        return False

    def has_delete_access(self, access_name):
        for access in self.sitegroup_access:
            if access.access_name == access_name and access.access_delete:
                return True
        return False
