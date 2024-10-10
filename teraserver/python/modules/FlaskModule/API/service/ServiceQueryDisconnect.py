from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraParticipant import TeraParticipant
from modules.DatabaseModule.DBManager import DBManager
from modules.DatabaseModule.DBManagerTeraServiceAccess import DBManagerTeraServiceAccess
from sqlalchemy.exc import InvalidRequestError

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user', type=int, help='ID of the user to query', default=None)
get_parser.add_argument('user_uuid', type=str, help='User uuid of the device to query', default=None)
get_parser.add_argument('id_participant', type=int, help='ID of the participant to query', default=None)
get_parser.add_argument('participant_uuid', type=str, help='Participant uuid of the device to query', default=None)
get_parser.add_argument('id_device', type=int, help='ID of the device to query', default=None)
get_parser.add_argument('device_uuid', type=str, help='Device uuid of the device to query', default=None)


class ServiceQueryDisconnect(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Disconnect user/participant/device from server.',
             responses={200: 'Success - user/participant/device will be disconnected.',
                        400: 'No parameters specified at least one id / uuid must be used',
                        403: 'Forbidden access. Please check that the service has access to'
                             ' the requested id/uuid.',
                        500: 'Database error'},
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        """
        Forcefully disconnect a user, participant or device
        """
        args = get_parser.parse_args()
        service_access: DBManagerTeraServiceAccess = DBManager.serviceAccess(current_service)

        try:
            if args['id_user']:
                if args['id_user'] in service_access.get_accessible_users_ids():
                    user = TeraUser.get_user_by_id(args['id_user'])
                    self.module.send_user_disconnect_module_message(user.user_uuid)
                else:
                    return gettext('Forbidden'), 403
            elif args['user_uuid']:
                if args['user_uuid'] in service_access.get_accessible_users_uuids():
                    user = TeraUser.get_user_by_uuid(args['user_uuid'])
                    self.module.send_user_disconnect_module_message(user.user_uuid)
                else:
                    return gettext('Forbidden'), 403

            elif args['id_participant']:
                if args['id_participant'] in service_access.get_accessible_participants_ids():
                    participant = TeraParticipant.get_participant_by_id(args['id_participant'])
                    self.module.send_participant_disconnect_module_message(participant.participant_uuid)
                else:
                    return gettext('Forbidden'), 403
            elif args['participant_uuid']:
                if args['participant_uuid'] in service_access.get_accessible_participants_uuids():
                    participant = TeraParticipant.get_participant_by_uuid(args['participant_uuid'])
                    self.module.send_participant_disconnect_module_message(participant.participant_uuid)
                else:
                    return gettext('Forbidden'), 403
            elif args['id_device']:
                if args['id_device'] in service_access.get_accessible_devices_ids():
                    device = TeraDevice.get_device_by_id(args['id_device'])
                    self.module.send_device_disconnect_module_message(device.device_uuid)
                else:
                    return gettext('Forbidden'), 403
            elif args['device_uuid']:
                if args['device_uuid'] in service_access.get_accessible_devices_uuids():
                    device = TeraDevice.get_device_by_uuid(args['device_uuid'])
                    self.module.send_device_disconnect_module_message(device.device_uuid)
                else:
                    return gettext('Forbidden'), 403
            else:
                return gettext('Invalid request'), 400

            return gettext('Success'), 200

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryDisconnect.__name__,
                                         'get', 500, 'Database error', str(e))
            return '', 500

