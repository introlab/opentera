from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraDeviceProject import TeraDeviceProject
from opentera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_device', type=int, help='ID of the device from which to request all associated projects'
                        )
get_parser.add_argument('id_project', type=int, help='ID of the project from which to get all associated devices')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information '
                                                          '(ids only)')

# post_parser = reqparse.RequestParser()
# post_parser.add_argument('device_project', type=str, location='json',
#                          help='Device-project association to create / update', required=True)
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

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get devices that are associated with a project. Only one "ID" parameter required and '
                         'supported at once.',
             responses={200: 'Success - returns list of devices - project association',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error occured when loading devices for projects'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()

        device_project = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        if args['id_device']:
            if args['id_device'] in user_access.get_accessible_devices_ids():
                device_project = TeraDeviceProject.query_projects_for_device(device_id=args['id_device'])
        elif args['id_project']:
            if args['id_project'] in user_access.get_accessible_projects_ids():
                device_project = TeraDeviceProject.query_devices_for_project(project_id=args['id_project'])
        try:
            device_project_list = []
            for dj in device_project:
                json_dj = dj.to_json()
                if args['list'] is None:
                    json_dj['project_name'] = dj.device_project_project.project_name
                    json_dj['device_name'] = dj.device_project_device.device_name
                    json_dj['device_available'] = not dj.device_project_device.device_participants
                device_project_list.append(json_dj)

            return jsonify(device_project_list)

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryDeviceProjects.__name__,
                                         'get', 500, 'Database error', str(e))
            return '', 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create/update devices associated with a project.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify device association - the user isn\'t admin '
                             'of the project or current user can\'t access the device.',
                        400: 'Badly formed JSON or missing fields(id_project or id_device) in the JSON body',
                        500: 'Internal error occured when saving device association'})
    def post(self):
        # parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        json_device_projects = request.json['device_project']
        if not isinstance(json_device_projects, list):
            json_device_projects = [json_device_projects]

        # Validate if we have an id
        for json_device_project in json_device_projects:
            if 'id_device' not in json_device_project or 'id_project' not in json_device_project:
                return gettext('Missing fields in body'), 400

            # Check if current user can modify the posted device
            if json_device_project['id_project'] not in user_access.get_accessible_projects_ids(admin_only=True) or\
                    json_device_project['id_device'] not in user_access.get_accessible_devices_ids(admin_only=True):
                return gettext('Forbidden'), 403

            # Check if already exists
            device_project = TeraDeviceProject.get_device_project_id_for_device_and_project(
                device_id=json_device_project['id_device'], project_id=json_device_project['id_project'])

            if device_project:
                json_device_project['id_device_project'] = device_project.id_device_project
            else:
                json_device_project['id_device_project'] = 0

            # Do the update!
            if json_device_project['id_device_project'] > 0:
                # Already existing
                try:
                    TeraDeviceProject.update(json_device_project['id_device_project'], json_device_project)
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryDeviceProjects.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500
            else:
                try:
                    new_device_project = TeraDeviceProject()
                    new_device_project.from_json(json_device_project)
                    TeraDeviceProject.insert(new_device_project)
                    # Update ID for further use
                    json_device_project['id_device_project'] = new_device_project.id_device_project
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryDeviceProjects.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500

        update_device_project = json_device_projects

        return jsonify(update_device_project)

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific device-project association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete device association (no admin access to project or one of the '
                             'device\'s site)',
                        500: 'Device-project association not found or database error.'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        device_project = TeraDeviceProject.get_device_project_by_id(id_todel)
        if not device_project:
            return gettext('Not found'), 400

        if device_project.id_project not in user_access.get_accessible_projects_ids(admin_only=True) or \
                device_project.device_project_device.id_device not in \
                user_access.get_accessible_devices_ids(admin_only=True):
            return gettext('Forbidden'), 403

        # Delete participants associated with that device, since the project was changed.
        associated_participants = TeraDeviceParticipant.query_participants_for_device(
            device_id=device_project.device_project_device.id_device)
        for part in associated_participants:
            if part.device_participant_participant.participant_project.id_project == device_project.id_project:
                device_part = TeraDeviceParticipant.query_device_participant_for_participant_device(
                    device_id=device_project.device_project_device.id_device, participant_id=part.id_participant)
                if device_part:
                    TeraDeviceParticipant.delete(device_part.id_device_participant)

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
