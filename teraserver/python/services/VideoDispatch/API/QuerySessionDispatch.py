from flask import jsonify, session, request
from flask_restplus import Resource, reqparse, inputs, fields
from sqlalchemy import exc
from flask_babel import gettext
from sqlalchemy.exc import InvalidRequestError
from services.VideoDispatch.FlaskModule import default_api_ns as api
from services.VideoDispatch.AccessManager import AccessManager
from libtera.redis.RedisRPCClient import RedisRPCClient
from messages.python.JoinSessionEvent_pb2 import JoinSessionEvent
from google.protobuf.any_pb2 import Any

# Parser definition(s)
get_parser = api.parser()
post_parser = api.parser()


class QuerySessionDispatch(Resource):

    def __init__(self, _api, flaskModule=None):
        Resource.__init__(self, _api)
        self.module = flaskModule

    @AccessManager.token_required
    @api.expect(get_parser)
    @api.doc(description='Get session',
             responses={200: 'Success',
                        400: 'Required parameter is missing',
                        500: 'Internal server error',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'})
    def get(self):

        client = RedisRPCClient(self.module.config.redis_config)

        result = client.call('VideoDispatchService.OnlineUsersModule', 'participant_dispatch')

        if not result:
            print('Error!')
            return 'Internal server error', 500

        reply = {}

        if 'participant_uuid' in result:
            participant_uuid = result['participant_uuid']
            from uuid import uuid4
            session_name = str(uuid4())
            result = client.call('VideoDispatchService.WebRTCModule', 'create_session', session_name)
            if result:
                reply['participant_name'] = 'Anonymous'
                reply['session_url'] = result['url']

                # Invite participant via websocket
                topic = 'websocket.participant.' + participant_uuid
                event = JoinSessionEvent()
                event.session_url = result['url']

                message = self.module.create_tera_message(dest=topic)
                any_message = Any()
                any_message.Pack(event)
                message.data.extend([any_message])
                self.module.publish(message.head.dest, message.SerializeToString())

        return reply

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


