from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraParticipant import TeraParticipant
from opentera.db.models.TeraDevice import TeraDevice
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from flask_babel import gettext


# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user', type=int, help='ID of the user to query', default=None)
get_parser.add_argument('user_uuid', type=str, help='User uuid of the device to query', default=None)
get_parser.add_argument('id_participant', type=int, help='ID of the participant to query', default=None)
get_parser.add_argument('participant_uuid', type=str, help='Participant uuid of the device to query', default=None)
get_parser.add_argument('id_device', type=int, help='ID of the device to query', default=None)
get_parser.add_argument('device_uuid', type=str, help='Device uuid of the device to query', default=None)


class UserQueryDisconnect(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Disconnect user/participant/device from server. Use Logout for current user instead.',
             responses={200: 'Success - user/participant/device will be disconnected.',
                        400: 'No parameters specified, at least one id / uuid must be used',
                        403: 'Forbidden access. Please check that the user has access to'
                             ' the requested id/uuid.',
                        500: 'Database error'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        args = get_parser.parse_args()
        user_access = DBManager.userAccess(current_user)

        try:
            if args['id_user']:
                if args['id_user'] in user_access.get_accessible_users_ids(admin_only=True):
                    user = TeraUser.get_user_by_id(args['id_user'])
                    if user.user_uuid == current_user.user_uuid:
                        return gettext('Use Logout instead to disconnect current user'), 400
                    self.module.send_user_disconnect_module_message(user.user_uuid)
            elif args['user_uuid']:
                if args['user_uuid'] in user_access.get_accessible_users_uuids(admin_only=True):
                    user = TeraUser.get_user_by_uuid(args['user_uuid'])
                    if user.user_uuid == current_user.user_uuid:
                        return gettext('Use Logout instead to disconnect current user'), 400
                    self.module.send_user_disconnect_module_message(user.user_uuid)
            elif args['id_participant']:
                if args['id_participant'] in user_access.get_accessible_participants_ids(admin_only=True):
                    participant = TeraParticipant.get_participant_by_id(args['id_participant'])
                    self.module.send_participant_disconnect_module_message(participant.participant_uuid)
            elif args['participant_uuid']:
                if args['participant_uuid'] in user_access.get_accessible_participants_uuids(admin_only=True):
                    participant = TeraParticipant.get_participant_by_uuid(args['participant_uuid'])
                    self.module.send_participant_disconnect_module_message(participant.participant_uuid)
            elif args['id_device']:
                if args['id_device'] in user_access.get_accessible_devices_ids(admin_only=True):
                    device = TeraDevice.get_device_by_id(args['id_device'])
                    self.module.send_device_disconnect_module_message(device.device_uuid)
            elif args['device_uuid']:
                if args['device_uuid'] in user_access.get_accessible_devices_uuids(admin_only=True):
                    device = TeraDevice.get_device_by_uuid(args['device_uuid'])
                    self.module.send_device_disconnect_module_message(device.device_uuid)
            else:
                return gettext('Invalid request'), 400

            return gettext('Success'), 200

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryDisconnect.__name__,
                                         'get', 500, 'Database error', str(e))
            return '', 500

