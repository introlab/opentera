from libtera.db.Base import db, BaseModel


class TeraAccess(db.Model, BaseModel):
    __tablename__ = 't_access'
    id_access = db.Column(db.Integer, db.Sequence('id_access_sequence'), primary_key=True, autoincrement=True)
    id_usergroup = db.Column(db.Integer, db.ForeignKey('t_usergroups.id_usergroup'), nullable=False)
    access_name = db.Column(db.String(100), nullable=False, unique=True)
    access_create = db.Column(db.BOOLEAN, nullable=False, default=False)
    access_update = db.Column(db.BOOLEAN, nullable=False, default=False)
    access_read = db.Column(db.BOOLEAN, nullable=False, default=False)
    access_delete = db.Column(db.BOOLEAN, nullable=False, default=False)

    access_usergroups = db.relationship('TeraUserGroup', back_populates='usergroup_access')

    def __init__(self, name, create=False, update=False, read=False, delete=False):
        self.access_name = name
        self.access_create = create
        self.access_update = update
        self.access_read = read
        self.access_delete = delete

    def to_json(self, ignore_fields=[]):
        if ignore_fields is None:
            ignore_fields = []
        rval = super().to_json(ignore_fields=ignore_fields)

        # Add access in json format, if needed
        if 'access_usergroups' in rval:
            access_list = []
            for group in self.access_usergroups:
                access_list.append(group.to_json(ignore_fields=['usergroups_access']))
            rval['user_usergroups'] = access_list

        return rval

    def __str__(self):
        return self.to_json()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraAccess.id_access))
        return count.first()[0]

