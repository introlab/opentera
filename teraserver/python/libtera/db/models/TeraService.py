from libtera.db.Base import db, BaseModel
from flask_babel import gettext

import uuid


class TeraService(db.Model, BaseModel):
    __tablename__ = 't_services'
    default_config_schema = ''

    id_service = db.Column(db.Integer, db.Sequence('id_service_sequence'), primary_key=True, autoincrement=True)
    service_uuid = db.Column(db.String(36), nullable=False, unique=True)
    service_name = db.Column(db.String, nullable=False)
    service_key = db.Column(db.String, nullable=False, unique=True)
    service_hostname = db.Column(db.String, nullable=False)
    service_port = db.Column(db.Integer, nullable=False)
    service_endpoint = db.Column(db.String, nullable=False)
    service_clientendpoint = db.Column(db.String, nullable=False)
    service_enabled = db.Column(db.Boolean, nullable=False, default=False)
    service_system = db.Column(db.Boolean, nullable=False, default=False)
    service_config_schema = db.Column(db.String, nullable=False, default=default_config_schema)
    service_default_config = db.Column(db.String, nullable=True, default='{"Globals": {}}')

    service_roles = db.relationship('TeraServiceRole')

    def __init__(self):
        pass

    def __str__(self):
        return '<TeraService ' + str(self.service_name) + ' >'

    def __repr__(self):
        return self.__str__()

    def to_json(self, ignore_fields=None, minimal=False):
        if ignore_fields is None:
            ignore_fields = []

        ignore_fields.extend(['service_roles', 'service_system'])

        if minimal:
            ignore_fields.extend(['service_config_schema'])

        json_service = super().to_json(ignore_fields=ignore_fields)
        if not minimal:
            # Add roles for that service
            roles = []
            for role in self.service_roles:
                roles.append(role.to_json())
            json_service['service_roles'] = roles

        return json_service

    def get_token(self, token_key: str, expiration=3600):
        import time
        import jwt
        # Creating token with user info
        now = time.time()
        payload = {
            'iat': int(now),
            'exp': int(now) + expiration,
            'iss': 'TeraServer',
            'service_uuid': self.service_uuid
        }

        return jwt.encode(payload, token_key, algorithm='HS256').decode('utf-8')

    def has_config_schema(self) -> bool:
        return self.service_config_schema != self.default_config_schema

    @staticmethod
    def get_service_by_key(key: str):
        service = TeraService.query.filter_by(service_key=key).first()

        if service:
            return service

        return None

    @staticmethod
    def get_service_by_uuid(p_uuid: str):
        service = TeraService.query.filter_by(service_uuid=p_uuid).first()

        if service:
            return service

        return None

    @staticmethod
    def get_service_by_name(name: str):
        return TeraService.query.filter_by(service_name=name).first()

    @staticmethod
    def get_service_by_id(s_id: int):
        return TeraService.query.filter_by(id_service=s_id).first()

    @staticmethod
    def get_openteraserver_service():
        return TeraService.get_service_by_key('OpenTeraServer')

    @staticmethod
    def create_defaults():
        new_service = TeraService()
        new_service.service_uuid = '00000000-0000-0000-0000-000000000001'
        new_service.service_key = 'OpenTeraServer'
        new_service.service_name = 'OpenTera Server'
        new_service.service_hostname = 'localhost'
        new_service.service_port = 4040
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/'
        new_service.service_enabled = True
        new_service.service_system = True
        new_service.service_config_schema = new_service.create_default_config_schema()
        db.session.add(new_service)

        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'LoggingService'
        new_service.service_name = 'Logging Service'
        new_service.service_hostname = 'localhost'
        new_service.service_port = 4041
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/log'
        new_service.service_enabled = True
        new_service.service_system = True
        new_service.service_config_schema = new_service.create_default_config_schema()
        db.session.add(new_service)

        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'FileTransferService'
        new_service.service_name = 'File Transfer Service'
        new_service.service_hostname = 'localhost'
        new_service.service_port = 4042
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/file'
        new_service.service_enabled = True
        new_service.service_system = True
        new_service.service_config_schema = new_service.create_default_config_schema()
        db.session.add(new_service)

        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'BureauActif'
        new_service.service_name = 'Bureau Actif'
        new_service.service_hostname = 'localhost'
        new_service.service_port = 4050
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/bureau'
        new_service.service_enabled = True
        new_service.service_config_schema = new_service.create_default_config_schema()
        db.session.add(new_service)

        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'VideoDispatch'
        new_service.service_name = 'Salle d\'attente vidéo'
        new_service.service_hostname = 'localhost'
        new_service.service_port = 4060
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/videodispatch'
        new_service.service_enabled = True
        new_service.service_config_schema = new_service.create_default_config_schema()
        db.session.add(new_service)

        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'VideoRehabService'
        new_service.service_name = 'Télé-réadaptation vidéo'
        new_service.service_hostname = 'localhost'
        new_service.service_port = 4070
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/rehab'
        new_service.service_enabled = True
        new_service.service_config_schema = new_service.create_default_config_schema()
        db.session.add(new_service)

        new_service = TeraService()
        new_service.service_uuid = str(uuid.uuid4())
        new_service.service_key = 'RobotTeleOperationService'
        new_service.service_name = 'Robot Teleoperation Service'
        new_service.service_hostname = 'localhost'
        new_service.service_port = 4080
        new_service.service_endpoint = '/'
        new_service.service_clientendpoint = '/robot'
        new_service.service_enabled = True
        new_service.service_config_schema = new_service.create_default_config_schema()
        db.session.add(new_service)

        db.session.commit()

    def create_default_config_schema(self) -> str:
        from libtera.forms.TeraForm import TeraForm, TeraFormItem, TeraFormItemCondition, TeraFormSection, TeraFormValue
        import json

        form = TeraForm('service_config_config')

        if self.service_key == 'VideoRehabService':
            # Sections
            section1 = TeraFormSection("main_audio_video", gettext("Configuration audio-vidéo"))
            form.add_section(section1)

            # Items
            section1.add_item(TeraFormItem("camera", gettext("Caméra"), "videoinputs", False))
            item = TeraFormItem("teracam_type", gettext("Type de caméra"), "array", True,
                                [TeraFormValue("0", gettext("Caméra réseau")),
                                 TeraFormValue("1", gettext("Capture d'écran"))],
                                "0", TeraFormItemCondition("camera", "=", "TeraCam"))
            section1.add_item(item)

            item = TeraFormItem("teracam_src", gettext("Adresse du flux de la caméra"), "text", True,
                                item_condition=TeraFormItemCondition("teracam_type", "=", 0))
            section1.add_item(item)

            item = TeraFormItem("teracam_screen_fps", gettext("Trames par seconde"), "array", True,
                                ["Maximum", "5", "10", "15",
                                 "20", "24", "30"],
                                item_condition=TeraFormItemCondition("teracam_type", "=", 1))
            section1.add_item(item)
            item = TeraFormItem("teracam_screen_res", gettext("Résolution"), "array", True,
                                ["Maximum", "160x120", "320x240",
                                 "640x480", "720x480", "800x600",
                                 "1024x768", "1280x720", "1440x900",
                                 "1680x1050", "1920x1080"],
                                item_condition=TeraFormItemCondition("teracam_type", "=", 1))
            section1.add_item(item)

            section1.add_item(TeraFormItem("camera_ptz", gettext("Caméra contrôlable (PTZ)"), "boolean"))
            item = TeraFormItem("camera_ptz_type", gettext("Type de contrôle"), "array", True,
                                [TeraFormValue("0", gettext("Vivotek")), TeraFormValue("1", gettext("ONVIF (générique)"))],
                                item_condition=TeraFormItemCondition("camera_ptz", "=", True))
            section1.add_item(item)
            item = TeraFormItem("camera_ptz_ip", gettext("Adresse réseau"), "text", True,
                                item_condition=TeraFormItemCondition("camera_ptz", "=", True))
            section1.add_item(item)
            item = TeraFormItem("camera_ptz_port", gettext("Port"), "numeric", True,
                                item_condition=TeraFormItemCondition("camera_ptz", "=", True))
            section1.add_item(item)
            item = TeraFormItem("camera_ptz_username", gettext("Nom utilisateur"), "text", True,
                                item_condition=TeraFormItemCondition("camera_ptz", "=", True))
            section1.add_item(item)
            item = TeraFormItem("camera_ptz_password", gettext("Mot de passe"), "password", True,
                                item_condition=TeraFormItemCondition("camera_ptz", "=", True))
            section1.add_item(item)

            section1.add_item(TeraFormItem("audio", gettext("Microphone"), "audioinputs", False))
            section1.add_item(TeraFormItem("camera2", gettext("Caméra secondaire"), "videoinputs"))

            return json.dumps(form.to_dict())

        return self.default_config_schema

    @classmethod
    def insert(cls, service):
        service.service_uuid = str(uuid.uuid4())

        # NOT USED - using TeraForm instead
        # Validate that the service config schema is a valid json schema
        # if service.service_config_schema:
        #     import jsonschema
        #     try:
        #         jsonschema.Draft7Validator.check_schema(cls.service_config_schema)
        #     except jsonschema.exceptions.SchemaError as err:
        #         raise err
        super().insert(service)

    @classmethod
    def update(cls, update_id: int, values: dict):
        # Prevent changes on UUID
        if 'service_uuid' in values:
            del values['service_uuid']

        # NOT USED - using TeraForm instead
        # Validate that the service config schema is a valid json schema
        # if 'service_config_schema' in values:
        #     import jsonschema
        #     try:
        #         jsonschema.Draft7Validator.check_schema(values['service_config_schema'])
        #     except jsonschema.exceptions.SchemaError as err:
        #         raise err
        super().update(update_id, values)

