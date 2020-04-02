from flask import jsonify, session, request
from flask_restplus import Resource, reqparse, inputs, fields
from sqlalchemy import exc
from flask_babel import gettext
from sqlalchemy.exc import InvalidRequestError
from services.VideoDispatch.FlaskModule import default_api_ns as api
from services.VideoDispatch.AccessManager import AccessManager
from libtera.redis.RedisRPCClient import RedisRPCClient
from messages.python.StopSessionEvent_pb2 import StopSessionEvent
from google.protobuf.any_pb2 import Any

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('session_key', type=str, help='Session key to manage')
get_parser.add_argument('session_stop', type=inputs.boolean, help='Set to true to stop the sessions specified')
post_parser = api.parser()


class QuerySessionManage(Resource):

    def __init__(self, _api, flaskModule=None):
        Resource.__init__(self, _api)
        self.module = flaskModule

    @AccessManager.token_required
    @api.expect(get_parser)
    @api.doc(description='Manage session',
             responses={200: 'Success',
                        400: 'Required parameter is missing',
                        500: 'Internal server error',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'})
    def get(self):
        args = get_parser.parse_args()

        # If we have no arguments, don't do anything!
        if not any(args.values()):
            return '', 400

        if args['session_stop']:
            if not args['session_key']:
                return 'Missing session key', 400

            # Do a request to stop the session
            client = RedisRPCClient(self.module.config.redis_config)
            result = client.call('VideoDispatchService.WebRTCModule', 'stop_session', args['session_key'])
            if not result:
                print('Error!')
                return 'Internal server error', 500

            reply = {}

            # Emit websocket message to stop session
            if 'participant_uuid' in result:
                participant_uuid = result['participant_uuid']

                topic = 'websocket.participant.' + participant_uuid
                event = StopSessionEvent()
                event.session_key = args['session_key']

                message = self.module.create_tera_message(dest=topic)
                any_message = Any()
                any_message.Pack(event)
                message.data.extend([any_message])
                self.module.publish(message.head.dest, message.SerializeToString())

        return 200

    @AccessManager.token_required
    @api.expect(post_parser)
    @api.doc(description='Update/Create session',
             responses={200: 'Success',
                        400: 'Required parameter is missing',
                        500: 'Internal server error',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'})
    def post(self):
        return 'Not Implemented', 501


