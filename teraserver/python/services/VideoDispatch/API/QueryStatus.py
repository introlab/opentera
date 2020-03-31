from flask import jsonify, session, request
from flask_restplus import Resource, reqparse, inputs, fields
from flask_babel import gettext

from services.VideoDispatch.FlaskModule import default_api_ns as api
from services.VideoDispatch.AccessManager import AccessManager, current_user_client, current_participant_client
from libtera.redis.RedisRPCClient import RedisRPCClient

# Parser definition(s)
get_parser = api.parser()
post_parser = api.parser()


class QueryStatus(Resource):

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
        if current_user_client:
            # Return all stats
            # Query only numbers, does not pop a participant
            result = client.call('VideoDispatchService.OnlineUsersModule', 'participant_dispatch', False)

            if not result:
                print('Error!')
                return 'Internal server error', 500

            return result
        else:
            if current_participant_client:
                # Return current position in the queue
                result = client.call('VideoDispatchService.OnlineUsersModule', 'participant_rank',
                                     current_participant_client.participant_uuid)

                if not result:
                    print('Error!')
                    return 'Internal server error', 500

                return {'rank': result}
            else:
                return '', 500

