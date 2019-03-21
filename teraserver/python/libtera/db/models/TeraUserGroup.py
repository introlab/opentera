from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraAccess import TeraAccess

users_usergroups_table = db.Table('t_users_usergroups', db.Column('id_user', db.Integer,
                                                                  db.ForeignKey('t_users.id_user')),
                                  db.Column('id_usergroup', db.Integer, db.ForeignKey('t_usergroups.id_usergroup')))


class TeraUserGroup(db.Model, BaseModel):
    __tablename__ = 't_usergroups'
    id_usergroup = db.Column(db.Integer, db.Sequence('id_usergroup_sequence'), primary_key=True, autoincrement=True)
    usergroup_name = db.Column(db.String(100), nullable=False, unique=True)

    usergroup_users = db.relationship("TeraUser", secondary=users_usergroups_table, back_populates="user_usergroups",
                                      cascade="all,delete")

    usergroup_access = db.relationship('TeraAccess', back_populates='access_usergroups')

    def to_json(self, ignore_fields=[]):
        if ignore_fields is None:
            ignore_fields = []
        rval = super().to_json(ignore_fields=ignore_fields)

        # Add usergroups in json format, if needed
        if 'usergroup_users' in rval:
            users_list = []
            for user in self.usergroup_users:
                users_list.append(user.to_json(ignore_fields=['user_usergroups']))
            rval['user_usergroups'] = users_list

        # Add access in json format, if needed
        if 'usergroup_access' in rval:
            access_list = []
            for access in self.usergroup_access:
                access_list.append(access.to_json(ignore_fields=['access_usergroups']))
            rval['usergroupe_access'] = access_list

        return rval

    @staticmethod
    def get_count():
        usergroups_count = db.session.query(db.func.count(TeraUserGroup.id_usergroup))
        return usergroups_count.first()[0]

    @staticmethod
    def create_default_usergroups():
        group = TeraUserGroup()
        group.usergroup_name = "Administrateurs"
        access = TeraAccess("users", True, True, True, True)
        group.usergroup_access.append(access)
        db.session.add(group)

        group = TeraUserGroup()
        group.usergroup_name = "Cliniciens"
        db.session.add(group)

        group = TeraUserGroup()
        group.usergroup_name = "Patients"
        db.session.add(group)

        group = TeraUserGroup()
        group.usergroup_name = "Users"
        db.session.add(group)


        db.session.commit()

    @staticmethod
    def get_usergroup_by_name(name):
        return TeraUserGroup.query.filter_by(usergroup_name=name).first()
