from libtera.db.Base import db, BaseModel


class TeraKit(db.Model, BaseModel):
    __tablename__ = 't_kits'
    id_kit = db.Column(db.Integer, db.Sequence('id_kit_sequence'),
                       primary_key=True, autoincrement=True)

