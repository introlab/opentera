from libtera.db.Base import db, BaseModel
from libtera.db.models.TeraUser import TeraUser


class TeraKitDevice(db.Model, BaseModel):
    __tablename__ = 't_kits_devices'
    id_kit_device = db.Column(db.Integer, db.Sequence('id_kit_device_sequence'), primary_key=True, autoincrement=True)
    id_kit = db.Column(db.Integer, db.ForeignKey("t_kits.id_kit", ondelete='cascade'), nullable=False)
    id_device = db.Column(db.Integer, db.ForeignKey("t_devices.id_device", ondelete='cascade'), nullable=False,
                          unique=True)
    kit_device_optional = db.Column(db.Boolean, nullable=False)

    kit_device_kit = db.relationship("TeraKit")
    kit_device_device = db.relationship("TeraDevice")

    def to_json(self, ignore_fields=[], minimal=False):
        ignore_fields.extend(['kit_device_kit', 'kit_device_device'])

        if minimal:
            ignore_fields.extend([])

        # Add additional informations
        rval = super().to_json(ignore_fields=ignore_fields)
        # rval['kit_device_kit_name'] = self.kit_device_kit.kit_name
        # rval['kit_device_device_name'] = self.kit_device_device.device_name

        return rval

    @staticmethod
    def get_kit_device_by_id(kit_device_id: int):
        return TeraKitDevice.query.filter_by(id_kit_device=kit_device_id).first()

    @staticmethod
    def query_kit_device_for_kit(kit_id: int):
        return TeraKitDevice.query.filter_by(id_kit=kit_id).all()

    @staticmethod
    def query_kit_device_for_device(device_id: int):
        return TeraKitDevice.query.filter_by(id_device=device_id).all()

    @staticmethod
    def query_kit_device_for_kit_device(device_id: int, kit_id: int):
        return TeraKitDevice.query.filter_by(id_device=device_id, id_kit=kit_id).first()

    @staticmethod
    def update_kit_device(id_kit_device, values={}):
        TeraKitDevice.query.filter_by(id_kit_device=id_kit_device).update(values)
        db.session.commit()

    @staticmethod
    def insert_kit_device(kit_device):
        kit_device.id_kit_device = None

        db.session.add(kit_device)
        db.session.commit()

    @staticmethod
    def delete_kit_device(id_kit_device):
        TeraKitDevice.query.filter_by(id_kit_device=id_kit_device).delete()
        db.session.commit()
