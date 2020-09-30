from flask import session, request
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from libtera.db.models import TeraDeviceType
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraDeviceType import TeraDeviceType
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from modules.DatabaseModule.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_device_type', type=int, help='ID of the device type')
get_parser.add_argument('list', type=inputs.boolean, help='List of all device types')

# post_parser = reqparse.RequestParser()
# post_parser.add_argument('device_type', type=str, location='json', help='Device type to create / update',
#                          required=True)
post_schema = api.schema_model('id_device_type', {'properties': TeraDeviceType.get_json_schema(),
                                                  'type': 'object',
                                                  'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Device type ID to delete', required=True)


class UserQueryDeviceTypes(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get devices types. Only one of the ID parameter is supported at once. If list True,'
                         'return all the devices',
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
        device_types = []

        # If we have no arguments, return all accessible devices
        if args['id_device_type'] is None and args['list'] is None and args['device_type_key']:
            return gettext('Missing parameters'), 400

        if args['list']:
            device_types = user_access.get_accessible_devices_types()

        # elif args['device_type_key']

        elif args['id_device_type']:
            device_types = TeraDeviceType.query.filter(TeraDeviceType.id_device_type.
                                                       in_(user_access.get_accessible_devices_types_ids())). \
                filter_by(id_device_type=args['id_device_type']).all()
            if not args['id_device_type'] in user_access.get_accessible_devices_types_ids():
                return gettext('No access to device type'), 403
        try:
            device_types_list = []
            for dt in device_types:
                dt_json = dt.to_json()
                device_types_list.append(dt_json)
            return device_types_list

        except InvalidRequestError:
            return '', 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create / update devices types. id_device_type must be set to "0" to create a new '
                         'type. Only site admins can create new devices types.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified device type',
                        400: 'Badly formed JSON or missing fields(id_device_name or id_device_type) in the JSON '
                             'body',
                        500: 'Internal error occured when saving device type',
                        501: 'Device already created'})
    def post(self):
        # parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_device_type = request.json['device_type']

        # Validate if we have an id
        if 'id_device_type' not in json_device_type:
            return gettext('Missing id_device_type'), 400

        if json_device_type['id_device_type'] == 0:
            try:
                new_device_type = TeraDeviceType()
                new_device_type.device_type_name = json_device_type['device_type_name']
                new_device_type.device_type_key = json_device_type['device_type_key']
                TeraDeviceType.insert(new_device_type)
                return gettext('New device type created'), 200

            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return gettext('Device Already created'), 501

        # Check if current user can modify the posted device
        if json_device_type['id_device_type'] not in user_access.get_accessible_devices_types_ids(admin_only=True):
            return gettext('Forbidden'), 403

        # Do the update!
        if json_device_type['id_device_type'] > 0:
            # Already existing
            try:
                TeraDeviceType.update(json_device_type['id_device_type'], json_device_type)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return gettext('Database error'), 500
        else:
            # New
            try:
                new_device_type = TeraDeviceType()
                new_device_type.from_json(json_device_type)
                TeraDeviceType.insert(new_device_type)
                # Update ID for further use
                json_device_type['id_device_type'] = new_device_type.id_device_type
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return gettext('Database error'), 500

        # TODO: Publish update to everyone who is subscribed to devices update...
        update_device = TeraDeviceType.get_device_type_by_id(json_device_type['id_device_type'])

        return [update_device.to_json()]

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific device type',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete device type (can delete if site admin)',
                        500: 'Device type not found or database error.'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        todel = TeraDeviceType.get_device_type_by_id(id_todel)
        if not todel:
            return gettext('Device type not found'), 500

        if todel.id_device_type not in user_access.get_accessible_devices_types_ids(admin_only=True):
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraDeviceType.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return gettext('Database error'), 500

        return '', 200
