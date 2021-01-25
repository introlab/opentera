from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraSessionType import TeraSessionType
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_project', type=int, help='Project ID to query associated session types from')
get_parser.add_argument('id_session_type', type=int, help='Session type ID to query associated projects from')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information '
                                                          '(ids only)')

# post_parser = reqparse.RequestParser()
# post_parser.add_argument('session_type_project', type=str, location='json',
#                          help='Device type - project association to create / update', required=True)
post_schema = api.schema_model('user_session_type_project', {'properties': TeraSessionTypeProject.get_json_schema(),
                                                             'type': 'object',
                                                             'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific device-type - project association ID to delete. '
                                                'Be careful: this is not the session-type or project ID, but the ID'
                                                ' of the association itself!', required=True)


class UserQuerySessionTypeProject(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get devices types that are associated with a project. Only one "ID" parameter required and '
                         'supported at once.',
             responses={200: 'Success - returns list of devices-types - projects association',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error when getting association'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()

        session_type_projects = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        if args['id_project']:
            session_type_projects = user_access.query_session_types_for_project(project_id=args['id_project'])
        else:
            if args['id_session_type']:
                if args['id_session_type'] in user_access.get_accessible_session_types_ids():
                    session_type_projects = TeraSessionTypeProject.query_projects_for_session_type(
                        args['id_session_type'])
        try:
            stp_list = []
            for stp in session_type_projects:
                json_stp = stp.to_json()
                if args['list'] is None:
                    json_stp['session_type_name'] = stp.session_type_project_session_type.session_type_name
                    json_stp['project_name'] = stp.session_type_project_project.project_name
                stp_list.append(json_stp)

            return jsonify(stp_list)

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySessionTypeProject.__name__,
                                         'get', 500, 'InvalidRequestError', e)
            return '', 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create/update session-type - project association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify association (session type must be accessible from project '
                             'access)',
                        400: 'Badly formed JSON or missing fields(id_project or id_session_type) in the JSON body',
                        500: 'Internal error occured when saving association'})
    def post(self):
        # parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        if 'session_type_project' not in request.json:
            return gettext('Field session_type_project missing'), 400

        json_stps = request.json['session_type_project']
        if not isinstance(json_stps, list):
            json_stps = [json_stps]

        # Validate if we have an id
        for json_stp in json_stps:
            if 'id_session_type' not in json_stp or 'id_project' not in json_stp:
                return '', 400

            # Check if current user can modify the posted information
            if json_stp['id_session_type'] not in user_access.get_accessible_session_types_ids(admin_only=True):
                return gettext('Access denied'), 403

            # Check if already exists
            stp = TeraSessionTypeProject.query_session_type_project_for_session_type_project(
                project_id=json_stp['id_project'], session_type_id=json_stp['id_session_type'])

            if stp:
                json_stp['id_session_type_project'] = stp.id_session_type_project
            else:
                json_stp['id_session_type_project'] = 0

            # Check if we try to change the associated project
            if 'id_project' in json_stp:
                # Check if we have a service type session type
                session_type = TeraSessionType.get_session_type_by_id(json_stp['id_session_type'])

                # Get services for that project
                if session_type.session_type_category == TeraSessionType.SessionCategoryEnum.SERVICE and \
                        session_type.id_session not in user_access.query_services_projects_for_project(json_stp['id_project']):
                    return gettext('Trying to associate a session type of type "service" with a service not associated '
                                   'to that project'), 400

            # Do the update!
            if json_stp['id_session_type_project'] > 0:
                # Already existing
                try:
                    TeraSessionTypeProject.update(json_stp['id_session_type_project'], json_stp)
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQuerySessionTypeProject.__name__,
                                                 'post', 500, 'Database error', e)
                    return gettext('Database error'), 500
            else:
                try:
                    new_stp = TeraSessionTypeProject()
                    new_stp.from_json(json_stp)
                    TeraSessionTypeProject.insert(new_stp)
                    # Update ID for further use
                    json_stp['id_session_type_project'] = new_stp.id_session_type_project
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return gettext('Database error'), 500

        update_stp = json_stps

        return jsonify(update_stp)

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific session-type - project association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete association (no access to session-type or project)',
                        500: 'Association not found or database error.'})
    def delete(self):
        parser = delete_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        stp = TeraSessionTypeProject.get_session_type_project_by_id(id_todel)
        if not stp:
            return gettext('Not found'), 500

        if stp.id_session_type not in user_access.get_accessible_session_types_ids(admin_only=True):
            return gettext('Access denied'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraSessionTypeProject.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySessionTypeProject.__name__,
                                         'delete', 500, 'Database error', e)
            return gettext('Database error'), 500

        return '', 200
