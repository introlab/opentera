from libtera.db.Base import db, BaseModel


class TeraProjectAccess(db.Model, BaseModel):
    __tablename__ = 't_projects_access'
    id_project_access = db.Column(db.Integer, db.Sequence('id_project_access_sequence'), primary_key=True,
                                  autoincrement=True)
    id_project = db.Column(db.Integer, db.ForeignKey('t_projects.id_project', ondelete='cascade'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user', ondelete='cascade'), nullable=False)
    project_access_role = db.Column(db.String(100), nullable=False, unique=False)

    project_access_project = db.relationship('TeraProject')
    project_access_user = db.relationship('TeraUser')

    def __init__(self):
        self.project_access_inherited = False

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []
        ignore_fields.extend(['id_project_access', 'project_access_project', 'project_access_user'])
        rval = super().to_json(ignore_fields=ignore_fields)

        rval['project_name'] = self.project_access_project.project_name
        rval['user_name'] = self.project_access_user.get_fullname()
        return rval

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraProjectAccess.id_project_access))
        return count.first()[0]

    @staticmethod
    def build_superadmin_access_object(project_id: int, user_id: int):
        from libtera.db.models.TeraProject import TeraProject
        from libtera.db.models.TeraUser import TeraUser
        super_admin = TeraProjectAccess()
        super_admin.id_user = user_id
        super_admin.id_project = project_id
        super_admin.project_access_role = 'admin'
        super_admin.project_access_inherited = True
        super_admin.project_access_user = TeraUser.get_user_by_id(user_id)
        super_admin.project_access_project = TeraProject.get_project_by_id(project_id)
        return super_admin

    @staticmethod
    def update_project_access(id_user: int, id_project: int, rolename: str):
        # Check if access already exists
        access = TeraProjectAccess.get_specific_project_access(id_user=id_user, id_project=id_project)
        if access is None:
            # No access already present for that user and site - create new one
            return TeraProjectAccess.insert_project_access(id_user=id_user, id_project=id_project, rolename=rolename)
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
    def insert_project_access(id_user: int, id_project: int, rolename: str):
        # No role - don't insert anything!
        if rolename == '':
            return

        new_access = TeraProjectAccess()
        new_access.project_access_role = rolename
        new_access.id_project = id_project
        new_access.id_user = id_user

        db.session.add(new_access)
        db.session.commit()

        return new_access

    @staticmethod
    def get_specific_project_access(id_user: int, id_project: int):
        access = TeraProjectAccess.query.filter_by(id_user=id_user, id_project=id_project).first()
        return access

    @staticmethod
    def create_defaults():
        pass
