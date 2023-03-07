from opentera.db.Base import BaseModel
from sqlalchemy import Column, ForeignKey, Integer, String, Sequence
from sqlalchemy.orm import relationship
from sqlalchemy.exc import IntegrityError
from opentera.db.models.TeraDevice import TeraDevice


class TeraDeviceSubType(BaseModel):

    __tablename__ = 't_devices_subtypes'
    id_device_subtype = Column(Integer, Sequence('id_device_subtype_sequence'), primary_key=True, autoincrement=True)
    id_device_type = Column(Integer, ForeignKey('t_devices_types.id_device_type', ondelete='cascade'), nullable=False)
    device_subtype_name = Column(String, nullable=False)

    device_subtype_type = relationship("TeraDeviceType")

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
            TeraDeviceSubType.db().session.add(subtype)

            subtype = TeraDeviceSubType()
            subtype.device_subtype_type = bureau
            subtype.device_subtype_name = 'Bureau modèle #2'
            TeraDeviceSubType.db().session.add(subtype)

            TeraDeviceSubType.db().session.commit()

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

    def delete_check_integrity(self) -> IntegrityError | None:
        if (TeraDevice.get_count(filters={'id_device_subtype': self.id_device_subtype})) > 0:
            return IntegrityError('Device subtype still have devices with that subtype', self.id_device_subtype,
                                  't_devices')
        return None
