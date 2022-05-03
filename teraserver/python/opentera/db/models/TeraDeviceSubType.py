from opentera.db.Base import db, BaseModel


class TeraDeviceSubType(db.Model, BaseModel):

    __tablename__ = 't_devices_subtypes'
    id_device_subtype = db.Column(db.Integer, db.Sequence('id_device_subtype_sequence'), primary_key=True,
                                  autoincrement=True)
    id_device_type = db.Column(db.Integer, db.ForeignKey('t_devices_types.id_device_type', ondelete='cascade'),
                               nullable=False)
    device_subtype_name = db.Column(db.String, nullable=False)

    device_subtype_type = db.relationship("TeraDeviceType")

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields += ['device_subtype_type']

        device_subtype_json = super().to_json(ignore_fields=ignore_fields)

        # Add device type name as parent
        device_subtype_json['device_subtype_parent'] = self.device_subtype_type.device_type_name

        return device_subtype_json

    @staticmethod
    def create_defaults(test=False):
        if test:
            from opentera.db.models.TeraDeviceType import TeraDeviceType
            bureau = TeraDeviceType.get_device_type_by_key('bureau_actif')
            subtype = TeraDeviceSubType()
            subtype.device_subtype_type = bureau
            subtype.device_subtype_name = 'Bureau modèle #1'
            db.session.add(subtype)

            subtype = TeraDeviceSubType()
            subtype.device_subtype_type = bureau
            subtype.device_subtype_name = 'Bureau modèle #2'
            db.session.add(subtype)

            db.session.commit()

    @staticmethod
    def get_devices_subtypes():
        return TeraDeviceSubType.query.all()

    @staticmethod
    def get_device_subtype(dev_subtype: int):
        return TeraDeviceSubType.query.filter_by(id_device_subtype=dev_subtype).first()

    @staticmethod
    def get_device_subtype_by_id(dev_subtype: int):
        return TeraDeviceSubType.query.filter_by(id_device_subtype=dev_subtype).first()

    @staticmethod
    def get_device_subtypes_for_type(dev_type: int):
        return TeraDeviceSubType.query.filter_by(id_device_type=dev_type).all()

