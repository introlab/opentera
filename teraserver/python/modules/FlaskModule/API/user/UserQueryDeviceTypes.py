from flask import session, request
from flask_babel import gettext
from flask_restx import Resource, reqparse, inputs
from sqlalchemy import exc
from sqlalchemy.exc import InvalidRequestError

from opentera.db.models import TeraDeviceType
from opentera.db.models.TeraDeviceType import TeraDeviceType
from opentera.db.models.TeraUser import TeraUser
from modules.DatabaseModule.DBManager import DBManager
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.LoginModule.LoginModule import user_multi_auth

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_device_type', type=int, help='ID of the device type')
get_parser.add_argument('device_type_key', type=str, help='Key of the device type')
get_parser.add_argument('list', type=inputs.boolean, help='List of all device types')


# post_parser = reqparse.RequestParser()
# post_parser.add_argument('id_device_type', type=str, location='json', help='Device type to create / update',
#                          required=True)
post_schema = api.schema_model('device_type', {'properties': TeraDeviceType.get_json_schema(),
                                                  'type': 'object',
                                                  'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Device type ID to delete')
delete_parser.add_argument('device_type_key', type=str, help='Unique device key to delete')


class UserQueryDeviceTypes(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get devices types. Only one of the ID parameter is supported at once.'
                         ' The ID is dominant on the device_type_key',
             responses={200: 'Success - returns list of devices types',
                        400: 'No parameters specified at least one id must be used',
                        403: 'Forbidden access to the device type specified. Please check that the user has access to a'
                             ' session type containing that device type.',
                        500: 'Database error'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = get_parser
        args = parser.parse_args()
        device_type = []

        # If we have no arguments, return all accessible device types
        if args['id_device_type'] is None and args['device_type_key'] is None:
            device_type = user_access.get_accessible_devices_types()

        elif args['id_device_type']:
            if args['id_device_type'] in user_access.get_accessible_devices_types_ids():
                device_type = [TeraDeviceType.get_device_type_by_id(args['id_device_type'])]
            else:
                return gettext('Unexisting ID/Forbidden access'), 403
        elif args['device_type_key']:
            if args['device_type_key'] in user_access.get_accessible_devices_types_keys():
                device_type = [TeraDeviceType.get_device_type_by_key(args['device_type_key'])]
            else:
                return gettext('Unexisting ID/Forbidden access'), 403
        try:
            device_type_list = []
            for dt in device_type:
                if args['list']:
                    device_type_list.append(dt.to_json(minimal=True))
                else:
                    device_type_list.append(dt.to_json())
            return device_type_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryDeviceTypes.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Database Error'), 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create / update devices types. id_device_type must be set to "0" to create a new '
                         'type. Only site admins can create new devices types.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified device type',
                        400: 'Badly formed JSON or missing fields(id_device_name or id_device_type) in the JSON '
                             'body',
                        500: 'Internal error occured when saving device type',})
    def post(self):
        # parser = post_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_device_type = request.json['device_type']

        # Validate if we have an id
        if 'id_device_type' not in json_device_type:
            return gettext('Missing id_device_type'), 400

        if not current_user.user_superadmin:
            return gettext('Forbidden'), 403

        # Do the update!
        if json_device_type['id_device_type'] > 0:
            # Already existing
            try:
                TeraDeviceType.update(json_device_type['id_device_type'], json_device_type)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryDeviceTypes.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # New
            try:
                new_device_type = TeraDeviceType()
                new_device_type.from_json(json_device_type)
                TeraDeviceType.insert(new_device_type)
                # Update ID for further use
                json_device_type['id_device_type'] = new_device_type.id_device_type
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryDeviceTypes.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        # TODO: Publish update to everyone who is subscribed to devices update...
        update_device = TeraDeviceType.get_device_type_by_id(json_device_type['id_device_type'])

        return [update_device.to_json()]

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific device type',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete device type (can delete if site admin)',
                        500: 'Device type not found or database error.',
                        501: 'Tried to delete with 2 parameters'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        args = parser.parse_args()
        # To accomodate the 'delete_with_http_auth' function which uses id as args, the id_device_type is rename as id
        # If not argument or both argument incorrect
        if not any([args['id'], args['device_type_key']]):
            return gettext('Missing arguments'), 400

        if args['id'] and args['device_type_key']:
            return gettext('Tried to delete with 2 parameters'), 400

        elif args['id']:
            device_type_to_del = TeraDeviceType.get_device_type_by_id(args['id'])

        elif args['device_type_key']:
            device_type_to_del = TeraDeviceType.get_device_type_by_key(args['device_type_key'])
        else:
            return gettext('Device type not found'), 400

        # if device_type_to_del.id_device_type in user_access.get_accessible_devices_types_ids():
        if user_access.user.user_superadmin:
            try:
                TeraDeviceType.delete(id_todel=device_type_to_del.id_device_type)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryDeviceTypes.__name__,
                                             'delete', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            return gettext('Forbidden'), 403

        return gettext('Device type successfully deleted'), 200
