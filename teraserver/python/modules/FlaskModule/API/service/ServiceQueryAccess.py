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

        # Request access from user_uuid perspective
        if from_user_uuid:
            result['admin'] = args['admin']
            user = TeraUser.get_user_by_uuid(from_user_uuid)
            if user is None:
                return gettext('Invalid user uuid'), 400

            user_access = DBManagerTeraUserAccess(user)
            result['from_user_uuid'] = from_user_uuid

            if args['with_users_uuids']:
                result['users_uuids'] = user_access.get_accessible_users_uuids(admin_only=args['admin'])

            if args['with_projects_ids']:
                result['projects_ids'] = user_access.get_accessible_projects_ids(admin_only=args['admin'])

            if args['with_participants_uuids']:
                result['participants_uuids'] = user_access.get_accessible_participants_uuids(admin_only=args['admin'])

            if args['with_devices_uuids']:
                result['devices_uuids'] = user_access.get_accessible_devices_uuids(admin_only=args['admin'])

            if args['with_sites_ids']:
                result['sites_ids'] = user_access.get_accessible_sites_ids(admin_only=args['admin'])

        # Request access from participant perspective
        if from_participant_uuid:
            if args['admin']:
                return gettext('Participant cannot be admin'), 400

            participant = TeraParticipant.get_participant_by_uuid(from_participant_uuid)
            if participant is None:
                return gettext('Invalid participant uuid'), 400

            # TODO Unused for now
            participant_access = DBManagerTeraParticipantAccess(participant)
            result['from_participant_uuid'] = from_participant_uuid

            # TODO should return users that have sessions with this participant
            if args['with_users_uuids']:
                result['users_uuids'] = []

            # TODO should return only the project containing the participant_uuid
            if args['with_projects_ids']:
                result['projects_ids'] = []

            # TODO should return participants of the same group
            if args['with_participants_uuids']:
                result['participants_uuids'] = [from_participant_uuid]

            # TODO should return devices associated to this participant
            if args['with_devices_uuids']:
                result['devices_uuids'] = []

            # TODO should return the site of the current participant's project
            if args['with_sites_ids']:
                result['sites_ids'] = []

        # Request access from device perspective
        if from_device_uuid:
            if args['admin']:
                return gettext('Device cannot be admin'), 400

            device = TeraDevice.get_device_by_uuid(from_device_uuid)
            if device is None:
                return gettext('Invalid device uuid'), 400

            # TODO unused for now
            device_access = DBManagerTeraDeviceAccess(device)
            result['from_device_uuid'] = from_device_uuid

            # TODO should return users that have sessions with this device
            if args['with_users_uuids']:
                result['users_uuids'] = []

            # TODO should return projects where device is associated
            if args['with_projects_ids']:
                result['projects_ids'] = []

            # TODO should return participants associated with this device
            if args['with_participants_uuids']:
                result['participants_uuids'] = [participant.participant_uuid
                                                for participant in device_access.get_accessible_participants()]

            # TODO devices of the same project ? sessions with devices ?
            if args['with_devices_uuids']:
                result['devices_uuids'] = [from_device_uuid]

            # TODO return sites where device is associated
            if args['with_sites_ids']:
                result['sites_ids'] = []

        return result
