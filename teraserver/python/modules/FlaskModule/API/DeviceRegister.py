from flask_restful import Resource, reqparse
from modules.LoginModule.LoginModule import LoginModule, current_device
from flask import request
import base64
from cryptography import x509
from cryptography.hazmat.backends import default_backend
import OpenSSL.crypto as crypto
from libtera.crypto.crypto_utils import generate_user_certificate, load_private_pem_key, load_pem_certificate
from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa

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
            # Read certificate request
            # req = crypto.load_certificate_request(crypto.FILETYPE_PEM, request.data)

            req = x509.load_pem_x509_csr(request.data, default_backend())

            # Must sign request with CA/key
            cert = generate_user_certificate(req, self.ca_info)



            print(req)
            print(cert)

        return '', 200
