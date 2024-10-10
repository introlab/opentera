from flask_restx import Resource, inputs
from flask_babel import gettext
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from opentera.crypto.crypto_utils import generate_device_certificate, load_private_pem_key, load_pem_certificate

from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization

from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraDeviceType import TeraDeviceType
from opentera.db.models.TeraDeviceSubType import TeraDeviceSubType
from opentera.db.models.TeraServerSettings import TeraServerSettings
from modules.FlaskModule.FlaskModule import device_api_ns as api

from modules.FlaskModule.FlaskModule import flask_app
import uuid

limiter = Limiter(get_remote_address, app=flask_app, storage_uri="memory://")

api_parser = api.parser()
api_parser.add_argument('key', type=str, required=True, help='Server device registration key')
api_parser.add_argument('name', type=str, required=True, help='Device name to use')
api_parser.add_argument('type_key', type=str, required=True, help='Device type key to use')
api_parser.add_argument('subtype_name', type=str, help='Device subtype name to use')
api_parser.add_argument('onlineable', type=inputs.boolean, help='Device can get online status')


class DeviceRegister(Resource):
    """
    Registration process requires a POST with a certificate signing request (CSR)
    Will return the certificate with newly created device UUID, but disabled.
    Administrators will need to put the device in a site and enable it before use.
    """
    decorators = [limiter.limit("1/second", error_message='Rate Limited',
                                exempt_when=lambda: flask_app.testing is True)]

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

        self.ca_info = dict()

        if not self.test:
            # Load CA private key
            self.ca_info['private_key'] = load_private_pem_key(self.module.config.server_config['ssl_path'] + '/'
                                                               + self.module.config.server_config['ca_private_key'])

            # Load CA certificate
            self.ca_info['certificate'] = load_pem_certificate(self.module.config.server_config['ssl_path'] + '/'
                                                               + self.module.config.server_config['ca_certificate'])
        else:
            # Generate temporary CA certificate and key for tests
            from opentera.crypto.crypto_utils import generate_ca_certificate
            info = generate_ca_certificate()
            self.ca_info['private_key'] = info['private_key']
            self.ca_info['certificate'] = info['certificate']

    @api.doc(description='Register a device to use token identification. This endpoint is rate limited. If the device '
                         'type key doesn\'t exist, a new one will be created. Same behavior for subtype name.',
             reponses={200: 'Success - returns registration information. Devices must then be enabled by admin.',
                       400: 'Missing or invalid parameter',
                       401: 'Unauthorized - provided registration key is invalid'})
    @api.expect(api_parser)
    def get(self):
        """
        Register a new device in the server (token based)
        """
        args = api_parser.parse_args(strict=True)

        # Check if provided registration key is ok
        if args['key'] != TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerDeviceRegisterKey):
            return gettext('Invalid registration key'), 401

        new_device = self.get_new_device(args)
        TeraDevice.insert(new_device)

        device_json = new_device.to_json(minimal=True, ignore_fields=['id_device', 'id_device_type',
                                                                      'id_device_subtype'])
        device_json['device_token'] = new_device.device_token

        self.module.logger.log_info(self.module.module_name, DeviceRegister.__name__,
                                    'post', 'Device registered (token)',
                                    new_device.device_name + '(' + new_device.device_uuid + ')')

        return device_json

    @api.doc(description='Register a device with certificate request. This endpoint is rate limited. If the device '
                         'type key doesn\'t exist, a new one will be created. Same behavior for subtype name.'
                         'Use application/octet-stream to send CSR.',
             responses={200: 'Success - returns registration information. Devices must then be enabled by admin.',
                        400: 'Missing or invalid parameter',
                        401: 'Unauthorized - provided registration key is invalid'})
    def post(self):
        """
        Register a new device in the server (certificate based)
        """
        args = api_parser.parse_args(strict=True)

        # Check if provided registration key is ok
        if args['key'] != TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerDeviceRegisterKey):
            return gettext('Invalid registration key'), 401

        # We should receive a certificate signing request (base64) in an octet-stream
        if request.content_type != 'application/octet-stream':
            return gettext('Invalid content type'), 400

        # Read certificate request
        req = x509.load_pem_x509_csr(request.data, default_backend())

        if req.is_signature_valid:

            new_device = self.get_new_device(args)
            new_device.device_uuid = str(uuid.uuid4())  # Device uuid is required to generate certificate

            # Must sign request with CA/key and generate certificate
            cert = generate_device_certificate(req, self.ca_info, new_device.device_uuid)

            # Update certificate
            new_device.device_certificate = cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')

            # Store
            TeraDevice.insert(new_device)

            device_json = new_device.to_json(minimal=True, ignore_fields=['id_device', 'id_device_type',
                                                                          'id_device_subtype'])
            device_json['device_certificate'] = new_device.device_certificate
            device_json['ca_info'] = self.ca_info['certificate'].public_bytes(serialization.Encoding.PEM).decode('utf-8')
            device_json['device_token'] = new_device.device_token

            self.module.logger.log_info(self.module.module_name, DeviceRegister.__name__,
                                        'post', 'Device registered (certificate)',
                                        new_device.device_name + '(' + new_device.device_uuid + ')')

            return device_json
        else:
            self.module.logger.log_error(self.module.module_name, DeviceRegister.__name__,
                                         'post', 400, 'Invalid CSR signature', request.data)

            return gettext('Invalid CSR signature'), 400

    @staticmethod
    def get_new_device(args) -> TeraDevice:
        # Get device type
        device_type = TeraDeviceType.get_device_type_by_key(args['type_key'])
        if not device_type:
            # Create a new device type with the appropriate key
            device_type = TeraDeviceType()
            device_type.device_type_key = args['type_key']
            device_type.device_type_name = device_type.device_type_key
            TeraDeviceType.insert(device_type)

        # Get device subtype, if required
        device_subtype = None
        if args['subtype_name']:
            device_subtype = TeraDeviceSubType.get_device_subtype_by_name(args['subtype_name'],
                                                                          device_type.id_device_type)
            if not device_subtype:
                # Create a new device subtype
                device_subtype = TeraDeviceSubType()
                device_subtype.id_device_type = device_type.id_device_type
                device_subtype.device_subtype_name = args['subtype_name']
                TeraDeviceSubType.insert(device_subtype)

        # Create new device
        device = TeraDevice()
        device.device_name = args['name']
        device.id_device_type = device_type.id_device_type
        if device_subtype:
            device.id_device_subtype = device_subtype.id_device_subtype
        if 'onlineable' in args:
            device.device_onlineable = args['onlineable']
        return device
