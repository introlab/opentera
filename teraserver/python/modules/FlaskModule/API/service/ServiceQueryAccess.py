from flask import request
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from modules.DatabaseModule.DBManager import DBManager
from modules.DatabaseModule.DBManager import DBManagerTeraUserAccess
from modules.DatabaseModule.DBManager import DBManagerTeraParticipantAccess
from modules.DatabaseModule.DBManager import DBManagerTeraDeviceAccess

# Parser definition(s)
get_parser = api.parser()
# Source uuid
get_parser.add_argument('from_user_uuid', type=str, help='Participant uuid requesting access')
get_parser.add_argument('from_participant_uuid', type=str, help='Participant uuid requesting access')
get_parser.add_argument('from_device_uuid', type=str, help='Participant uuid requesting access')

# Additional flags
get_parser.add_argument('with_users_uuids', type=inputs.boolean, help='List accessible user uuids',
                        default=False)
get_parser.add_argument('with_projects_ids', type=inputs.boolean, help='List accessible project ids',
                        default=False)
get_parser.add_argument('with_participants_uuids', type=inputs.boolean, help='List accessible participants uuids',
                        default=False)
get_parser.add_argument('with_devices_uuids', type=inputs.boolean, help='List accessible device uuids',
                        default=False)
get_parser.add_argument('with_sites_ids', type=inputs.boolean, help='List accessible site ids',
                        default=False)
get_parser.add_argument('admin', type=inputs.boolean, help='List only accessible with admin rights',
                        default=False)


class ServiceQueryAccess(Resource):

    # Handle auth
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @LoginModule.service_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return access information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged service doesn\'t have permission to access the requested data'})
    def get(self):

        service_access = DBManager.serviceAccess(current_service)
        args = get_parser.parse_args()

        # Host information can be overwritten by NGINX
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']
        if 'X_EXTERNALSERVER' in request.headers:
            servername = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        from_user_uuid = None
        from_participant_uuid = None
        from_device_uuid = None

        # Note that None is considered False
        if not any(args.values()):
            return gettext('No arguments specified'), 400

        # One of the three from_x_uuid must be present
        if args['from_user_uuid']:
            from_user_uuid = args['from_user_uuid']
        elif args['from_participant_uuid']:
            from_participant_uuid = args['from_participant_uuid']
        elif 'from_device_uuid' in args:
            from_device_uuid = args['from_device_uuid']
        else:
            return gettext('Missing at least one from argument for uuids'), 400

        # Copy query flags
        result = dict()
        result['admin'] = args['admin']

        if from_user_uuid:
            user_access = DBManagerTeraUserAccess(TeraUser.get_user_by_uuid(from_user_uuid))
            result['from_user_uuid'] = from_user_uuid

        if from_participant_uuid:
            participant_access = DBManagerTeraParticipantAccess(
                TeraParticipant.get_participant_by_uuid(from_participant_uuid))
            result['from_participant_uuid'] = from_participant_uuid

        if from_device_uuid:
            device_access = DBManagerTeraDeviceAccess(TeraDevice.get_device_by_uuid(from_device_uuid))
            result['from_device_uuid'] = from_device_uuid

        return result
