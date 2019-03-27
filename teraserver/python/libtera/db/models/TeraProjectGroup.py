from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraProject import TeraProject
from libtera.db.models.TeraProjectAccess import TeraProjectAccess

users_projectgroups_table = db.Table('t_users_projects_groups', db.Column('id_user', db.Integer,
                                                                        db.ForeignKey('t_users.id_user')),
                                     db.Column('id_projectgroup', db.Integer,
                                               db.ForeignKey('t_projects_groups.id_projectgroup')))


class TeraProjectGroup(db.Model, BaseModel):
    __tablename__ = 't_projects_groups'
    id_projectgroup = db.Column(db.Integer, db.Sequence('id_projectgroup_sequence'), primary_key=True,
                                autoincrement=True)
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project'), nullable=False)
    projectgroup_name = db.Column(db.String, nullable=False, unique=False)

    projectgroup_users = db.relationship("TeraUser", secondary=users_projectgroups_table,
                                         back_populates="user_projectgroups", cascade="all,delete")
    projectgroup_access = db.relationship('TeraProjectAccess', back_populates='access_projectgroups')

    def __str__(self):
        return '<TeraProjectGroup name="' + self.projectgroup_name + '">'

    def __repr__(self):
        return self.__str__()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraProjectGroup.id_projectgroup))
        return count.first()[0]

    @staticmethod
    def get_projectgroup_by_name(name):
        return TeraProjectGroup.query.filter_by(projectgroup_name=name).first()

    @staticmethod
    def create_defaults():
        admin_default_projgroup = TeraProjectGroup()
        admin_default_projgroup.projectgroup_name = 'Admin - Default Project #1'
        admin_default_projgroup.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
        admin_default_projgroup.projectgroup_access = TeraProjectAccess.create_defaults()
        for access in admin_default_projgroup.projectgroup_access:
            access.set_access(True, True, True, True)
        db.session.add(admin_default_projgroup)

        user_default_projgroup = TeraProjectGroup()
        user_default_projgroup.projectgroup_name = 'User - Default Project #1'
        user_default_projgroup.id_project = TeraProject.get_project_by_projectname('Default Project #1').id_project
        user_default_projgroup.projectgroup_access = TeraProjectAccess.create_defaults()
        for access in user_default_projgroup.projectgroup_access:
            access.set_access(False, True, False, False)
        db.session.add(user_default_projgroup)

        user_default_projgroup2 = TeraProjectGroup()
        user_default_projgroup2.projectgroup_name = 'User - Default Project #2'
        user_default_projgroup2.id_project = TeraProject.get_project_by_projectname('Default Project #2').id_project
        user_default_projgroup2.projectgroup_access = TeraProjectAccess.create_defaults()
        for access in user_default_projgroup2.projectgroup_access:
            access.set_access(False, False, False, False)
        db.session.add(user_default_projgroup2)

        db.session.commit()

    def has_create_access(self, access_name):
        for access in self.projectgroup_access:
            if access.access_name == access_name and access.access_create:
                return True
        return False

    def has_read_access(self, access_name):
        for access in self.projectgroup_access:
            if access.access_name == access_name and access.access_read:
                return True
        return False

    def has_update_access(self, access_name):
        for access in self.projectgroup_access:
            if access.access_name == access_name and access.access_update:
                return True
        return False

    def has_delete_access(self, access_name):
        for access in self.projectgroup_access:
            if access.access_name == access_name and access.access_delete:
                return True
        return False
