from flask import request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from opentera.db.models.TeraUser import TeraUser
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
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
get_parser.add_argument('enabled', type=inputs.boolean, help='Flag that limits the returned data to the enabled '
                                                             'projects')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')

post_parser = api.parser()
post_schema = api.schema_model('user_project', {'properties': TeraProject.get_json_schema(),
                                                'type': 'object',
                                                'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Project ID to delete', required=True)


class UserQueryProjects(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get projects information. Only one of the ID parameter is supported and required at once',
             responses={200: 'Success - returns list of participants',
                        500: 'Database error'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        """
        Get projects
        """
        user_access = DBManager.userAccess(current_user)
        args = get_parser.parse_args()

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
            if args['id_service'] in user_access.get_accessible_services_ids():
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
                if args['enabled'] is not None:
                    if project.project_enabled != args['enabled']:
                        continue

                if args['list'] is None or args['list'] is False:
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

            return projects_list
        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryProjects.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @api.doc(description='Create / update projects. id_project must be set to "0" to create a new '
                         'project. A project can be created/modified if the user has admin rights to the '
                         'related site.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified project',
                        400: 'Badly formed JSON or missing fields(id_site or id_project) in the JSON body',
                        500: 'Internal error occured when saving project'})
    @api.expect(post_schema)
    @user_multi_auth.login_required
    def post(self):
        """
        Create / update project
        """
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        if 'project' not in request.json:
            return gettext('Missing project'), 400

        json_project = request.json['project']

        # Validate if we have an id
        if 'id_project' not in json_project:
            return gettext('Missing id_project'), 400
        if json_project['id_project'] == 0 and 'id_site' not in json_project:
            return gettext('Missing id_site arguments'), 400

        # Check if current user can modify the posted kit
        # User can modify or add a project if it is the project admin of that kit
        # if json_project['id_project'] not in user_access.get_accessible_projects_ids(admin_only=True) and \
        #         json_project['id_project'] > 0:
        #     return '', 403

        # Only site admins can create new projects
        if json_project['id_project'] == 0 and \
                json_project['id_site'] not in user_access.get_accessible_sites_ids(admin_only=True):
            return gettext('Forbidden'), 403

        # Only site admins can update projects
        if json_project['id_project'] > 0 and \
                json_project['id_project'] not in user_access.get_accessible_projects_ids(admin_only=True):
            return gettext('Forbidden'), 403

        update_session_types = False
        session_types_ids = []
        accessible_st_ids = []
        if 'sessiontypes' in json_project:
            session_types = json_project.pop('sessiontypes')
            if not isinstance(session_types, list):
                session_types = [session_types]
            session_types_ids = [session_type['id_session_type'] for session_type in session_types]
            accessible_st_ids = user_access.get_accessible_session_types_ids()
            if set(session_types_ids).difference(accessible_st_ids):
                # We have some session types not accessible
                return gettext('No access to a session type for at least one of it'), 403

            if 'id_site' not in json_project:
                # If we are here, the project has a site since it is an update (otherwise, site id is required)
                project = TeraProject.get_project_by_id(json_project['id_project'])
                if project:
                    json_project['id_site'] = project.id_site
            site_session_types = TeraSessionTypeSite.get_sessions_types_for_site(site_id=json_project['id_site'])
            site_session_types_ids = [st.id_session_type for st in site_session_types]

            if set(session_types_ids).difference(site_session_types_ids):
                # We have some session types not associated to the project site
                return gettext('At least one session type is not associated to the project site'), 403
            update_session_types = True

        # Do the update!
        new_project = None
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

        update_project = TeraProject.get_project_by_id(json_project['id_project'])

        if update_session_types:
            # Associate session types to that project
            if new_project:
                # New session type - directly update the list
                update_project.project_session_types = [TeraSessionType.get_session_type_by_id(st_id)
                                                        for st_id in session_types_ids]
            else:
                # Updated projects - first, we add session types not already there
                current_st_ids = [st.id_session_type for st in update_project.project_session_types]
                st_to_add = set(session_types_ids).difference(current_st_ids)
                update_project.project_session_types.extend([TeraSessionType.get_session_type_by_id(st_id)
                                                             for st_id in st_to_add])

                # Then, we delete session types that the current user has access, but are not present in the list,
                # without touching session types already there
                current_st_ids.extend(list(st_to_add))
                missing_st_list = set(accessible_st_ids).difference(session_types_ids)
                for st_id in missing_st_list:
                    if st_id in current_st_ids:
                        update_project.project_session_types.remove(TeraSessionType.get_session_type_by_id(st_id))

            # Commit the changes we made!
            update_project.commit()

            # Ensure services are associated to session type
            for ses_type in update_project.project_session_types:
                session_type_project = TeraSessionTypeProject.get_session_type_project_for_session_type_project(
                    update_project.id_project, ses_type.id_session_type)
                TeraSessionTypeProject.check_integrity(session_type_project)

        return [update_project.to_json()]

    @api.doc(description='Delete a specific project',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete project (only site admin can delete)',
                        500: 'Database error.'})
    @api.expect(delete_parser)
    @user_multi_auth.login_required
    def delete(self):
        """
        Delete project
        """
        user_access = DBManager.userAccess(current_user)
        args = delete_parser.parse_args()
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
            self.module.logger.log_warning(self.module.module_name, UserQueryProjects.__name__, 'delete', 500,
                                           'Integrity error', str(e))
            return gettext('Can\'t delete project: please delete all participants with sessions before deleting.'), 500
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryProjects.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
