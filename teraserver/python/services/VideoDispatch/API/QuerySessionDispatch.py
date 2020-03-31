from flask import jsonify, session, request
from flask_restplus import Resource, reqparse, inputs, fields
from sqlalchemy import exc
from flask_babel import gettext
from sqlalchemy.exc import InvalidRequestError
from services.VideoDispatch.FlaskModule import default_api_ns as api
from services.VideoDispatch.AccessManager import AccessManager
from libtera.redis.RedisRPCClient import RedisRPCClient

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

        # TODO: Get real URL to connect to
        reply = {'participant_name': 'Participant Test', 'session_url': 'https://localhost:40075/videodispatch/session?'
                                                                        'id=1234'}
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


