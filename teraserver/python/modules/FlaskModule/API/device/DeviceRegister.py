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
from libtera.db.models.TeraSessionType import TeraSessionType

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
            # try:
            # Read certificate request
            req = x509.load_pem_x509_csr(request.data, default_backend())

            if req.is_signature_valid:
                # Create TeraDevice
                device = TeraDevice()

                # Required field(s)
                # Name should be taken from CSR
                device.device_name = str(req.subject.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value)
                # TODO set flags properly
                device.device_onlineable = False
                # TODO WARNING - Should be disabled when created...
                device.device_enabled = True
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

                # TODO remove participant assignation
                from libtera.db.models.TeraParticipant import TeraParticipant
                from libtera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
                participant1 = TeraParticipant.get_participant_by_id(1)
                device_partipant = TeraDeviceParticipant()
                device_partipant.device_participant_participant = participant1
                device_partipant.device_participant_device = device
                db.session.add(device_partipant)

                # Commit to database
                db.session.commit()

                result = dict()
                result['certificate'] = device.device_certificate

                f = open(self.module.config.server_config['ssl_path'] + '/'
                         + self.module.config.server_config['ca_certificate'])

                result['ca_info'] = f.read()

                # Return certificate...
                return jsonify(result)
            else:
                return 'Invalid CSR signature', 400
                # except:
                #     return 'Error processing request', 400
        else:
            return 'Invalid content type', 400
