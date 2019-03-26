from libtera.db.Base import db, BaseModel

users_projectgroups_table = db.Table('t_users_projectgroups', db.Column('id_user', db.Integer,
                                                                        db.ForeignKey('t_users.id_user')),
                                     db.Column('id_projectgroup', db.Integer,
                                               db.ForeignKey('t_projectgroups.id_projectgroup')))


class TeraProjectGroup(db.Model, BaseModel):
    __tablename__ = 't_projectgroups'
    id_projectgroup = db.Column(db.Integer, db.Sequence('id_projectgroup_sequence'), primary_key=True,
                                autoincrement=True)
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project'), nullable=False)
    projectgroup_name = db.Column(db.String, nullable=False, unique=False)

    projectgroup_users = db.relationship("TeraUser", secondary=users_projectgroups_table,
                                         back_populates="user_projectgroups", cascade="all,delete")
    projectgroup_access = db.relationship('TeraProjectAccess', back_populates='access_projectgroups')

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraProjectGroup.id_projectgroup))
        return count.first()[0]
