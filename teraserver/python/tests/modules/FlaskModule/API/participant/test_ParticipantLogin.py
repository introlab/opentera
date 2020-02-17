import unittest
import os
from requests import get
import json
from base64 import b64encode
# request_headers = {'Authorization': 'OpenTera ' + self.__user_token}
# TODO: remove verify=False and check certificate
# backend_response = get(url=self.__backend_url + path, headers=request_headers, verify=self.__backend_cacert)
# return backend_response


class ParticipantLoginTest(unittest.TestCase):

    host = 'localhost'
    port = 4040
    login_endpoint = '/api/participant/login'

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def make_url(self, hostname, port, endpoint):
        return 'https://' + hostname + ':' + str(port) + endpoint

    def test_login_valid_participant_httpauth(self):
        url = self.make_url(self.host, self.port, self.login_endpoint)
        # Using default participant information
        backend_response = get(url=url, verify=False, auth=('participant1', 'opentera'))
        self.assertEqual(backend_response.status_code, 200)
        self.assertEqual(backend_response.headers['Content-Type'], 'application/json')
        json_data = json.loads(backend_response.text)
        self.assertGreater(len(json_data), 0)
