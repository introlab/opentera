from libtera.db.Base import db, BaseModel

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
