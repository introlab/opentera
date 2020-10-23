from flask import session, request
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraDeviceSubType import TeraDeviceSubType
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from modules.DatabaseModule.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_device_subtype', type=int, help='ID of the device subtype to query')
get_parser.add_argument('id_device_type', type=int, help='ID of the device type from which to get all subtypes')
get_parser.add_argument('list', type=inputs.boolean, help='Return minimal information')

# post_parser = reqparse.RequestParser()
# post_parser.add_argument('device_subtype', type=str, location='json', help='Device subtype to create / update',
#                          required=True)
post_schema = api.schema_model('user_device_subtype', {'properties': TeraDeviceSubType.get_json_schema(),
                                                       'type': 'object',
                                                       'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Device subtype ID to delete', required=True)


class UserQueryDeviceSubTypes(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get devices subtypes. Only one of the ID parameter is supported at once.',
             responses={200: 'Success - returns list of devices subtypes',
                        400: 'No parameters specified at least one id must be used',
                        403: 'Forbidden access to the device type specified. Please check that the user has access to a'
                             ' session type containing that device type.',
                        500: 'Database error'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()
        has_list = args.pop('list')

        #  if we have 2 IDs, return error
        if args['id_device_subtype'] is not None and args['id_device_type'] is not None:
            return gettext('Too Many IDs'), 400

        if args['id_device_subtype'] is not None:
            if args['id_device_subtype'] in user_access.get_accessible_devices_subtypes_ids():
                device_subtypes = TeraDeviceSubType.query.filter(TeraDeviceSubType.id_device_type.
                                                                 in_(user_access.get_accessible_devices_types_ids())).\
                    filter_by(id_device_subtype=args['id_device_subtype']).all()
            else:
                return gettext('No access to device subtype'), 403
        elif args['id_device_type'] is not None:
            # Check if has access to the id_device_type
            if args['id_device_type'] in user_access.get_accessible_devices_types_ids():
                device_subtypes = TeraDeviceSubType.get_device_subtypes_for_type(args['id_device_type'])
            else:
                return gettext('No access to device type'), 403
        else:
            # Return all available device subtypes
            device_subtypes = user_access.get_accessible_devices_subtypes();

        try:
            device_subtypes_list = []
            for dst in device_subtypes:
                dst_json = dst.to_json(minimal=has_list)
                device_subtypes_list.append(dst_json)
                # if dst is not None:
                #     if has_list:
                #         dst_json = dst.to_json(minimal=True)
                #         device_subtypes_list.append(dst_json)
                #     else:
                #         dst_json = dst.to_json()
                #         device_subtypes_list.append(dst_json)
            return device_subtypes_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryDeviceSubTypes.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return '', 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create / update devices subtypes. id_device_subtype must be set to "0" to create a new '
                         'subtype. Only site admins can create new devices subtypes.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified device subtype',
                        400: 'Badly formed JSON or missing fields(id_device_subtype or id_device_type) in the JSON '
                             'body',
                        500: 'Internal error occured when saving device subtype'})
    def post(self):
        # parser = post_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_device_subtype = request.json['device_subtype']

        # Validate if we have an id
        if 'id_device_subtype' not in json_device_subtype:
            return gettext('Missing id_device_subtype'), 400

        if not current_user.user_superadmin:
            return gettext('Forbidden'), 403

        # Do the update!
        if json_device_subtype['id_device_subtype'] > 0:
            # Already existing
            try:
                json_device_subtype['id_device_type'] = TeraDeviceSubType.\
                    get_device_subtype(json_device_subtype['id_device_subtype']).id_device_type
                TeraDeviceSubType.update(json_device_subtype['id_device_subtype'], json_device_subtype)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryDeviceSubTypes.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # New
            try:
                new_device_subtype = TeraDeviceSubType()
                new_device_subtype.from_json(json_device_subtype)
                TeraDeviceSubType.insert(new_device_subtype)
                # Update ID for further use
                json_device_subtype['id_device_subtype'] = new_device_subtype.id_device_subtype
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryDeviceSubTypes.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        # TODO: Publish update to everyone who is subscribed to devices update...
        update_device = TeraDeviceSubType.get_device_subtype(json_device_subtype['id_device_subtype'])

        return [update_device.to_json()]

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific device subtype',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete device subtype (can delete if site admin)',
                        500: 'Device subtype not found or database error.'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        todel = TeraDeviceSubType.get_device_subtype(id_todel)
        if not todel:
            return gettext('Device subtype not found'), 400
        
        if not user_access.user.user_superadmin:
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraDeviceSubType.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryDeviceSubTypes.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return gettext('Device subtype successfully deleted'), 200
