from libtera.db.Base import db, BaseModel


class TeraProjectAccess(db.Model, BaseModel):
    __tablename__ = 't_projects_access'
    id_project_access = db.Column(db.Integer, db.Sequence('id_project_access_sequence'), primary_key=True,
                                  autoincrement=True)
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=False)
    id_user_group = db.Column(db.Integer, db.ForeignKey('t_users_groups.id_user_group', ondelete='cascade'),
                              nullable=False)
    project_access_role = db.Column(db.String(100), nullable=False, unique=False)

    project_access_project = db.relationship('TeraProject')
    project_access_user_group = db.relationship('TeraUserGroup')

    def __init__(self):
        self.project_access_inherited = False

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['id_project_access', 'project_access_project', 'project_access_user_group'])
        rval = super().to_json(ignore_fields=ignore_fields)

        rval['project_name'] = self.project_access_project.project_name
        if self.project_access_user_group:
            rval['user_group_name'] = self.project_access_user_group.user_group_name
        else:
            rval['user_group_name'] = None
        return rval

    @staticmethod
    def build_user_access_object(project_id: int, user_group_id: int, role: str):
        from libtera.db.models.TeraProject import TeraProject
        from libtera.db.models.TeraUserGroup import TeraUserGroup
        user_access = TeraProjectAccess()
        user_access.id_user_group = user_group_id
        user_access.id_project = project_id
        user_access.project_access_role = role
        user_access.project_access_inherited = True
        user_access.project_access_user_group = TeraUserGroup.get_user_group_by_id(user_group_id)
        user_access.project_access_project = TeraProject.get_project_by_id(project_id)
        return user_access

    @staticmethod
    def update_project_access(id_user_group: int, id_project: int, rolename: str):
        # Check if access already exists
        access = TeraProjectAccess.get_specific_project_access(id_user_group=id_user_group, id_project=id_project)
        if access is None:
            # No access already present for that user and site - create new one
            return TeraProjectAccess.insert_project_access(id_user_group=id_user_group, id_project=id_project,
                                                           rolename=rolename)
        else:
            # Update it
            if rolename == '':
                # No role anymore - delete it from the database
                db.session.delete(access)
            else:
                access.project_access_role = rolename

            db.session.commit()
            return access

    @staticmethod
    def insert_project_access(id_user_group: int, id_project: int, rolename: str):
        # No role - don't insert anything!
        if rolename == '':
            return

        new_access = TeraProjectAccess()
        new_access.project_access_role = rolename
        new_access.id_project = id_project
        new_access.id_user_group = id_user_group

        db.session.add(new_access)
        db.session.commit()

        return new_access

    @staticmethod
    def get_specific_project_access(id_user_group: int, id_project: int):
        access = TeraProjectAccess.query.filter_by(id_user=id_user_group, id_project=id_project).first()
        return access

    @staticmethod
    def get_projects_access_for_user_group(id_user_group: int):
        return TeraProjectAccess.query.filter_by(id_user_group=id_user_group).all()

    @staticmethod
    def get_projects_access_for_project(project_id: int):
        return TeraProjectAccess.query.filter_by(id_project=project_id).all()

    @staticmethod
    def get_project_access_by_id(project_access_id: int):
        return TeraProjectAccess.query.filter_by(id_project_access=project_access_id).first()

    @staticmethod
    def create_defaults():
        pass
