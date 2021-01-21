from requests import post
import opentera.crypto.crypto_utils as crypto
from cryptography.hazmat.primitives import serialization
import datetime
from os import path

server_hostname = 'localhost'
server_port = 40075
server_scheme = 'https'
device_register_endpoint = '/api/device/register'

ca_certificate_file_name = 'ca_certificate.pem'
certificate_file_name = 'certificate.pem'
private_key_file_name = 'private_key.pem'


def make_url(scheme=server_scheme, hostname=server_hostname, port=server_port, endpoint=device_register_endpoint):
    return str(scheme) + '://' + str(hostname) + ':' + str(port) + str(endpoint)


# This process needs to be done only once to register a new device
# Once the certificates and key are generated, use them to connect to the device API
if __name__ == '__main__':

    if path.exists(certificate_file_name) and path.exists(private_key_file_name) \
            and path.exists(ca_certificate_file_name):
        print('Certificates and private key already generated. Exiting...')
        exit(-1)

    # STEP 1
    # Create a private key and Certificate Signing Request to register a new device
    # This will generate private key and signing request for the CA
    device_name = 'New Device Created at ' + str(datetime.datetime.now())
    client_info = crypto.create_certificate_signing_request(device_name)

    # Encode in CSR PEM format
    # This will be needed in our request
    encoded_csr = client_info['csr'].public_bytes(serialization.Encoding.PEM)

    # STEP 2
    # Call API /api/device/register to register a new device
    url = make_url(endpoint=device_register_endpoint)
    request_headers = {'Content-Type': 'application/octet-stream',
                       'Content-Transfer-Encoding': 'Base64'}

    # Verify = False is for servers with self signed certificates
    # The register endpoint is rate limited to 10 requests per minute.
    response = post(url=url, verify=False, headers=request_headers, data=encoded_csr)

    if response.status_code == 200:
        # We have our signed certificate
        result = response.json()

        # Save it to disk
        ca_certificate = result['ca_info'].encode('utf-8')
        certificate = result['certificate'].encode('utf-8')
        private_key = client_info['private_key'].private_bytes(serialization.Encoding.PEM,
                                                               serialization.PrivateFormat.TraditionalOpenSSL,
                                                               serialization.NoEncryption())
        with open(ca_certificate_file_name, 'wb') as f:
            f.write(ca_certificate)

        with open(certificate_file_name, 'wb') as f:
            f.write(certificate)

        with open(private_key_file_name, 'wb') as f:
            f.write(private_key)

        print('Certificate and private key saved. Keep them safe.')
        print('You need to enable the device : ', device_name, ' to get access to device api.')
        print('Make sure onlineable is true if you want to enable live sessions.')

    else:
        print('Error getting certificate: ', response.status_code)
        exit(-1)

    # Step 3
    # Enable the device using OpenTeraPlus
    # Set Onlineable flag if required
    # The signed certificate contains the UUID of the device that will be used for login and to get access to the API.

    exit(0)
