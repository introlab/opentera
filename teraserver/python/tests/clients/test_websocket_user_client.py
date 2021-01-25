import unittest
import os
from requests import get
import json
import websocket
import ssl
from opentera.messages.python.UserRegisterToEvent_pb2 import UserRegisterToEvent
from opentera.messages.python.TeraModuleMessage_pb2 import TeraModuleMessage
from google.protobuf.json_format import MessageToJson
from google.protobuf.json_format import Parse, ParseError
from google.protobuf.any_pb2 import Any
import datetime


class WebSocketUserClient(unittest.TestCase):

    host = 'localhost'
    port = 40075
    login_endpoint = '/api/user/login'
    ws = None
    token = None
    uuid = None

    def _make_url(self, hostname, port, endpoint):
        return 'https://' + hostname + ':' + str(port) + endpoint

    def _http_auth(self, username, password):
        url = self._make_url(self.host, self.port, self.login_endpoint)
        result = get(url=url, verify=False, auth=(username, password))
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.headers['Content-Type'], 'application/json')
        json_data = result.json()
        self.assertGreater(len(json_data), 0)

        # Validate fields in json response
        self.assertTrue(json_data.__contains__('websocket_url'))
        self.assertTrue(json_data.__contains__('user_uuid'))
        self.assertTrue(json_data.__contains__('user_token'))
        self.assertGreater(len(json_data['websocket_url']), 0)
        self.assertGreater(len(json_data['user_uuid']), 0)
        self.assertGreater(len(json_data['user_token']), 0)
        return json_data

    def _create_tera_message(self, dest='websocket', seq=0):
        tera_message = TeraModuleMessage()
        tera_message.head.version = 1
        tera_message.head.time = datetime.datetime.now().timestamp()
        tera_message.head.seq = seq
        tera_message.head.source = 'WebSocketUserClient'
        tera_message.head.dest = 'websocket.user.' + self.uuid
        return tera_message

    def _register_event(self, action,  event_type):
        event = UserRegisterToEvent()
        event.action = action
        event.event_type = event_type

        message = self._create_tera_message()
        # Need to use Any container
        any_message = Any()
        any_message.Pack(event)
        message.data.extend([any_message])

        # Send to websocket
        json_data = MessageToJson(message, including_default_value_fields=True)
        ret = self.ws.send(json_data)

        # Wait for answer
        val = self.ws.recv()

        return val

    def setUp(self):
        # Using siteadmin default user information
        json_data = self._http_auth('siteadmin', 'siteadmin')

        # Create websocket
        self.ws = websocket.WebSocket(sslopt={"cert_reqs": ssl.CERT_NONE})
        self.ws.connect(json_data['websocket_url'])
        self.token = json_data['user_token']
        self.uuid = json_data['user_uuid']
        self.assertTrue(self.ws.connected)

    def tearDown(self):
        if self.ws:
            self.ws.close()
        pass

    def test_events_valid_user_httpauth(self):
        # websocket is created in setUp function.
        # Test register event
        self._register_event(UserRegisterToEvent.ACTION_REGISTER, UserRegisterToEvent.EVENT_USER_CONNECTED)

        ret2 = self.ws.recv()
        print(ret2)






