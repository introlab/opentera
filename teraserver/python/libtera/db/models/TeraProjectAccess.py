from libtera.db.Base import db, BaseModel


class TeraProjectAccess(db.Model, BaseModel):
    __tablename__ = 't_projects_access'
    id_project_access = db.Column(db.Integer, db.Sequence('id_project_access_sequence'), primary_key=True,
                                  autoincrement=True)
    id_projectgroup = db.Column(db.Integer, db.ForeignKey('t_projectgroups.id_projectgroup'), nullable=False)
    access_name = db.Column(db.String(100), nullable=False, unique=False)
    access_create = db.Column(db.BOOLEAN, nullable=False, default=False)
    access_update = db.Column(db.BOOLEAN, nullable=False, default=False)
    access_read = db.Column(db.BOOLEAN, nullable=False, default=False)
    access_delete = db.Column(db.BOOLEAN, nullable=False, default=False)

    access_projectgroups = db.relationship('TeraProjectGroup', back_populates='projectgroup_access')

    access_list = ['users', 'kits', 'sessions', 'tests', 'participants', 'participantgroups']

    def __init__(self, name, create=False, read=False, update=False, delete=False):
        self.access_name = name
        self.set_access(create=create, update=update, read=read, delete=delete)

    def set_access(self, create=False, read=False, update=False, delete=False):
        self.access_create = create
        self.access_update = update
        self.access_read = read
        self.access_delete = delete

    @staticmethod
    def create_defaults():
        default_access = []
        for access in TeraProjectAccess.access_list:
            proj_access = TeraProjectAccess(access)
            default_access.append(proj_access)

        return default_access
