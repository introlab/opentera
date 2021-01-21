from opentera.db.Base import db, BaseModel
from datetime import datetime
import json
import jsonschema


class TeraServiceConfig(db.Model, BaseModel):
    __tablename__ = 't_services_configs'
    id_service_config = db.Column(db.Integer, db.Sequence('id_service_config_sequence'), primary_key=True,
                                  autoincrement=True)
    id_service = db.Column(db.Integer, db.ForeignKey('t_services.id_service', ondelete='cascade'), nullable=False)
    id_user = db.Column(db.Integer, db.ForeignKey('t_users.id_user', ondelete='cascade'), nullable=True)
    id_participant = db.Column(db.Integer, db.ForeignKey('t_participants.id_participant', ondelete='cascade'),
                               nullable=True)
    id_device = db.Column(db.Integer, db.ForeignKey('t_devices.id_device', ondelete='cascade'), nullable=True)
    service_config_config = db.Column(db.String, nullable=False, default='{}')

    service_config_service = db.relationship("TeraService")
    service_config_user = db.relationship("TeraUser")
    service_config_participant = db.relationship('TeraParticipant')
    service_config_device = db.relationship('TeraDevice')
    service_config_specifics = db.relationship('TeraServiceConfigSpecific', cascade='delete')

    def to_json(self, ignore_fields=None, minimal=False, specific_id=None):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['service_config_service', 'service_config_user', 'service_config_participant',
                              'service_config_device', 'service_config_specifics'])

        if minimal:
            ignore_fields.extend([])

        json_config = super().to_json(ignore_fields=ignore_fields)

        if not minimal:
            json_config['service_config_name'] = self.service_config_service.service_name
            if self.version_id:  # No version ID can occur on temporary objects
                json_config['service_config_last_update_time'] = self.get_last_update_datetime().isoformat()
            else:
                json_config['service_config_last_update_time'] = None

        # Filter null ids
        if not self.id_user:
            del json_config['id_user']

        if not self.id_participant:
            del json_config['id_participant']

        if not self.id_device:
            del json_config['id_device']

        # Get correct config
        if specific_id and self.has_specific_config_for_specific_id(specific_id=specific_id):
            json_config['service_config_config'] = self.get_config_for_specific_id(specific_id=specific_id)
            json_config['service_config_specific_id'] = specific_id
        else:
            json_config['service_config_config'] = self.get_global_config()
            json_config['service_config_specific_id'] = None

        return json_config

    def from_json(self, json_values: dict):
        super().from_json(json=json_values, ignore_fields=['service_config_config', 'id_specific'])

        if 'service_config_config' in json_values:
            if 'id_specific' not in json_values:
                # Specifc config can't be handled here, since id_service_config might be equal to 0...
                #     self.set_config_for_specific_id(json_values['id_specific'], json_values['service_config_config'])
                # else:
                self.set_global_config(json_values['service_config_config'])

    @staticmethod
    def get_service_config_by_id(s_id: int):
        return TeraServiceConfig.query.filter_by(id_service_config=s_id).first()

    @staticmethod
    def get_service_config_for_service(service_id: int):
        return TeraServiceConfig.query.filter_by(id_service=service_id).all()

    @staticmethod
    def get_service_config_for_service_for_user(service_id: int, user_id: int):
        return TeraServiceConfig.query.filter_by(id_service=service_id, id_user=user_id).first()

    @staticmethod
    def get_service_config_for_service_for_participant(service_id: int, participant_id: int):
        return TeraServiceConfig.query.filter_by(id_service=service_id, id_participant=participant_id).first()

    @staticmethod
    def get_service_config_for_service_for_device(service_id: int, device_id: int):
        return TeraServiceConfig.query.filter_by(id_service=service_id, id_device=device_id).first()

    def has_specific_config_for_specific_id(self, specific_id: int) -> bool:
        for specific in self.service_config_specifics:
            if specific.service_config_specific_id == specific_id:
                return True
        return False

    def get_last_update_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.version_id/1000)

    def config_is_valid(self) -> bool:
        if self.service_config_config is None:
            return True  # Will use default value

        # Check if the config is a correct json format
        if isinstance(self.service_config_config, str):
            try:
                json.loads(self.service_config_config)
            except ValueError as err:
                raise err

        return True

    def get_global_config(self) -> dict:
        if self.service_config_config is None:
            return dict()

        try:
            config_json = json.loads(self.service_config_config)
        except ValueError as err:
            raise err
        return config_json

    def get_config_for_specific_id(self, specific_id: str) -> dict:
        if self.service_config_config is None:
            return dict()

        try:
            config_json = json.loads(self.service_config_config)
        except ValueError as err:
            raise err

        # No specific config at all - return global config
        if self.service_config_specifics is None or len(self.service_config_specifics) == 0:
            return config_json

        # Check if we have a specific config
        for specific in self.service_config_specifics:
            if specific.service_config_specific_id == specific_id:
                # Complete or overwrite values in current config
                try:
                    specific_config = json.loads(specific.service_config_specific_config)
                except ValueError as err:
                    raise err
                for specific_key, specific_value in specific_config.items():
                    config_json[specific_key] = specific_value

        return config_json

    def set_config_for_specific_id(self, specific_id: str, config: str):
        if isinstance(config, dict):
            try:
                config = json.dumps(config)
            except ValueError as err:
                raise err

        #  Set or update specific config
        from opentera.db.models.TeraServiceConfigSpecific import TeraServiceConfigSpecific
        TeraServiceConfigSpecific.insert_or_update_specific_config(service_config_id=self.id_service_config,
                                                                   specific_id=specific_id, config=config)

    def set_global_config(self, config: str):
        if isinstance(config, dict):
            try:
                config = json.dumps(config)
            except ValueError as err:
                raise err

        self.service_config_config = config

    @staticmethod
    def get_empty_config() -> dict:
        # return {'Globals': {}, 'Specifics': {}}
        return dict()

    def get_specific_ids_list(self) -> list:
        return [specific_config.service_config_specific_id for specific_config in self.service_config_specifics]

    @staticmethod
    def create_defaults(test=False):
        if test:
            from .TeraUser import TeraUser
            from .TeraDevice import TeraDevice
            from .TeraService import TeraService
            from .TeraParticipant import TeraParticipant
            from .TeraServiceConfigSpecific import TeraServiceConfigSpecific

            new_config = TeraServiceConfig()
            new_config.id_user = TeraUser.get_user_by_id(1).id_user
            new_config.id_service = TeraService.get_openteraserver_service().id_service
            new_config.service_config_config = '{"notification_sounds": true}'
            db.session.add(new_config)

            new_config = TeraServiceConfig()
            new_config.id_participant = TeraParticipant.get_participant_by_name('Participant #1').id_participant
            new_config.id_service = TeraService.get_service_by_key('VideoRehabService').id_service
            new_config.service_config_config = '{"default_muted": false, "view_local": true}'
            db.session.add(new_config)
            db.session.commit()

            new_specific_config = TeraServiceConfigSpecific()
            new_specific_config.id_service_config = new_config.id_service_config
            new_specific_config.service_config_specific_id = 'pc-001'
            new_specific_config.service_config_specific_config = '{"default_muted": true}'
            db.session.add(new_specific_config)

            new_specific_config = TeraServiceConfigSpecific()
            new_specific_config.id_service_config = new_config.id_service_config
            new_specific_config.service_config_specific_id = 'pc-002'
            new_specific_config.service_config_specific_config = '{"default_muted": true, "view_local": false}'
            db.session.add(new_specific_config)

            new_config = TeraServiceConfig()
            new_config.id_device = TeraDevice.get_device_by_name('Apple Watch #W05P1').id_device
            new_config.id_service = TeraService.get_service_by_key('VideoRehabService').id_service
            new_config.service_config_config = '{"delete_from_device": true}'
            db.session.add(new_config)

            db.session.commit()

    @classmethod
    def update(cls, update_id: int, values: dict):
        # Validate that the config we have is valid
        if 'service_config_config' in values:
            if 'id_specific' in values:
                # We have a specific config...
                config = TeraServiceConfig.get_service_config_by_id(values['id_service_config'])
                if not config:
                    return False

                config.set_config_for_specific_id(specific_id=values['id_specific'],
                                                  config=values['service_config_config'])
            else:
                # We have a global config...
                config = TeraServiceConfig.get_service_config_by_id(values['id_service_config'])
                if not config:
                    return False

                config.set_global_config(config=values['service_config_config'])

            if not config.config_is_valid():
                return False

            # Already updated - remove from list
            del values['service_config_config']

        super().update(update_id=update_id, values=values)
        return True

    @classmethod
    def insert(cls, db_object):
        # Validate that the config we have is valid
        try:
            config_valid = db_object.config_is_valid()
        except (ValueError, jsonschema.exceptions.ValidationError) as err:
            raise err

        if not config_valid:
            return False

        super().insert(db_object)
        return True

