from flask import session
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.redis.RedisRPCClient import RedisRPCClient
from modules.BaseModule import ModuleNames
from modules.DatabaseModule.DBManager import DBManager

get_parser = api.parser()
get_parser.add_argument('with_busy', type=inputs.boolean, help='Also return participants that are busy.')


class UserQueryOnlineParticipants(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get online participants uuids.',
             responses={200: 'Success'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        parser = get_parser
        args = parser.parse_args()
        user_access = DBManager.userAccess(current_user)

        try:
            # rpc = RedisRPCClient(self.flaskModule.config.redis_config)
            # online_participants = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_participants')
            #
            # # Filter participants that are available to the query
            # participant_uuids = list(set(online_participants).intersection(user_access.
            #                                                                get_accessible_participants_uuids()))
            #
            # return participant_uuids

            accessible_participants = user_access.get_accessible_participants_uuids()
            rpc = RedisRPCClient(self.flaskModule.config.redis_config)
            online_parts = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'online_participants')

            # Filter participants that are available to the query
            online_part_uuids = list(set(online_parts).intersection(accessible_participants))

            # Query user information
            participants = TeraParticipant.query.filter(TeraParticipant.participant_uuid.in_(online_part_uuids)).all()
            parts_json = [part.to_json(minimal=True) for part in participants]
            for part in parts_json:
                part['participant_online'] = True

            # Also query busy participants?
            if args['with_busy']:
                busy_participants = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'busy_participants')

                # Filter participants that are available to the query
                busy_part_uuids = list(set(busy_participants).intersection(accessible_participants))

                # Query user information
                busy_parts = TeraParticipant.query.filter(TeraParticipant.participant_uuid.in_(busy_part_uuids)).all()
                busy_parts_json = [part.to_json(minimal=True) for part in busy_parts]
                for part in busy_parts_json:
                    part['participant_busy'] = True
                parts_json.extend(busy_parts_json)

            return parts_json

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryOnlineParticipants.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Internal server error when making RPC call.'), 500

    # def post(self):
    #     return '', 501
    #
    # def delete(self):
    #     return '', 501

