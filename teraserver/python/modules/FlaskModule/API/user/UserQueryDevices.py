from flask import jsonify, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraSite import TeraSite
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from modules.DatabaseModule.DBManager import DBManager, TeraDeviceProject
from flask_babel import gettext
from opentera.redis.RedisRPCClient import RedisRPCClient
from opentera.modules.BaseModule import ModuleNames

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id', type=int, help='ID of the device to query')
get_parser.add_argument('id_device', type=int, help='ID of the device to query')
get_parser.add_argument('device_uuid', type=str, help='Device uuid of the device to query')
get_parser.add_argument('uuid', type=str, help='Alias for "device_uuid"')
get_parser.add_argument('id_site', type=int, help='ID of the site from which to get all associated devices')
get_parser.add_argument('id_project', type=int, help='ID of the project from which to get all associated devices')
get_parser.add_argument('id_device_type', type=int, help='ID of device type from which to get all devices. Can be '
                                                         'combined with id_site or id_project.')
get_parser.add_argument('id_device_subtype', type=int, help='Device subtype id to get all devices of that subtype.')
get_parser.add_argument('name', type=str, help='Name of the device to query')
# get_parser.add_argument('available', type=inputs.boolean, help='Flag that indicates if only available (devices not '
#                                                                'associated to a participant) should be returned')
get_parser.add_argument('projects', type=inputs.boolean, help='Flag that indicates if associated project(s) information'
                                                              ' should be included in the returned device list')
get_parser.add_argument('enabled', type=inputs.boolean, help='Flag that limits the returned data to the enabled '
                                                             'devices.')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')
get_parser.add_argument('with_participants', type=inputs.boolean, help='Flag that indicates if associated '
                                                                       'participant(s) information should be included '
                                                                       'in the returned device list')
get_parser.add_argument('with_sites', type=inputs.boolean, help='Flag that indicates if associated site(s) information '
                                                                'should be included in the returned device list')
get_parser.add_argument('with_status', type=inputs.boolean, help='Include status information - offline, online, busy '
                                                                 'for each device')


post_parser = api.parser()
post_schema = api.schema_model('user_device', {'properties': TeraDevice.get_json_schema(),
                                               'type': 'object',
                                               'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Device ID to delete', required=True)


class UserQueryDevices(Resource):

    @staticmethod
    def _value_counter(args, ids_only=False):
        res = 0
        if not ids_only:
            for value in args.values():
                if value is not None:
                    res += 1
        else:
            for key in args.keys():
                if (key.startswith('id_') or key.find('uuid') >= 0 or key == 'name') and args[key] is not None:
                    res += 1
        return res

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get devices information. Only one of the ID parameter is supported at once. If no ID is '
                         'specified, returns all accessible devices for the logged user.',
             responses={200: 'Success - returns list of devices',
                        400: 'User Error : Too Many IDs',
                        403: 'Forbidden access',
                        500: 'Database error'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        """
        Get device information
        """
        user_access = DBManager.userAccess(current_user)
        args = get_parser.parse_args()

        if args['id']:
            args['id_device'] = args['id']

        # has_available = args.pop('available')
        has_projects = args.pop('projects')
        has_enabled = args.pop('enabled')
        has_list = args.pop('list')
        has_with_participants = args.pop('with_participants')
        has_with_sites = args.pop('with_sites')
        has_with_status = args.pop('with_status')
        id_device_type = args.pop('id_device_type')

        devices = []
        # If we have no arguments, return all accessible devices
        if self._value_counter(args=args) == 0:
            if id_device_type is not None:
                devices = user_access.query_devices_by_type(id_device_type)
            else:
                devices = user_access.get_accessible_devices()
        elif self._value_counter(args=args, ids_only=True) == 1:
            if args['id_device']:
                if args['id_device'] in user_access.get_accessible_devices_ids():
                    devices = [TeraDevice.get_device_by_id(args['id_device'])]
            if args['device_uuid']:
                if args['device_uuid'] in user_access.get_accessible_devices_uuids():
                    devices = [TeraDevice.get_device_by_uuid(args['device_uuid'])]
            if args['uuid']:
                if args['uuid'] in user_access.get_accessible_devices_uuids():
                    devices = [TeraDevice.get_device_by_uuid(args['uuid'])]
            if args['id_site']:
                devices = user_access.query_devices_for_site(args['id_site'], id_device_type, has_enabled)
            if args['id_project']:
                devices = user_access.query_devices_for_project(args['id_project'], id_device_type, has_enabled)
            if args['id_device_subtype']:
                devices = user_access.query_devices_by_subtype(args['id_device_subtype'])
            if args['name']:
                devices = [TeraDevice.get_device_by_name(args['name'])]
                for device in devices:
                    if device is None and len(devices) == 1:
                        devices = []
                        break
                    if device.id_device not in user_access.get_accessible_devices_ids():
                        devices = []
        else:
            return gettext('Too many IDs'), 400

        # if not devices:
        #     return gettext('Forbidden access'), 403
        # if args['available'] is not None:
        #     if args['available']:
        #         devices = TeraDevice.get_available_devices()
        #     else:
        #         devices = TeraDevice.get_unavailable_devices()

        try:
            device_list = []

            if has_with_status:
                # Query status
                if not self.test:
                    rpc = RedisRPCClient(self.module.config.redis_config)
                    status_devices = rpc.call(ModuleNames.USER_MANAGER_MODULE_NAME.value, 'status_devices')
                else:
                    status_devices = {}
                    for device in devices:
                        status_devices[device.device_uuid] = {'busy': False, 'online': True}

            for device in devices:
                if device is not None:
                    if has_enabled:
                        if device.device_enabled != has_enabled:
                            continue

                    if not has_list:
                        device_json = device.to_json()
                    else:
                        device_json = device.to_json(minimal=True)

                    if has_with_participants:
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
                            if not has_list:
                                part_info['project_name'] = part.participant_project.project_name
                            parts.append(part_info)
                        device_json['device_participants'] = parts

                    if has_with_sites:
                        # Add sites
                        sites_list = []
                        device_sites = user_access.query_sites_for_device(device.id_device)
                        for device_site in device_sites:
                            ignore_site_fields = []
                            if has_list:
                                ignore_site_fields = ['site_name']
                            site_json = device_site.to_json(ignore_fields=ignore_site_fields)
                            sites_list.append(site_json)

                        device_json['device_sites'] = sites_list

                    if has_projects:
                        # Add projects
                        projects_list = []
                        device_projects = TeraDeviceProject.get_projects_for_device(device.id_device)
                        for device_project in device_projects:
                            ignore_project_fields = []
                            if has_list:
                                ignore_project_fields = ['project_name']
                            project_json = device_project.to_json(ignore_fields=ignore_project_fields)
                            if not has_list:
                                project_json['project'] = device_project.device_project_project.to_json()
                            projects_list.append(project_json)

                        device_json['device_projects'] = projects_list
                    # if has_available:
                    #     if not has_available:
                    #         device_json['id_kit'] = device.device_kits[0].id_kit
                    #         device_json['kit_name'] = device.device_kits[0].kit_device_kit.kit_name
                    #         device_json['kit_device_optional'] = device.device_kits[0].kit_device_optional

                    if device.id_device_subtype is not None:
                        device_json['device_subtype'] = device.device_subtype.to_json()

                    if has_with_status:
                        if device.device_uuid in status_devices:
                            # TODO Keep for compatibility. Should only keep device_status
                            device_json['device_busy'] = status_devices[device.device_uuid]['busy']
                            device_json['device_online'] = status_devices[device.device_uuid]['online']
                            device_json['device_status'] = status_devices[device.device_uuid]
                        else:
                            # TODO Keep for compatibility. Should only keep device_status
                            device_json['device_busy'] = False
                            device_json['device_online'] = False
                            device_json['device_status'] = None

                    device_list.append(device_json)
            return jsonify(device_list)

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryDevices.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return '', 500

    @api.doc(description='Create / update devices. id_device must be set to "0" to create a new device. Only '
                         'superadmins can create new devices, site admin can update and project admin can modify config'
                         ' and notes.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified device',
                        400: 'Badly formed JSON or missing fields(id_device) in the JSON body',
                        500: 'Internal error occurred when saving device'})
    @api.expect(post_schema)
    @user_multi_auth.login_required
    def post(self):
        """
        Create / update devices
        """
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        if 'device' not in request.json:
            return gettext('Missing device'), 400

        json_device = request.json['device']

        # Validate if we have an id
        if 'id_device' not in json_device:
            return gettext('Missing id_device'), 400

        # Manage device projects
        device_projects_ids = []
        update_device_projects = False
        if 'device_projects' in json_device:
            # if json_device['id_device'] > 0:
            #     return gettext('Device projects may be specified with that API only on a new device. Use '
            #                    '"device_projects" instead'), 400
            device_projects = json_device.pop('device_projects')
            # Check if the current user is site admin in all of those projects
            device_projects_ids = [project['id_project'] for project in device_projects]

            for project_id in device_projects_ids:
                project = TeraProject.get_project_by_id(project_id)
                if user_access.get_site_role(project.id_site) != 'admin':
                    return gettext('No site admin access for at a least one project in the list'), 403
            update_device_projects = True

        device_sites_ids = []
        update_device_sites = False
        if 'device_sites' in json_device:
            device_sites = json_device.pop('device_sites')
            # Check if the current user is site admin in all of those sites
            device_sites_ids = [site['id_site'] for site in device_sites]

            for site_id in device_sites_ids:
                if user_access.get_site_role(site_id) != 'admin':
                    return gettext('No site admin access for at a least one site in the list'), 403
            update_device_sites = True

        # New devices can only be added by super admins or by site admins
        if json_device['id_device'] == 0:
            if not current_user.user_superadmin and not update_device_projects and not update_device_sites:
                return gettext('Forbidden'), 403
        else:
            # Check if current user can modify the posted device
            if json_device['id_device'] not in user_access.get_accessible_devices_ids(admin_only=True):
                return gettext('Forbidden'), 403

            # Check if the user if a site admin of the projects, otherwise limit what can be updated
            current_device = TeraDevice.get_device_by_id(json_device['id_device'])
            is_site_admin = current_user.user_superadmin
            for project in current_device.device_projects:
                if user_access.get_site_role(project.project_site.id_site) == 'admin':
                    is_site_admin = True
                    break

            # User is not site admin - strip everything that can't be modified by a project admin
            if not is_site_admin:
                allowed_fields = ['id_device', 'device_config', 'device_notes']
                json_device2 = {}
                for field in allowed_fields:
                    if field in json_device:
                        json_device2[field] = json_device[field]
                json_device = json_device2

        # Do the update!
        new_device = None
        if json_device['id_device'] > 0:
            # Already existing
            try:
                TeraDevice.update(json_device['id_device'], json_device)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryDevices.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # New
            try:
                new_device = TeraDevice()
                new_device.from_json(json_device)
                TeraDevice.insert(new_device)
                # Update ID for further use
                json_device['id_device'] = new_device.id_device
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryDevices.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        update_device = TeraDevice.get_device_by_id(json_device['id_device'])

        # Update device sites, if needed
        if update_device_sites:
            if new_device:
                # New device - directly update the list
                update_device.device_sites = [TeraSite.get_site_by_id(site_id) for site_id in device_sites_ids]
                update_device.commit()
            else:
                # Updated device - first, we add sites not already there
                update_device_current_sites = [site.id_site for site in update_device.device_sites]
                sites_to_add = set(device_sites_ids).difference(update_device_current_sites)
                update_device.device_sites.extend([TeraSite.get_site_by_id(site_id) for site_id in sites_to_add])

                # Then, we delete sites that the current user has access, but are not present in the posted list,
                # without touching sites already there
                current_user_sites = user_access.get_accessible_sites_ids(admin_only=True)
                update_device_current_sites.extend(list(sites_to_add))
                missing_sites = set(current_user_sites).difference(device_sites_ids)
                for site_id in missing_sites:
                    update_device.device_sites.remove(TeraSite.get_site_by_id(site_id))
                update_device.commit()

        # Update device projects, if needed
        if update_device_projects:
            if new_device:
                # New device - directly update the list
                update_device.device_projects = [TeraProject.get_project_by_id(project_id)
                                                 for project_id in device_projects_ids]
                update_device.commit()
            else:
                # Updated device - first, we add projects not already there
                update_device_current_projects = [project.id_project for project in update_device.device_projects]
                projects_to_add = set(device_projects_ids).difference(update_device_current_projects)
                update_device.device_projects.extend([TeraProject.get_project_by_id(project_id)
                                                     for project_id in projects_to_add])

                # Then, we delete projects that the current user has access, but are not present in the posted list,
                # without touching projects already there
                current_user_projects = user_access.get_accessible_projects_ids(admin_only=True)
                update_device_current_projects.extend(list(projects_to_add))
                missing_projects = set(current_user_projects).difference(device_projects_ids)
                for project_id in missing_projects:
                    if project_id in update_device_current_projects:
                        update_device.device_projects.remove(TeraProject.get_project_by_id(project_id))
                update_device.commit()

        return [update_device.to_json()]

    @api.doc(description='Delete a specific device',
             responses={200: 'Success',
                        400: 'Wrong ID/ No ID',
                        403: 'Logged user can\'t delete device (can delete if superadmin)',
                        500: 'Device not found or database error.'})
    @api.expect(delete_parser)
    @user_multi_auth.login_required
    def delete(self):
        """
        Delete a specific device
        """
        user_access = DBManager.userAccess(current_user)
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        full_delete = current_user.user_superadmin
        dif_projects = []
        device_to_del = TeraDevice.get_device_by_id(id_todel)
        if not device_to_del:
            return gettext('Invalid id'), 400
        if not current_user.user_superadmin:
            # We must check if we need to remove projects from that device or delete it completely
            access_projects = user_access.get_accessible_projects(admin_only=True)
            if not access_projects:
                return gettext('Forbidden'), 403
            dif_projects = set(device_to_del.device_projects).difference(access_projects)
            if len(dif_projects) == 0:
                full_delete = True

        if full_delete:
            # If we are here, we are allowed to delete. Do so.
            try:
                TeraDevice.delete(id_todel=id_todel)
            except exc.IntegrityError as e:

                self.module.logger.log_warning(self.module.module_name, UserQueryDevices.__name__, 'delete', 500,
                                               'Integrity error', str(e))

                # Causes that could make an integrity error when deleting:
                # - Associated with sessions
                # - Associated with assets
                # - Associated with participants
                if 't_devices_participants' in str(e.args):
                    return gettext('Can\'t delete device: please delete all participants association before deleting.'
                                   ), 500
                if 't_sessions_devices' in str(e.args):
                    return gettext('Can\'t delete device: please remove all sessions referring to that device before '
                                   'deleting.'), 500
                if 't_sessions_id_creator' in str(e.args):
                    return gettext('Can\'t delete device: please remove all sessions created by that device before '
                                   'deleting.'), 500
                if 't_assets' in str(e.args):
                    return gettext('Can\'t delete device: please delete all assets created by that device before '
                                   'deleting.'), 500
                if 't_tests' in str(e.args):
                    return gettext('Can\'t delete device: please delete all tests created by that device before '
                                   'deleting.'), 500

                return gettext('Can\'t delete device: please remove all related sessions, assets and tests before '
                               'deleting.'), 500

            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryDevices.__name__,
                                             'delete', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # Only remove projects from that device so that device is "apparently" deleted to the user
            projects = device_to_del.device_projects
            for project in projects:
                if project.id_project not in dif_projects:
                    device_to_del.device_projects.remove(project)
            device_to_del.commit()

        return gettext('Device successfully deleted'), 200
