from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraDeviceProject import TeraDeviceProject
from opentera.db.models.TeraDeviceSite import TeraDeviceSite
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraProject import TeraProject
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc, inspect
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_device', type=int, help='ID of the device from which to request all associated projects'
                        )
get_parser.add_argument('id_project', type=int, help='ID of the project from which to get all associated devices')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information '
                                                          '(ids only)')

get_parser.add_argument('with_projects', type=inputs.boolean, help='Used with id_device. Also return projects that '
                                                                   'don\'t have any association with that device')
get_parser.add_argument('with_devices', type=inputs.boolean, help='Used with id_project. Also return devices that '
                                                                  'don\'t have any association with that project')
get_parser.add_argument('with_sites', type=inputs.boolean, help='Used with id_device. Also return site information '
                                                                'of the returned projects.')


post_parser = api.parser()

post_schema = api.schema_model('user_device_project', {'properties': TeraDeviceProject.get_json_schema(),
                                                       'type': 'object',
                                                       'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific device-project association ID to delete. Be careful: this'
                                                ' is not the device or the project ID, but the ID of the '
                                                'association itself!', required=True)


class UserQueryDeviceProjects(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get devices that are associated with a project. Only one "ID" parameter required and '
                         'supported at once.',
             responses={200: 'Success - returns list of devices - project association',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error occurred when loading devices for projects'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        user_access = DBManager.userAccess(current_user)
        args = get_parser.parse_args()

        device_project = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        if args['id_device']:
            if args['id_device'] in user_access.get_accessible_devices_ids():
                device_project = user_access.query_devices_projects_for_device(device_id=args['id_device'],
                                                                               include_other_projects=
                                                                               args['with_projects'])
        elif args['id_project']:
            if args['id_project'] in user_access.get_accessible_projects_ids():
                device_project = user_access.query_devices_projects_for_project(project_id=args['id_project'],
                                                                                include_other_devices=
                                                                                args['with_devices'])
        try:
            device_project_list = []
            accessible_part_ids = user_access.get_accessible_participants_ids()
            for dp in device_project:
                json_dp = dp.to_json()

                if args['list'] is None:
                    obj_type = inspect(dp)
                    if not obj_type.transient:
                        json_dp['project_name'] = dp.device_project_project.project_name
                        json_dp['device_name'] = dp.device_project_device.device_name
                        json_dp['device_available'] = len([part.id_participant for part in
                                                           dp.device_project_device.device_participants
                                                           if part.id_participant in accessible_part_ids]) == 0
                        if args['with_sites']:
                            json_dp['id_site'] = dp.device_project_project.id_site
                            json_dp['site_name'] = dp.device_project_project.project_site.site_name
                    else:
                        # Temporary object, a not-committed object, result of listing projects not associated in a
                        # device.
                        if dp.id_device:
                            device = TeraDevice.get_device_by_id(dp.id_device)
                            json_dp['device_name'] = device.device_name
                            json_dp['device_available'] = len([part.id_participant for part in
                                                               device.device_participants
                                                               if part.id_participant in accessible_part_ids]) == 0
                            #  not device.device_participants
                        else:
                            json_dp['device_name'] = None
                            json_dp['device_available'] = False
                        if dp.id_project:
                            project = TeraProject.get_project_by_id(dp.id_project)
                            json_dp['project_name'] = project.project_name
                            if args['with_sites']:
                                json_dp['id_site'] = project.id_site
                                json_dp['site_name'] = project.project_site.site_name
                        else:
                            json_dp['project_name'] = None
                device_project_list.append(json_dp)

            return device_project_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryDeviceProjects.__name__,
                                         'get', 500, 'Database error', str(e))
            return '', 500

    @api.doc(description='Create/update devices associated with a project.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify device association - the user isn\'t admin '
                             'of the project or current user can\'t access the device.',
                        400: 'Badly formed JSON or missing fields(id_project or id_device) in the JSON body',
                        500: 'Internal error occured when saving device association'},
             params={'token': 'Secret token'})
    @api.expect(post_schema)
    @user_multi_auth.login_required
    def post(self):
        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        if 'device' in request.json:
            # We have a device. Get list of items
            if 'id_device' not in request.json['device']:
                return gettext('Missing id_device'), 400
            if 'projects' not in request.json['device']:
                return gettext('Missing projects'), 400
            id_device = request.json['device']['id_device']

            # Get all current association for device
            current_projects = TeraDeviceProject.get_projects_for_device(device_id=id_device)
            current_projects_ids = [proj.id_project for proj in current_projects]
            received_projects_ids = [proj['id_project'] for proj in request.json['device']['projects']]
            # Difference - we must delete projects not anymore in the list
            todel_ids = set(current_projects_ids).difference(received_projects_ids)

            # Improve - not efficient at all...
            for id_project in todel_ids:
                project = TeraProject.get_project_by_id(id_project)
                if user_access.get_site_role(project.id_site) != 'admin':
                    return gettext('Access denied'), 403

            # Also filter projects already there
            received_projects_ids = set(received_projects_ids).difference(current_projects_ids)
            for proj_id in todel_ids:
                project = TeraProject.get_project_by_id(proj_id)
                if user_access.get_site_role(project.id_site) != 'admin':
                    return gettext('Access denied'), 403
                TeraDeviceProject.delete_with_ids(device_id=id_device, project_id=proj_id)
            # Build projects association to add
            json_dps = [{'id_device': id_device, 'id_project': project_id} for project_id in received_projects_ids]
        elif 'project' in request.json:
            # We have a project. Get list of items
            if 'id_project' not in request.json['project']:
                return gettext('Missing id_project'), 400
            if 'devices' not in request.json['project']:
                return gettext('Missing devices'), 400
            id_project = request.json['project']['id_project']

            # Only site admin can modify
            project = TeraProject.get_project_by_id(id_project)
            if user_access.get_site_role(project.id_site) != 'admin':
                return gettext('Access denied'), 403

            # Get all current association for project
            current_devices = TeraDeviceProject.get_devices_for_project(project_id=id_project)
            current_devices_ids = [device.id_device for device in current_devices]
            received_devices_ids = [device['id_device'] for device in request.json['project']['devices']]

            # Difference - we must delete devices not anymore in the list
            todel_ids = set(current_devices_ids).difference(received_devices_ids)
            # Also filter devices already there
            received_devices_ids = set(received_devices_ids).difference(current_devices_ids)

            for device_id in todel_ids:
                TeraDeviceProject.delete_with_ids(device_id=device_id, project_id=id_project)
            # Build projects association to add
            json_dps = [{'id_device': device_id, 'id_project': id_project} for device_id in received_devices_ids]
        elif 'device_project' in request.json:
            json_dps = request.json['device_project']
            if not isinstance(json_dps, list):
                json_dps = [json_dps]
        else:
            return '', 400

        # Validate if we have an id and access
        for json_dp in json_dps:
            if 'device_uuid' in json_dp:
                # Get id for that uuid
                from opentera.db.models.TeraDevice import TeraDevice
                json_dp['id_device'] = TeraDevice.get_device_by_uuid(json_dp['device_uuid']).id_device
                del json_dp['device_uuid']

            if 'id_device' not in json_dp or 'id_project' not in json_dp:
                return '', 400

            project = TeraProject.get_project_by_id(json_dp['id_project'])
            if user_access.get_site_role(project.id_site) != 'admin':
                return gettext('Access denied'), 403

            # Check if the device is part of the device site
            site_device = TeraDeviceSite.get_device_site_id_for_device_and_site(site_id=project.id_site,
                                                                                device_id=json_dp['id_device'])
            if not site_device:
                return gettext('At least one device is not part of the allowed device for that project site'), 403

        for json_dp in json_dps:
            if 'id_device_project' not in json_dp:
                # Check if already exists
                dp = TeraDeviceProject.get_device_project_id_for_device_and_project(
                    project_id=int(json_dp['id_project']), device_id=int(json_dp['id_device']))
                if dp:
                    json_dp['id_device_project'] = dp.id_device_project
                else:
                    json_dp['id_device_project'] = 0

            # Do the update!
            if int(json_dp['id_device_project']) > 0:
                # Already existing
                try:
                    TeraDeviceProject.update(int(json_dp['id_device_project']), json_dp)
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryDeviceProjects.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500
            else:
                try:
                    new_dp = TeraDeviceProject()
                    new_dp.from_json(json_dp)
                    TeraDeviceProject.insert(new_dp)
                    # Update ID for further use
                    json_dp['id_device_project'] = new_dp.id_device_project
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryDeviceProjects.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500

        return json_dps

    @api.doc(description='Delete a specific device-project association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete device association (no admin access to project or one of the '
                             'device\'s site)',
                        500: 'Device-project association not found or database error.'},
             params={'token': 'Secret token'})
    @api.expect(delete_parser)
    @user_multi_auth.login_required
    def delete(self):
        user_access = DBManager.userAccess(current_user)
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        device_project = TeraDeviceProject.get_device_project_by_id(id_todel)
        if not device_project:
            return gettext('Not found'), 400

        if device_project.id_project not in user_access.get_accessible_projects_ids(admin_only=True) or \
                device_project.device_project_device.id_device not in \
                user_access.get_accessible_devices_ids(admin_only=True):
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraDeviceProject.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryDeviceProjects.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
