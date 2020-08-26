from libtera.db.Base import db, BaseModel
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

    # Typical service config format is:
    # { Globals: {
    #               ---- Put "default" config values here with format:
    #               {name: value, .... }
    #            },
    #   Specifics: [
    #                   {
    #                       xxxx, # Specific id of that config, for example hardware ID
    #                       ---- Put "overriden" config values here for that config id
    #                   },
    #                   {
    #                       xxxx, # Specific id of that config, for example hardware ID
    #                       ---- Put "overriden" config values here for that config id
    #                   }, ...
    #              ]
    # }
    service_config_config = db.Column(db.String, nullable=False, default='{"Globals": {}}')

    service_config_service = db.relationship("TeraService")
    service_config_user = db.relationship("TeraUser")
    service_config_participant = db.relationship('TeraParticipant')
    service_config_device = db.relationship('TeraDevice')

    def to_json(self, ignore_fields=None, minimal=False, specific_id=None, raw_config=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['service_config_service', 'service_config_user', 'service_config_participant',
                              'service_config_device'])

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

        # Generate correct config - hides Globals and Specifics if now requesting "raw" config
        if not raw_config:
            if specific_id:
                json_config['service_config_config'] = self.get_config_for_specific_id(specific_id=specific_id)
            else:
                json_config['service_config_config'] = self.get_global_config()

        return json_config

    def from_json(self, json_values: dict):
        super().from_json(json=json_values, ignore_fields=['service_config_config'])

        if 'service_config_config' in json_values:
            if 'id_specific' in json_values:
                self.set_config_for_specific_id(json_values['id_specific'], json_values['service_config_config'])
            else:
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

    def get_last_update_datetime(self) -> datetime:
        return datetime.fromtimestamp(self.version_id/1000)

    def config_is_valid(self) -> bool:
        if self.service_config_config is None:
            return True  # Will use default value

        if isinstance(self.service_config_config, str):
            try:
                config_json = json.loads(self.service_config_config)
            except ValueError as err:
                raise err
        else:
            config_json = self.service_config_config

        # Minimum required fields is "Globals"
        if 'Globals' not in config_json:
            return False

        # Validate that we have a match for the "Globals" config with the expected service schema
        # try:
        #     schema_json = json.loads(self.service_config_service.service_config_schema)
        #     jsonschema.validate(instance=config_json['Globals'], schema=schema_json)
        # except (ValueError, jsonschema.exceptions.ValidationError) as err:
        #     raise err

        if 'Specifics' in config_json:
            # Ensure we have an "id" in each of specifics items
            for specific_config in config_json['Specifics']:
                if not isinstance(config_json['Specifics'][specific_config], dict):
                    return False

        return True

    def get_global_config(self) -> dict:
        if self.service_config_config is None:
            return dict()

        try:
            config_json = json.loads(self.service_config_config)
        except ValueError as err:
            raise err
        return config_json['Globals']

    def get_config_for_specific_id(self, specific_id: str) -> dict:
        if self.service_config_config is None:
            return dict()

        try:
            config_json = json.loads(self.service_config_config)
        except ValueError as err:
            raise err

        # Get "Globals" config as base
        current_config = config_json['Globals']

        # Check if we have a specific config
        if 'Specifics' in config_json:
            for specific in config_json['Specifics']:
                if specific == specific_id:
                    # Complete or overwrite values in current config
                    for specific_key, specific_value in config_json['Specifics'][specific].items():
                        current_config[specific_key] = specific_value

        return current_config

    def set_config_for_specific_id(self, specific_id: str, config: str):
        try:
            config_json = json.loads(self.service_config_config)
        except ValueError as err:
            raise err
        except TypeError:
            config_json = self.get_empty_config()

        config_json['Specifics'][specific_id] = config

        try:
            self.service_config_config = json.dumps(config_json)
        except ValueError as err:
            raise err

    def set_global_config(self, config: str):
        try:
            config_json = json.loads(self.service_config_config)
        except ValueError as err:
            raise err
        except TypeError:
            config_json = self.get_empty_config()

        config_json['Globals'] = config

        try:
            self.service_config_config = json.dumps(config_json)
        except ValueError as err:
            raise err

    @staticmethod
    def get_empty_config() -> dict:
        return {'Globals': {}, 'Specifics': {}}

    def get_specific_ids_list(self) -> list:
        try:
            config_json = json.loads(self.service_config_config)
        except ValueError as err:
            raise err
        except TypeError:
            config_json = self.get_empty_config()

        if 'Specifics' in config_json:
            ids = [specific_id for specific_id in config_json['Specifics']]
        else:
            ids = []

        return ids

    @staticmethod
    def create_defaults():
        from .TeraUser import TeraUser
        from .TeraDevice import TeraDevice
        from .TeraService import TeraService
        from .TeraParticipant import TeraParticipant

        new_config = TeraServiceConfig()
        new_config.id_user = TeraUser.get_user_by_id(1).id_user
        new_config.id_service = TeraService.get_openteraserver_service().id_service
        new_config.service_config_config = '{"Globals": {"notification_sounds": true}}'
        db.session.add(new_config)

        new_config = TeraServiceConfig()
        new_config.id_participant = TeraParticipant.get_participant_by_name('Participant #1').id_participant
        new_config.id_service = TeraService.get_service_by_key('VideoRehabService').id_service
        new_config.service_config_config = '{"Globals": {"default_muted": false}, "Specifics": {"id": "pc-001", ' \
                                           '"default_muted": true}}'
        db.session.add(new_config)

        new_config = TeraServiceConfig()
        new_config.id_device = TeraDevice.get_device_by_name('Apple Watch #W05P1').id_device
        new_config.id_service = TeraService.get_service_by_key('BureauActif').id_service
        new_config.service_config_config = '{"Globals": {"delete_from_device": true}}'
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

