from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.serialization import (Encoding, PrivateFormat, NoEncryption)
import datetime
import os
import uuid
import socket


def load_private_pem_key(filename):
    with open(filename, 'rb') as key:
        private_key = serialization.load_pem_private_key(key.read(), None, default_backend())
        return private_key

    return None


def load_pem_certificate(filename):
    with open(filename, 'rb') as f:
        cert = x509.load_pem_x509_certificate(f.read(), default_backend())
        return cert

    return None


def load_pem_certificate_from_data(data: bytes):
    return x509.load_pem_x509_certificate(data, default_backend())


# info at https://cryptography.io
def generate_ca_certificate(common_name=socket.gethostname(), country_name=u'CA',
                            state_or_province=u'State_Or_Province', locality_name=u'Locality Name',
                            organization_name=u'Organization Name', email=u'test@noemail.com'):

    result = {}

    # Generate the private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend())

    result['private_key'] = private_key

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        x509.NameAttribute(NameOID.COUNTRY_NAME, country_name),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state_or_province),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality_name),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization_name),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, email)
    ])

    builder = x509.CertificateSigningRequestBuilder()

    # Create Certificate
    cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow() - datetime.timedelta(days=1)
        ).not_valid_after(
            # Our certificate will be valid for 10 years
            datetime.datetime.utcnow() + datetime.timedelta(days=3650)
        ).add_extension(
            x509.BasicConstraints(ca=True, path_length=None),
            critical=True
            # Sign our certificate with our private key
        ).sign(private_key, hashes.SHA256(), default_backend())

    result['certificate'] = cert

    return result


def generate_local_certificate_csr(common_name=socket.gethostname(), country_name=u'CA',
                                   state_or_province=u'State_Or_Province', locality_name=u'Locality Name',
                                   organization_name=u'Organization Name', email=u'test@noemail.com'):

    result = {}

    # 1. You generate a private / public key pair
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    result['private_key'] = private_key

    # 2. You create a request for a certificate, which is signed by your key (to prove that you own the key)
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        # Provide various details about who we are.
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        x509.NameAttribute(NameOID.COUNTRY_NAME, country_name),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state_or_province),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality_name),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization_name),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, email)
    ])).sign(private_key, hashes.SHA256(), default_backend())

    result['csr'] = csr

    return result


def generate_local_certificate(common_name=socket.gethostname(), country_name=u'CA',
                               state_or_province=u'State_Or_Province', locality_name=u'Locality Name',
                               organization_name=u'Organization Name', email=u'test@noemail.com'):

    result = {}

    # Generate the private key
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend())

    result['private_key'] = private_key

    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, common_name),
        x509.NameAttribute(NameOID.COUNTRY_NAME, country_name),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, state_or_province),
        x509.NameAttribute(NameOID.LOCALITY_NAME, locality_name),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization_name),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS, email)
    ])

    builder = x509.CertificateSigningRequestBuilder()

    # Create Certificate
    cert = x509.CertificateBuilder().subject_name(
            subject
        ).issuer_name(
            issuer
        ).public_key(
            private_key.public_key()
        ).serial_number(
            x509.random_serial_number()
        ).not_valid_before(
            datetime.datetime.utcnow() - datetime.timedelta(hours=1)
        ).not_valid_after(
            # Our certificate will be valid for 1 year
            datetime.datetime.utcnow() + datetime.timedelta(days=365)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
            critical=False
            # Sign our certificate with our private key
        ).add_extension(
            x509.BasicConstraints(ca=False, path_length=None),
            critical=True
        ).sign(private_key, hashes.SHA256(), default_backend())

    result['certificate'] = cert

    return result


def write_private_key_and_certificate(info: dict, keyfile='key.pem', certfile='cert.pem'):
    """
        Use def generate_ca_certificate(...) to generate the private key and certificate before.

    """
    try:
        # Will write private key in PEM (base64) format
        with open(keyfile, 'wb') as f:
            f.write(info['private_key'].private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=NoEncryption()
            ))

        # Will write certificate
        with open(certfile, 'wb') as f:
            f.write(info['certificate'].public_bytes(serialization.Encoding.PEM))
    except:
        return False

    return True


# Default apple watch, for testing...
def create_certificate_signing_request(device_name):

    result = {}

    # 1. You generate a private / public key pair
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    result['private_key'] = private_key

    # 2. You create a request for a certificate, which is signed by your key (to prove that you own the key)
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        # Provide various details about who we are.
        x509.NameAttribute(NameOID.COMMON_NAME, str(device_name))
        ])).sign(private_key, hashes.SHA256(), default_backend())

    result['csr'] = csr

    return result


def generate_local_certificate_with_csr(csr, ca_info):
    # 3 You give your csr to a CA (but not the private key!)
    # 4 The CA validates that you own the resource (verify uuid?)
    # 5 The CA gives you a certificate, signed by them, which identifies your public key, and the resource you are
    #   authenticated for.
    builder = x509.CertificateBuilder()

    ca = ca_info['certificate']
    ca_key = ca_info['private_key']

    # # WARNING, subject needs to be verified by CA, do not use csr subject
    builder = builder.subject_name(
        x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u'127.0.0.1'),
            x509.NameAttribute(NameOID.COUNTRY_NAME, u'CA'),
            x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u'State'),
            x509.NameAttribute(NameOID.LOCALITY_NAME, u'Locality'),
            x509.NameAttribute(NameOID.ORGANIZATION_NAME, u'Organization'),
            x509.NameAttribute(NameOID.EMAIL_ADDRESS, u'test@noemail.com')
        ])
    )

    builder = builder.add_extension(
        x509.SubjectAlternativeName([x509.DNSName(u'localhost')]),
        critical=False
    )

    # Certificate valid for one year
    builder = builder.issuer_name(ca.subject)
    builder = builder.not_valid_before(datetime.datetime.now() - datetime.timedelta(hours=1))
    builder = builder.not_valid_after(datetime.datetime.now() + datetime.timedelta(days=365))
    builder = builder.public_key(csr.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    for ext in csr.extensions:
        builder = builder.add_extension(ext.value, ext.critical)

    # Sign with the CA
    certificate = builder.sign(
        private_key=ca_key,
        algorithm=hashes.SHA256(),
        backend=default_backend()
    )

    return certificate


def generate_device_certificate(csr, ca_info, device_uuid):
    # 3 You give your csr to a CA (but not the private key!)
    # 4 The CA validates that you own the resource (verify uuid?)
    # 5 The CA gives you a certificate, signed by them, which identifies your public key, and the resource you are
    #   authenticated for.
    builder = x509.CertificateBuilder()

    ca = ca_info['certificate']
    ca_key = ca_info['private_key']

    builder = builder.subject_name(
        x509.Name([
            x509.NameAttribute(NameOID.COMMON_NAME, u'Device'),
            x509.NameAttribute(NameOID.USER_ID, str(device_uuid))
        ])
    )

    builder = builder.issuer_name(ca.subject)
    builder = builder.not_valid_before(datetime.datetime.now() - datetime.timedelta(hours=1))
    builder = builder.not_valid_after(datetime.datetime.now() + datetime.timedelta(days=3650))
    builder = builder.public_key(csr.public_key())
    builder = builder.serial_number(x509.random_serial_number())
    for ext in csr.extensions:
        builder = builder.add_extension(ext.value, ext.critical)

    # Sign with the CA
    certificate = builder.sign(
        private_key=ca_key,
        algorithm=hashes.SHA256(),
        backend=default_backend()
    )

    return certificate


# For testing...
if __name__ == '__main__':
    print(socket.gethostname())

    current_path = os.getcwd()

    # Generate CA certificate
    ca_info = generate_ca_certificate(common_name='IntRoLab_CA')
    write_private_key_and_certificate(ca_info, keyfile=current_path + '/../../certificates/ca_key.pem',
                                      certfile=current_path + '/../../certificates/ca_cert.pem')

    # Generate Local Certificate key and csr
    local_info = generate_local_certificate_csr()
    print(local_info)

    # Create local certificate signed by our CA
    local_info['certificate'] = generate_local_certificate_with_csr(local_info['csr'], ca_info)
    print(local_info)

    write_private_key_and_certificate(local_info, keyfile=current_path + '/../../certificates/site_key.pem',
                                      certfile=current_path + '/../../certificates/site_cert.pem')

    # # Generate signing request
    # client_info = create_certificate_signing_request(device_name='Test Device')
    # client_info['certificate'] = generate_device_certificate(client_info['csr'], ca_info,
    #                                                          'b707e0b2-e649-47e7-a938-2b949c423f73')
    #
    # # Client test key + certificate
    # write_private_key_and_certificate(client_info,
    #                                   keyfile=current_path + '/../../certificates/devices/client_key.pem',
    #                                   certfile=current_path + '/../../certificates/devices/client_certificate.pem')
    #
    # # Will use hostname as common name by default
    # site_info = generate_local_certificate()
    # write_private_key_and_certificate(site_info, keyfile=current_path + '/../../certificates/site_key.pem',
    #                                   certfile=current_path + '/../../certificates/site_cert.pem')
    #
    # print(ca_info)
    # print(site_info)
    # print(client_info)
