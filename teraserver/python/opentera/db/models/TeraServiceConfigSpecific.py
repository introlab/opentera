from opentera.db.Base import db, BaseModel
from datetime import datetime
import json
import jsonschema


class TeraServiceConfigSpecific(db.Model, BaseModel):
    __tablename__ = 't_services_configs_specifics'
    id_service_config_specific = db.Column(db.Integer, db.Sequence('id_service_config_specific_sequence'),
                                           primary_key=True, autoincrement=True)
    id_service_config = db.Column(db.Integer, db.ForeignKey('t_services_configs.id_service_config', ondelete='cascade'),
                                  nullable=False)
    service_config_specific_id = db.Column(db.String, nullable=False)
    service_config_specific_config = db.Column(db.String, nullable=False)

    service_config_specific_service_config = db.relationship("TeraServiceConfig")

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['service_config_specific_service_config'])

        if minimal:
            ignore_fields.extend([])

        json_config = super().to_json(ignore_fields=ignore_fields)

        return json_config

    @staticmethod
    def get_service_config_specific_by_id(s_id: int):
        return TeraServiceConfigSpecific.query.filter_by(id_service_config_specific=s_id).first()

    @staticmethod
    def get_service_config_specifics_for_service_config(service_config_id: int):
        return TeraServiceConfigSpecific.query.filter_by(id_service_config=service_config_id).all()

    def get_last_update_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.version_id/1000)

    @staticmethod
    def insert_or_update_specific_config(service_config_id: int, specific_id: str, config: str):
        # Check if we have an existing specific config for that service_config
        configs = TeraServiceConfigSpecific.get_service_config_specifics_for_service_config(service_config_id)
        insertion = True

        if configs:
            for s_config in configs:
                if s_config.service_config_specific_id == specific_id:
                    # Update
                    s_config.service_config_specific_config = config
                    insertion = False
                    break
        if insertion:
            # Insert
            new_specific_config = TeraServiceConfigSpecific()
            new_specific_config.id_service_config = service_config_id
            new_specific_config.service_config_specific_id = specific_id
            new_specific_config.service_config_specific_config = config
            db.session.add(new_specific_config)
        db.session.commit()
