from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from modules.DatabaseModule.DBManager import DBManager
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_project', type=int, help='ID of the project to query')
get_parser.add_argument('id', type=int, help='Alias for "id_project"')
get_parser.add_argument('id_site', type=int, help='ID of the site from which to get all projects')
get_parser.add_argument('id_service', type=int, help='ID of the service from which to get all projects')
get_parser.add_argument('user_uuid', type=str, help='User UUID from which to get all projects that are accessible')
get_parser.add_argument('name', type=str, help='Project to query by name')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')

# post_parser = reqparse.RequestParser()
# post_parser.add_argument('project', type=str, location='json', help='Project to create / update', required=True)
post_schema = api.schema_model('user_project', {'properties': TeraProject.get_json_schema(),
                                                'type': 'object',
                                                'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Project ID to delete', required=True)


class UserQueryProjects(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get projects information. Only one of the ID parameter is supported and required at once',
             responses={200: 'Success - returns list of participants',
                        500: 'Database error'})
    def get(self):
        parser = get_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        args = parser.parse_args()

        projects = []
        # If we have no arguments, return all accessible projects
        # queried_user = current_user

        if args['id']:
            args['id_project'] = args['id']

        if args['id_project']:
            if args['id_project'] in user_access.get_accessible_projects_ids():
                projects = [TeraProject.get_project_by_id(args['id_project'])]

        elif args['user_uuid']:
            # If we have a user_uuid, query for the site of that user
            queried_user = TeraUser.get_user_by_uuid(args['user_uuid'])
            if queried_user is not None:
                user_access = DBManager.userAccess(queried_user)
                projects = user_access.get_accessible_projects()
        elif args['id_service']:
            projects = [project.service_project_project
                        for project in
                        user_access.query_projects_for_service(args['id_service'], site_id=args['id_site'])]
        elif args['id_site']:
            # If we have a site id, query for projects of that site
            projects = user_access.query_projects_for_site(site_id=args['id_site'])
        elif args['name']:
            projects = [TeraProject.get_project_by_projectname(projectname=args['name'])]
            for project in projects:
                if project is None and len(projects) == 1:
                    projects = []
                    break
                if project.id_project not in user_access.get_accessible_projects_ids():
                    # Current user doesn't have access to the requested project
                    projects = []
        else:
            projects = user_access.get_accessible_projects()

        try:
            projects_list = []

            for project in projects:
                if args['list'] is None or args['list'] == False:
                    project_json = project.to_json()
                    project_json['project_role'] = user_access.get_project_role(project.id_project)
                    projects_list.append(project_json)
                else:
                    project_json = project.to_json(minimal=True)
                    project_json['project_participant_group_count'] = \
                        len(TeraParticipantGroup.get_participant_group_for_project(project.id_project))
                    project_json['project_participant_count'] = len(user_access.query_all_participants_for_project(
                        project.id_project))
                    projects_list.append(project_json)

            return jsonify(projects_list)
        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryProjects.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create / update projects. id_project must be set to "0" to create a new '
                         'project. A project can be created/modified if the user has admin rights to the '
                         'related site.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified project',
                        400: 'Badly formed JSON or missing fields(id_site or id_project) in the JSON body',
                        500: 'Internal error occured when saving project'})
    def post(self):
        # parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_project = request.json['project']

        # Validate if we have an id
        if 'id_project' not in json_project or 'id_site' not in json_project:
            return gettext('Missing id_project or id_site arguments'), 400

        # Check if current user can modify the posted kit
        # User can modify or add a project if it is the project admin of that kit
        # if json_project['id_project'] not in user_access.get_accessible_projects_ids(admin_only=True) and \
        #         json_project['id_project'] > 0:
        #     return '', 403

        # Only site admins can create new projects
        if json_project['id_project'] == 0 and \
                json_project['id_site'] not in user_access.get_accessible_sites_ids(admin_only=True):
            return gettext('Forbidden'), 403

        # Do the update!
        if json_project['id_project'] > 0:
            # Already existing
            try:
                TeraProject.update(json_project['id_project'], json_project)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryProjects.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # New
            try:
                new_project = TeraProject()
                new_project.from_json(json_project)
                TeraProject.insert(new_project)
                # Update ID for further use
                json_project['id_project'] = new_project.id_project
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryProjects.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_project = TeraProject.get_project_by_id(json_project['id_project'])

        return jsonify([update_project.to_json()])

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific project',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete project (only site admin can delete)',
                        500: 'Database error.'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # Only site admins can delete a project
        project = TeraProject.get_project_by_id(id_todel)

        if user_access.get_site_role(project.project_site.id_site) != 'admin':
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraProject.delete(id_todel=id_todel)
        except exc.IntegrityError as e:
            # Causes that could make an integrity error when deleting:
            # - Associated participant groups with participants with sessions
            # - Associated participants with sessions
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryProjects.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Can\'t delete project: please delete all participants with sessions before deleting.'), 500
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryProjects.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
