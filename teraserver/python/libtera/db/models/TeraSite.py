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

    @staticmethod
    def get_site_by_id(site_id):
        return TeraSite.query.filter_by(id_site=site_id).first()

    @staticmethod
    def query_site_by_id(current_user, site_id: int):
        sites_ids = current_user.get_accessible_sites_ids()
        site = None

        if site_id in sites_ids:
            site = TeraSite.get_site_by_id(site_id)

        return site

    @staticmethod
    def query_data(filter_args):
        if isinstance(filter_args, tuple):
            return TeraSite.query.filter_by(*filter_args).all()
        if isinstance(filter_args, dict):
            return TeraSite.query.filter_by(**filter_args).all()
        return None

    @staticmethod
    def update_site(id_site, values={}):
        TeraSite.query.filter_by(id_site=id_site).update(values)
        db.session.commit()

    @staticmethod
    def insert_site(site):
        site.id_site = None

        db.session.add(site)
        db.session.commit()

    @staticmethod
    def delete_site(id_site):
        TeraSite.query.filter_by(id_site=id_site).delete()
        db.session.commit()
