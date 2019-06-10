from cryptography import x509
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives.serialization import (Encoding, PrivateFormat, NoEncryption)
import datetime
import os


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
    cert_bytes = open(path  + '/certificate.pem', 'rb').read()
    certificate = x509.load_pem_x509_certificate(cert_bytes, default_backend())
    result['certificate'] = certificate

    return result


# For testing...
if __name__ == '__main__':

    info = generate_ca_certificate()

    write_private_key_and_ca_certificate(info, path=os.getcwd())

    test = load_private_key_and_ca_certificate(path=os.getcwd())

    print(info)
