from libtera.db.Base import db, BaseModel


class TeraSite(db.Model, BaseModel):
    __tablename__ = 't_sites'
    id_site = db.Column(db.Integer, db.Sequence('id_site_sequence'), primary_key=True, autoincrement=True)
    site_name = db.Column(db.String, nullable=False, unique=True)

    @staticmethod
    def create_defaults():
        base_site = TeraSite()
        base_site.site_name = 'Default Site'
        db.session.add(base_site)

        base_site2 = TeraSite()
        base_site2.site_name = 'Top Secret Site'
        db.session.add(base_site2)
        db.session.commit()

    @staticmethod
    def get_count():
        count = db.session.query(db.func.count(TeraSite.id_site))
        return count.first()[0]

    @staticmethod
    def get_site_by_sitename(sitename):
        return TeraSite.query.filter_by(site_name=sitename).first()
