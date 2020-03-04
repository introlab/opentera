from flask import jsonify, session, request
from flask_restplus import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraDevice import TeraDevice
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from libtera.db.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_device', type=int, help='ID of the device to query')
get_parser.add_argument('id_site', type=int, help='ID of the site from which to get all associated devices')
get_parser.add_argument('id_project', type=int, help='ID of the project from which to get all associated devices')
get_parser.add_argument('device_type', type=int, help='ID of device type from which to get all devices. Can be '
                                                      'combined with id_site or id_project.')
get_parser.add_argument('available', type=inputs.boolean, help='Flag that indicates if only available (devices not '
                                                               'associated to a participant) should be returned')
get_parser.add_argument('participants', type=inputs.boolean, help='Flag that indicates if associated participant(s) '
                                                                  'information should be included in the returned '
                                                                  'device list')
get_parser.add_argument('sites', type=inputs.boolean, help='Flag that indicates if associated site(s) information '
                                                           'should be included in the returned device list')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')

post_parser = reqparse.RequestParser()
post_parser.add_argument('device', type=str, location='json', help='Device to create / update', required=True)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Device ID to delete', required=True)


class QueryDevices(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get devices information. Only one of the ID parameter is supported at once. If no ID is '
                         'specified, returns all accessible devices for the logged user.',
             responses={200: 'Success - returns list of devices',
                        500: 'Database error'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()

        devices = []
        # If we have no arguments, return all accessible devices
        if not args['id_device'] and not args['id_site'] and not args['device_type'] and not args['id_project']:
            devices = user_access.get_accessible_devices()
        elif args['id_device']:
            devices = [user_access.query_device_by_id(device_id=args['id_device'])]
        elif args['id_site']:
            # Check if has access to the requested site
            devices = user_access.query_devices_for_site(args['id_site'], args['device_type'])
        elif args['id_project']:
            devices = user_access.query_devices_for_project(args['id_project'], args['device_type'])
        elif args['device_type']:
            devices = user_access.query_devices_by_type(args['device_type'])

        # if args['available'] is not None:
        #     if args['available']:
        #         devices = TeraDevice.get_available_devices()
        #     else:
        #         devices = TeraDevice.get_unavailable_devices()

        try:
            device_list = []
            for device in devices:
                if device is not None:
                    if args['list'] is None:
                        device_json = device.to_json()
                    else:
                        device_json = device.to_json(minimal=True)

                    if args['participants'] is not None:
                        # Add participants information to the device, is available
                        dev_participants = user_access.query_participants_for_device(device.id_device)
                        parts = []
                        for part in dev_participants:
                            part_info = {'id_participant': part.id_participant,
                                         'participant_name': part.participant_name,
                                         'id_project': part.participant_project.id_project
                                         }
                            # if args['list'] is None:
                            #    part_info['participant_name'] = part.participant_name
                            # part_info['id_project'] = part.participant_participant_group.participant_group_project.\
                            #     id_project
                            if args['list'] is None:
                                part_info['project_name'] = part.participant_project.project_name
                            parts.append(part_info)
                        device_json['device_participants'] = parts

                    if args['sites'] is not None:
                        # Add sites
                        sites_list = []
                        device_sites = user_access.query_sites_for_device(device.id_device)
                        for device_site in device_sites:
                            ignore_site_fields = []
                            if args['list'] is not None:
                                ignore_site_fields = ['site_name']
                            site_json = device_site.to_json(ignore_fields=ignore_site_fields)
                            sites_list.append(site_json)

                        device_json['device_sites'] = sites_list
                    # if args['available'] is not None:
                    #     if not args['available']:
                    #         device_json['id_kit'] = device.device_kits[0].id_kit
                    #         device_json['kit_name'] = device.device_kits[0].kit_device_kit.kit_name
                    #         device_json['kit_device_optional'] = device.device_kits[0].kit_device_optional

                    if device.id_device_subtype is not None:
                        device_json['device_subtype'] = device.device_subtype.to_json()
                    device_list.append(device_json)
            return jsonify(device_list)

        except InvalidRequestError:
            return '', 500

    @user_multi_auth.login_required
    @api.expect(post_parser)
    @api.doc(description='Create / update devices. id_device must be set to "0" to create a new device. Only '
                         'superadmins can create new devices.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified device',
                        400: 'Badly formed JSON or missing fields(id_device) in the JSON body',
                        500: 'Internal error occured when saving device'})
    def post(self):
        # parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_device = request.json['device']

        # Validate if we have an id
        if 'id_device' not in json_device:
            return '', 400
        # New devices can only be added by super admins
        if json_device['id_device'] == 0:
            if not current_user.user_superadmin:
                return '', 403
        else:
            # Check if current user can modify the posted device
            if json_device['id_device'] not in user_access.get_accessible_devices_ids(admin_only=True):
                return '', 403

        # Do the update!
        if json_device['id_device'] > 0:
            # Already existing
            try:
                TeraDevice.update(json_device['id_device'], json_device)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # New
            try:
                new_device = TeraDevice()
                new_device.from_json(json_device)
                TeraDevice.insert(new_device)
                # Update ID for further use
                json_device['id_device'] = new_device.id_device
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        # TODO: Publish update to everyone who is subscribed to devices update...
        update_device = TeraDevice.get_device_by_id(json_device['id_device'])

        return jsonify([update_device.to_json()])

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific device',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete device (can delete if superadmin)',
                        500: 'Device not found or database error.'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # if user_access.query_device_by_id(device_id=id_todel) is None:
        if not current_user.user_superadmin:
            return '', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraDevice.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200
