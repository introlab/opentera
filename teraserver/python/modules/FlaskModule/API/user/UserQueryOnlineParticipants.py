from flask import session
from flask_restx import Resource, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from sqlalchemy.exc import InvalidRequestError
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames
from modules.DatabaseModule.DBManager import DBManager

get_parser = api.parser()
get_parser.add_argument('with_sites', type=inputs.boolean, help='Include site informations for each participant.')
get_parser.add_argument('with_projects', type=inputs.boolean, help='Include project informations for each participant.')


class UserQueryOnlineParticipants(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get online participants uuids.',
             responses={200: 'Success'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        args = get_parser.parse_args()
        user_access = DBManager.userAccess(current_user)

        try:
            accessible_participants = user_access.get_accessible_participants_uuids()

            if not self.test:
                rpc = RedisRPCClient(self.flaskModule.config.redis_config)
                status_participants = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'status_participants')
            else:
                status_participants = {accessible_participants[0]: {'online': True, 'busy': False}}

            participants_uuids = [participant_uuid for participant_uuid in status_participants]
            # Filter participants that are available to the query
            filtered_participants_uuids = list(set(participants_uuids).intersection(accessible_participants))

            # Query participants information
            participants = TeraParticipant.query.filter(TeraParticipant.participant_uuid.in_(
                filtered_participants_uuids)).order_by(TeraParticipant.participant_name.asc()).all()

            participants_json = []
            for participant in participants:
                part_json = participant.to_json(minimal=True)
                if args['with_projects']:
                    part_json['id_project'] = participant.id_project
                    part_json['project_name'] = participant.participant_project.project_name
                if args['with_sites']:
                    part_json['id_site'] = participant.participant_project.id_site
                    part_json['site_name'] = participant.participant_project.project_site.site_name
                part_json['participant_online'] = status_participants[part_json['participant_uuid']]['online']
                part_json['participant_busy'] = status_participants[part_json['participant_uuid']]['busy']
                participants_json.append(part_json)

            return participants_json

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryOnlineParticipants.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Internal server error when making RPC call.'), 500


