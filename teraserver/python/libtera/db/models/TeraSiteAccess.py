from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraSite import TeraSite


class TeraSiteAccess(db.Model, BaseModel):
    __tablename__ = 't_sites_access'
    id_site_access = db.Column(db.Integer, db.Sequence('id_site_access_sequence'), primary_key=True, autoincrement=True)
    id_site = db.Column(db.Integer, db.ForeignKey('t_sites.id_site'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user'), nullable=False)
    site_access_role = db.Column(db.String(100), nullable=False, unique=False)

    site_access_site = db.relationship('TeraSite')

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraSiteAccess.id_site_access))
        return count.first()[0]

    # def to_json(self, ignore_fields=[]):
    #     if ignore_fields is None:
    #         ignore_fields = []
    #     rval = super().to_json(ignore_fields=ignore_fields)
    #
    #     # Add access in json format, if needed
    #     if 'access_sitegroups' in rval:
    #         access_list = []
    #         for group in self.access_usergroups:
    #             access_list.append(group.to_json(ignore_fields=['sitegroup_access']))
    #         rval['access_sitegroups'] = access_list
    #
    #     return rval
    #
    # def __str__(self):
    #     return self.to_json()

    @staticmethod
    def create_defaults():
        pass
