from libtera.db.Base import db, BaseModel


class TeraSite(db.Model, BaseModel):
    __tablename__ = 't_sites'
    id_site = db.Column(db.Integer, db.Sequence('id_site_sequence'), primary_key=True, autoincrement=True)
    site_name = db.Column(db.String, nullable=False, unique=True)

