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
get_parser.add_argument('with_users', type=inputs.boolean, help='List accessible users', default=False)
get_parser.add_argument('with_projects', type=inputs.boolean, help='List accessible projects', default=False)
get_parser.add_argument('with_participants', type=inputs.boolean, help='List accessible participants', default=False)
get_parser.add_argument('with_devices', type=inputs.boolean, help='List accessible device', default=False)
get_parser.add_argument('with_sites', type=inputs.boolean, help='List accessible site', default=False)
get_parser.add_argument('admin', type=inputs.boolean, help='List only accessible with admin rights', default=False)
get_parser.add_argument('with_names', type=inputs.boolean, help='Also includes the names of the returned items',
                        default=False)


class ServiceQueryAccess(Resource):

    # Handle auth
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @api.expect(get_parser)
    @api.doc(description='Return access information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged service doesn\'t have permission to access the requested data'})
    @LoginModule.service_token_or_certificate_required
    def get(self):

        service_access = DBManager.serviceAccess(current_service)
        args = get_parser.parse_args()

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

            if args['with_users']:
                if not args['with_names']:
                    result['users'] = [{'uuid': user_uuid} for user_uuid in
                                       user_access.get_accessible_users_uuids(admin_only=args['admin'])]
                else:
                    users = user_access.get_accessible_users(admin_only=args['admin'])
                    result['users'] = [{'uuid': user.user_uuid, 'name': user.get_fullname()} for user in users]

            if args['with_projects']:
                if not args['with_names']:
                    result['projects'] = [{'id': id_project} for id_project in
                                          user_access.get_accessible_projects_ids(admin_only=args['admin'])]
                else:
                    projects = user_access.get_accessible_projects(admin_only=args['admin'])
                    result['projects'] = [{'id': proj.id_project, 'name': proj.project_name} for proj in projects]

            if args['with_participants']:
                if not args['with_names']:
                    result['participants'] = [{'uuid': part_uuid} for part_uuid in
                                              user_access.get_accessible_participants_uuids(admin_only=args['admin'])]
                else:
                    participants = user_access.get_accessible_participants(admin_only=args['admin'])
                    result['participants'] = [{'uuid': part.participant_uuid, 'name': part.participant_name}
                                              for part in participants]

            if args['with_devices']:
                if not args['with_names']:
                    result['devices'] = [{'uuid': dev_uuid} for dev_uuid in
                                         user_access.get_accessible_devices_uuids(admin_only=args['admin'])]
                else:
                    devices = user_access.get_accessible_devices(admin_only=args['admin'])
                    result['devices'] = [{'uuid': dev.device_uuid, 'name': dev.device_name} for dev in devices]

            if args['with_sites']:
                if not args['with_names']:
                    result['sites'] = [{'id': id_site} for id_site in
                                        user_access.get_accessible_sites_ids(admin_only=args['admin'])]
                else:
                    sites = user_access.get_accessible_sites(admin_only=args['admin'])
                    result['sites'] = [{'id': site.id_site, 'name': site.site_name} for site in sites]

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
            if args['with_users']:
                result['users'] = []

            # TODO should return only the project containing the participant_uuid
            if args['with_projects']:
                result['projects'] = []

            # TODO should return participants of the same group
            if args['with_participants']:
                if not args['with_names']:
                    result['participants'] = [{'uuid': from_participant_uuid}]
                else:
                    participant = TeraParticipant.get_participant_by_uuid(from_participant_uuid)
                    result['participants'] = [{'uuid': from_participant_uuid, 'name': participant.participant_name}]

                    # TODO should return devices associated to this participant
            if args['with_devices']:
                result['devices'] = []

            # TODO should return the site of the current participant's project
            if args['with_sites']:
                result['sites'] = []

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
            if args['with_users']:
                result['users'] = []

            # TODO should return projects where device is associated
            if args['with_projects']:
                result['projects'] = []

            # TODO should return participants associated with this device
            if args['with_participants']:
                if not args['with_names']:
                    result['participants'] = [{'uuid': participant.participant_uuid} for participant
                                              in device_access.get_accessible_participants()]
                else:
                    participants = device_access.get_accessible_participants()
                    result['participants'] = [{'uuid': part.participant_uuid, 'name': part.participant_name}
                                              for part in participants]

            # TODO devices of the same project ? sessions with devices ?
            if args['with_devices']:
                if not args['with_names']:
                    result['devices'] = [{'uuid': from_device_uuid}]
                else:
                    device = TeraDevice.get_device_by_uuid(from_device_uuid)
                    result['devices'] = [{'uuid': from_device_uuid, 'name': device.device_name}]

            # TODO return sites where device is associated
            if args['with_sites']:
                result['sites'] = []

        return result
