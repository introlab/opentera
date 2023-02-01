from flask_restx import Resource, reqparse
from flask_babel import gettext
from flask import jsonify
from flask import request
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import base64
from opentera.crypto.crypto_utils import generate_device_certificate, load_private_pem_key, load_pem_certificate
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization

from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraDeviceType import TeraDeviceType
from opentera.db.models.TeraSessionType import TeraSessionType
from modules.FlaskModule.FlaskModule import device_api_ns as api
import uuid
from modules.FlaskModule.FlaskModule import flask_app
from sqlalchemy.exc import SQLAlchemyError

limiter = Limiter(get_remote_address, app=flask_app, storage_uri="memory://")


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

    def create_device(self, name, device_json=None):
        # Create TeraDevice
        device = TeraDevice()

        if device_json:
            device.from_json(device_json)
        else:
            # Name should be taken from CSR or JSON request
            device.device_name = name
            # TODO set flags properly
            device.device_onlineable = False
            # TODO FORCING 'capteur' as default?
            device.id_device_type = TeraDeviceType.get_device_type_by_key('capteur').id_device_type

        # Force disabled by default
        device.device_enabled = False

        return device

    @api.doc(description='Register a device with certificate or token request. This endpoint is rate limited. '
                         'Use application/octet-stream to send CSR or application/json Content-Type for token '
                         'generation.',
             responses={200: 'Success, will return registration information. Devices must then be enabled by admin.',
                        400: 'Missing parameter(s)',
                        500: 'Internal server error'})
    def post(self):
        # We should receive a certificate signing request (base64) in an octet-stream
        if request.content_type == 'application/octet-stream':
            # try:
            # Read certificate request
            req = x509.load_pem_x509_csr(request.data, default_backend())

            if req.is_signature_valid:

                # Name should be taken from CSR
                device = self.create_device(str(req.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value))

                # Must sign request with CA/key and generate certificate
                cert = generate_device_certificate(req, self.ca_info, device.device_uuid)

                # Update certificate
                device.device_certificate = cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')

                # Store
                TeraDevice.insert(device)

                result = dict()
                result['certificate'] = device.device_certificate
                result['ca_info'] = self.ca_info['certificate'].public_bytes(serialization.Encoding.PEM).decode('utf-8')
                result['token'] = device.device_token

                self.module.logger.log_info(self.module.module_name, DeviceRegister.__name__,
                                            'post', 'Device registered (certificate)',
                                            device.device_uuid, result['certificate'])

                # Return certificate...
                return jsonify(result)
            else:
                self.module.logger.log_error(self.module.module_name,
                                             DeviceRegister.__name__,
                                             'post', 400, 'Invalid CSR signature', request.data)

                return gettext('Invalid CSR signature'), 400
                # except:
                #     return 'Error processing request', 400

        elif request.content_type == 'application/json':

            if 'device_info' not in request.json:
                return gettext('Invalid content type'), 400

            device_info = request.json['device_info']

            # Check if we have device name
            if 'device_name' not in device_info:
                return gettext('Invalid content type'), 400

            if 'id_device_type' not in device_info:
                return gettext('Invalid content type'), 400

            try:
                device_name = device_info['device_name']
                device = self.create_device(device_name, device_info)

                # Store
                TeraDevice.insert(device)

                result = dict()
                result['token'] = device.device_token

                self.module.logger.log_info(self.module.module_name, DeviceRegister.__name__,
                                            'post', 'Device registered (token)', device.device_uuid, result['token'])

                # Return token
                return jsonify(result)
            except SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             DeviceRegister.__name__,
                                             'post', 500, 'Database error', str(e))
                return e.args, 500

        else:
            return gettext('Invalid content type'), 400
