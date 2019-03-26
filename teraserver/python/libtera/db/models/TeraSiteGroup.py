from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.models.TeraSite import TeraSite

users_sitegroups_table = db.Table('t_users_sitegroups', db.Column('id_user', db.Integer,
                                                                  db.ForeignKey('t_users.id_user')),
                                  db.Column('id_sitegroup', db.Integer, db.ForeignKey('t_sitegroups.id_sitegroup')))


class TeraSiteGroup(db.Model, BaseModel):
    __tablename__ = 't_sitegroups'
    id_sitegroup = db.Column(db.Integer, db.Sequence('id_sitegroup_sequence'), primary_key=True, autoincrement=True)
    id_site = db.Column(db.Integer, db.ForeignKey('t_sites.id_site'), nullable=False)
    sitegroup_name = db.Column(db.String, nullable=False, unique=True)

    sitegroup_users = db.relationship("TeraUser", secondary=users_sitegroups_table, back_populates="user_sitegroups",
                                      cascade="all,delete")
    sitegroup_access = db.relationship('TeraSiteAccess', back_populates='access_sitegroups')

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

