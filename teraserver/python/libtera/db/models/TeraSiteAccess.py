from libtera.db.Base import db, BaseModel


class TeraSiteAccess(db.Model, BaseModel):
    __tablename__ = 't_sites_access'
    id_site_access = db.Column(db.Integer, db.Sequence('id_site_access_sequence'), primary_key=True, autoincrement=True)
    id_sitegroup = db.Column(db.Integer, db.ForeignKey('t_sitegroups.id_sitegroup'), nullable=False)
    access_name = db.Column(db.String(100), nullable=False, unique=False)
    access_create = db.Column(db.BOOLEAN, nullable=False, default=False)
    access_update = db.Column(db.BOOLEAN, nullable=False, default=False)
    access_read = db.Column(db.BOOLEAN, nullable=False, default=False)
    access_delete = db.Column(db.BOOLEAN, nullable=False, default=False)

    access_sitegroups = db.relationship('TeraSiteGroup', back_populates='sitegroup_access')

    access_list = ['projects', 'projectgroups', 'users', 'kits', 'sessiontypes', 'tests']

    def __init__(self, name, create=False, read=False, update=False, delete=False):
        self.access_name = name
        self.set_access(create=create, update=update, read=read, delete=delete)

    def set_access(self, create=False, read=False, update=False, delete=False):
        self.access_create = create
        self.access_update = update
        self.access_read = read
        self.access_delete = delete

    def to_json(self, ignore_fields=[]):
        if ignore_fields is None:
            ignore_fields = []
        rval = super().to_json(ignore_fields=ignore_fields)

        # Add access in json format, if needed
        if 'access_sitegroups' in rval:
            access_list = []
            for group in self.access_usergroups:
                access_list.append(group.to_json(ignore_fields=['sitegroup_access']))
            rval['access_sitegroups'] = access_list

        return rval

    def __str__(self):
        return self.to_json()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraSiteAccess.id_access))
        return count.first()[0]

    @staticmethod
    def create_defaults():
        default_access = []
        for access in TeraSiteAccess.access_list:
            site_access = TeraSiteAccess(access)
            default_access.append(site_access)

        return default_access


