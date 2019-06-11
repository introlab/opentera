from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.serialization import (Encoding, PrivateFormat, NoEncryption)
import datetime
import os
import uuid

# info at https://cryptography.io
def generate_ca_certificate(common_name=u'OpenTeraServer', country_name=u'CA',
                            state_or_province=u'Québec', locality_name=u'Sherbrooke',
                            organization_name=u'Université de Sherbrooke'):

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
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, organization_name)
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
            # Our certificate will be valid for 10 years
            datetime.datetime.utcnow() + datetime.timedelta(days=3650)
        ).add_extension(
            x509.SubjectAlternativeName([x509.DNSName(u"localhost")]),
            critical=False,
            # Sign our certificate with our private key
        ).sign(private_key, hashes.SHA256(), default_backend())

    result['certificate'] = cert

    return result


def write_private_key_and_ca_certificate(info: dict, path=''):
    """
        Use def generate_ca_certificate(...) to generate the private key and certificate before.

    """
    try:
        # Will write private key in PEM (base64) format
        with open(path + '/key.pem', 'wb') as f:
            f.write(info['private_key'].private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.TraditionalOpenSSL,
                encryption_algorithm=NoEncryption()
            ))

        # Will write certificate
        with open(path + '/certificate.pem', 'wb') as f:
            f.write(info['certificate'].public_bytes(serialization.Encoding.PEM))
    except:
        return False

    return True


def load_private_key_and_ca_certificate(path=''):
    result = {}
    # Load key
    key_bytes = open(path + '/key.pem', 'rb').read()
    private_key = serialization.load_pem_private_key(key_bytes, password=None, backend=default_backend())
    result['private_key'] = private_key

    # Load certificate
    cert_bytes = open(path + '/certificate.pem', 'rb').read()
    certificate = x509.load_pem_x509_certificate(cert_bytes, default_backend())
    result['certificate'] = certificate

    return result


def create_certificate_signing_request(user_uuid=uuid.uuid4()):

    result = {}

    # 1. You generate a private / public key pair
    private_key = rsa.generate_private_key(public_exponent=65537, key_size=2048, backend=default_backend())

    result['private_key'] = private_key

    # 2. You create a request for a certificate, which is signed by your key (to prove that you own the key)
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
        # Provide various details about who we are.
        x509.NameAttribute(NameOID.USER_ID, str(user_uuid))
        ])).sign(private_key, hashes.SHA256(), default_backend())

    result['csr'] = csr

    return result


def generate_user_certificate(csr, ca_info):
    # 3 You give your csr to a CA (but not the private key!)
    # 4 The CA validates that you own the resource (verify uuid?)
    # 5 The CA gives you a certificate, signed by them, which identifies your public key, and the resource you are
    #   authenticated for.
    builder = x509.CertificateBuilder()

    ca = ca_info['certificate']
    ca_key = ca_info['private_key']
    # WARNING, subject needs to be verified
    builder = builder.subject_name(csr.subject)
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

    ca_info = generate_ca_certificate()

    write_private_key_and_ca_certificate(ca_info, path=os.getcwd())

    test = load_private_key_and_ca_certificate(path=os.getcwd())

    client_info = create_certificate_signing_request()

    cert = generate_user_certificate(client_info['csr'], ca_info)

    print(ca_info)
