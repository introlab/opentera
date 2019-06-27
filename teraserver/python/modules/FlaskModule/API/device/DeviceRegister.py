from flask_restful import Resource, reqparse
from flask import jsonify
from flask import request
import base64
from libtera.crypto.crypto_utils import generate_device_certificate, load_private_pem_key, load_pem_certificate
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization

from libtera.db.Base import db
from libtera.db.models.TeraDevice import TeraDevice
from libtera.db.models.TeraDeviceType import TeraDeviceType
import uuid

class DeviceRegister(Resource):
    """
    Registration process requires a POST with a certificate signing request (CSR)
    Will return the certificate with newly created device UUID, but disabled.
    Administrators will need to put the device in a site and enable it before use.
    """
    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

        self.ca_info = dict()

        # Load CA private key
        self.ca_info['private_key'] = load_private_pem_key(self.module.config.server_config['ssl_path']
                                                           + '/' + self.module.config.server_config['ca_private_key'])

        # Load CA certificate
        self.ca_info['certificate'] = load_pem_certificate(self.module.config.server_config['ssl_path'] + '/'
                                                           + self.module.config.server_config['ca_certificate'])

        print(self.ca_info)

    def get(self):
        print(request)
        return '', 200

    def post(self):
        print(request)

        # We should receive a certificate signing request (base64)
        if request.content_type == 'application/octet-stream':
            try:
                # Read certificate request
                req = x509.load_pem_x509_csr(request.data, default_backend())

                # Create TeraDevice
                device = TeraDevice()

                # Required field(s)
                # Name should be taken from CSR
                device.device_name = str(req.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value)
                device.device_onlineable = False
                device.device_enabled = False
                device.device_type = TeraDeviceType.DeviceTypeEnum.SENSOR.value
                device.device_uuid = str(uuid.uuid4())
                device.create_token()
                device.update_last_online()

                # Must sign request with CA/key and generate certificate
                cert = generate_device_certificate(req, self.ca_info, device.device_uuid)

                # Update certificate
                device.device_certificate = cert.public_bytes(serialization.Encoding.PEM).decode('utf-8')

                # Store
                db.session.add(device)
                db.session.commit()

                result = dict()
                result['certificate'] = device.device_certificate

                # Return certificate...
                return jsonify(result)
            except:
                return 'Error processing request', 400
        else:
            return 'Invalid content type', 400