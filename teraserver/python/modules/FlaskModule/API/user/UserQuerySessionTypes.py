from flask import request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraServiceSite import TeraServiceSite
from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraService import TeraService
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError, IntegrityError
from sqlalchemy import exc
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_session_type', type=int, help='ID of the session type to query')
get_parser.add_argument('id_project', type=int, help='ID of the project to get session type for')
get_parser.add_argument('id_site', type=int, help='ID of the site to get session types for')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')

post_parser = api.parser()
post_schema = api.schema_model('user_session_type', {'properties': TeraSessionType.get_json_schema(),
                                                     'type': 'object',
                                                     'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Session type ID to delete', required=True)


class UserQuerySessionTypes(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get session type information. If no id_session_type specified, returns all available '
                         'session types',
             responses={200: 'Success - returns list of session types',
                        500: 'Database error'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        """
        Get session type
        """
        user_access = DBManager.userAccess(current_user)
        args = get_parser.parse_args()

        if args['id_session_type']:
            session_types = [user_access.query_session_type_by_id(args['id_session_type'])]
        elif args['id_project']:
            session_types_projects = user_access.query_session_types_for_project(args['id_project'])
            session_types = [stp.session_type_project_session_type for stp in session_types_projects]
        elif args['id_site']:
            if args['id_site'] not in user_access.get_accessible_sites_ids():
                return gettext('Forbidden'), 403
            session_types_sites = user_access.query_session_types_sites_for_site(args['id_site'])
            session_types = [sts.session_type_site_session_type for sts in session_types_sites]
        else:
            session_types = user_access.get_accessible_session_types()

        try:
            sessions_types_list = []
            for st in session_types:
                if st is None:
                    continue
                if args['list'] is None:
                    st_json = st.to_json()
                    sessions_types_list.append(st_json)
                else:
                    st_json = st.to_json(minimal=True)
                    sessions_types_list.append(st_json)

            return sessions_types_list

        except InvalidRequestError:
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySessionTypes.__name__,
                                         'get', 500, 'InvalidRequestError')
            return gettext('Invalid request'), 500

    @api.doc(description='Create / update session type. id_session_type must be set to "0" to create a new '
                         'type. A session type can be created/modified if the user has access to a related session type'
                         'project.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified session type',
                        400: 'Badly formed JSON or missing field(id_session_type) in the JSON body',
                        500: 'Internal error when saving session type'})
    @api.expect(post_schema)
    @user_multi_auth.login_required
    def post(self):
        """
        Create / update session type
        """
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        if 'session_type' not in request.json:
            return gettext('Missing session_type'), 400

        json_session_type = request.json['session_type']

        # Validate if we have an id
        if 'id_session_type' not in json_session_type:
            return gettext('Missing id_session_type'), 400

        # Check if current user can modify the posted type
        if json_session_type['id_session_type'] > 0:
            if json_session_type['id_session_type'] not in \
                    user_access.get_accessible_session_types_ids(admin_only=True):
                return gettext('Forbidden'), 403
        else:
            # Session types can be created without a site if super admin, but require a site otherwise
            if 'session_type_sites' not in json_session_type and not current_user.user_superadmin:
                return gettext('Missing site(s) to associate that session type to'), 400
            # Will check for admin access in each site later on

        # Check if we have a session type of type "service" and, if there's changes in the id_service, it won't break
        # any project association
        session_type_category = None
        if 'session_type_category' in json_session_type:
            session_type_category = TeraSessionType.SessionCategoryEnum(int(json_session_type['session_type_category']))

        session_type = None
        if json_session_type['id_session_type'] > 0 and not session_type_category:
            session_type = TeraSessionType.get_session_type_by_id(json_session_type['id_session_type'])
            session_type_category = session_type.session_type_category

        if session_type_category == TeraSessionType.SessionCategoryEnum.SERVICE:
            # Check if we have a service id associated
            current_service_id = None
            if 'id_service' in json_session_type:
                # Get service id directly from the request
                current_service_id = json_session_type['id_service']
            else:
                # Get service id from the exiting session type
                if session_type:
                    current_service_id = session_type.id_service
            if not current_service_id:
                return gettext('Missing id_service for session type of type service'), 400
            if current_service_id not in user_access.get_accessible_services_ids():
                return gettext('Forbidden'), 403

        st_sites_ids = []
        admin_sites_ids = []
        update_st_sites = False
        if 'session_type_sites' in json_session_type:
            session_type_sites = json_session_type.pop('session_type_sites')
            if not isinstance(session_type_sites, list):
                session_type_sites = [session_type_sites]
            st_sites_ids = [site['id_site'] for site in session_type_sites]
            admin_sites_ids = user_access.get_accessible_sites_ids(admin_only=True)
            if set(st_sites_ids).difference(admin_sites_ids):
                # We have some sites where we are not admin
                return gettext('No site admin access for at least one site in the list'), 403
            # Check if we have a service session type and if that service is associated to that site
            if not current_user.user_superadmin:  # Super admin can always add service to a site, but not site admins
                if 'session_type_category' in json_session_type and 'id_service' in json_session_type:
                    if json_session_type['session_type_category'] == TeraSessionType.SessionCategoryEnum.SERVICE.value:
                        for site_id in st_sites_ids:
                            service_site = TeraServiceSite.\
                                get_service_site_for_service_site(site_id=site_id,
                                                                  service_id=json_session_type['id_service'])
                            if not service_site:
                                return gettext('At least one site isn\'t associated with the service of that session '
                                               'type'), 403
            update_st_sites = True

        st_projects_ids = []
        admin_projects_ids = []
        update_st_projects = False
        if 'session_type_projects' in json_session_type:
            # if json_session_type['id_session_type'] > 0:
            #     return gettext('Session type projects may be specified with that API only on a new session type. Use '
            #                    '"sessiontypeproject" instead'), 400
            session_type_projects = json_session_type.pop('session_type_projects')
            # Check if the current user is project admin in all of those projects
            st_projects_ids = [project['id_project'] for project in session_type_projects]
            admin_projects_ids = user_access.get_accessible_projects_ids(admin_only=True)
            if set(st_projects_ids).difference(admin_projects_ids):
                # We have some projects where we are not admin
                return gettext('No project admin access for at a least one project in the list'), 403

            # for project_id in st_projects_ids:
            #     if user_access.get_project_role(project_id) != 'admin':
            #         return gettext('No project admin access for at a least one project in the list'), 403
            update_st_projects = True

        st_services_ids = []
        admin_services_ids = []
        update_st_services = False
        if 'session_type_services' in json_session_type:
            session_type_services = json_session_type.pop('session_type_services')
            # Check if the current user has admin access to all services
            st_services_ids = [service['id_service'] for service in session_type_services]
            admin_services_ids = user_access.get_accessible_services_ids(admin_only=True)
            if set(st_services_ids).difference(admin_services_ids):
                # We have some projects where we are not admin
                return gettext('No service admin access for at a least one service in the list'), 403

            # for project_id in st_projects_ids:
            #     if user_access.get_project_role(project_id) != 'admin':
            #         return gettext('No project admin access for at a least one project in the list'), 403
            update_st_services = True

        # Do the update!
        new_st = None
        if json_session_type['id_session_type'] > 0:
            # Already existing
            try:
                TeraSessionType.update(json_session_type['id_session_type'], json_session_type)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQuerySessionTypes.__name__,
                                             'post', 500, 'Database error', e)
                return gettext('Database error'), 500
        else:
            # New
            try:
                new_st = TeraSessionType()
                new_st.from_json(json_session_type)
                TeraSessionType.insert(new_st)
                # Update ID for further use
                json_session_type['id_session_type'] = new_st.id_session_type
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQuerySessionTypes.__name__,
                                             'post', 500, 'Database error', e)
                return gettext('Database error'), 500

        update_session_type: TeraSessionType = (
            TeraSessionType.get_session_type_by_id(json_session_type['id_session_type']))

        # Update session type sites, if needed
        if update_st_sites:
            from opentera.db.models.TeraSite import TeraSite
            if new_st:
                # New session type - directly update the list
                update_session_type.session_type_sites = [TeraSite.get_site_by_id(site_id)
                                                          for site_id in st_sites_ids]
            else:
                # Updated session type - first, we add sites not already there
                update_st_current_sites = [site.id_site for site in update_session_type.session_type_sites]
                sites_to_add = set(st_sites_ids).difference(update_st_current_sites)
                update_session_type.session_type_sites.extend([TeraSite.get_site_by_id(site_id)
                                                               for site_id in st_sites_ids])

                # Then, we delete sites that the current user has access, but are not present in the posted list,
                # without touching sites already there
                update_st_current_sites.extend(list(sites_to_add))
                missing_sites = set(admin_sites_ids).difference(st_sites_ids)
                for site_id in missing_sites:
                    if site_id in update_st_current_sites:
                        update_session_type.session_type_sites.remove(TeraSite.get_site_by_id(site_id))

            # Commit the changes we made!
            update_session_type.commit()

            # Ensure that the newly added session types sites have a correct service site association, if required
            for sts in update_session_type.session_type_session_type_sites:
                TeraSessionTypeSite.check_integrity(sts)

        # Update session type projects, if needed
        if update_st_projects:
            if new_st:
                # New session type - directly update the list
                update_session_type.session_type_projects = [TeraProject.get_project_by_id(project_id)
                                                             for project_id in st_projects_ids]
            else:
                # Updated session type - first, we add projects not already there
                update_st_current_projects = [project.id_project for project in
                                              update_session_type.session_type_projects]
                projects_ids_to_add = set(st_projects_ids).difference(update_st_current_projects)
                projects_to_add = [TeraProject.get_project_by_id(project_id) for project_id in projects_ids_to_add]

                # Check if each project is part of that session site
                if not update_st_sites:
                    st_sites = [site.id_site for site in update_session_type.session_type_sites]
                    for project in projects_to_add:
                        if project.id_site not in st_sites:
                            return gettext('Session type not associated to project site'), 400

                update_session_type.session_type_projects.extend(projects_to_add)

                # Then, we delete projects that the current user has access, but are not present in the posted list,
                # without touching projects already there
                update_st_current_projects.extend(list(projects_to_add))
                missing_projects = set(admin_projects_ids).difference(st_projects_ids)
                for project_id in missing_projects:
                    if project_id in update_st_current_projects:
                        update_session_type.session_type_projects.remove(TeraProject.get_project_by_id(project_id))

        # Update session type additional services, if needed
        if update_st_services:
            if new_st:
                # New session type - directly update the list
                update_session_type.session_type_secondary_services = [TeraService.get_service_by_id(service_id)
                                                             for service_id in st_services_ids]
            else:
                # Updated session type - first, we add services not already there
                update_st_current_services = [service.id_service for service in
                                              update_session_type.session_type_secondary_services]
                service_ids_to_add = set(st_services_ids).difference(update_st_current_services)
                services_to_add = [TeraService.get_service_by_id(service_id) for service_id in
                                   service_ids_to_add]

                update_session_type.session_type_secondary_services.extend(services_to_add)

                # Then, we delete services that the current user has access, but are not present in the posted list,
                # without touching services already there
                update_st_current_services.extend(list(services_to_add))
                missing_services = set(admin_services_ids).difference(st_services_ids)
                for service_id in missing_services:
                    if service_id in update_st_current_services:
                        update_session_type.session_type_secondary_services.remove(
                            TeraService.get_service_by_id(service_id))

            # Commit the changes we made!
            update_session_type.commit()

            # Ensure that the newly added session types projects have a correct service project association, if required
            for stp in update_session_type.session_type_session_type_projects:
                try:
                    TeraSessionTypeProject.check_integrity(stp)
                except IntegrityError:
                    return gettext('Session type has a a service not associated to its site'), 400

        return [update_session_type.to_json()]

    @api.doc(description='Delete a specific session type',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete session type (no admin access to project related to that type '
                             'or sessions of that type exists in the system somewhere)',
                        500: 'Database error.'},
             params={'token': 'Secret token'})
    @api.expect(delete_parser)
    @user_multi_auth.login_required
    def delete(self):
        """
        Delete session type
        """
        user_access = DBManager.userAccess(current_user)
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        session_type = TeraSessionType.get_session_type_by_id(id_todel)

        # Check if we are admin of all projects of that session_type
        if len(session_type.session_type_projects) > 0:
            for proj in session_type.session_type_projects:
                if user_access.get_project_role(proj.id_project) != "admin":
                    return gettext('Cannot delete because you are not admin in all projects.'), \
                           403
        else:
            # No project right now for that session type - must at least project admin somewhere to delete
            if len(user_access.get_accessible_projects(admin_only=True)) == 0:
                return gettext('Unable to delete - not admin in at least one project'), 403

        # Check if there's some sessions that are using that session type. If so, we must not delete!
        # Now done at database level

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraSessionType.delete(id_todel=id_todel)
        except exc.IntegrityError as e:
            # Causes that could make an integrity error when deleting:
            # - Associated sessions of that session type
            self.module.logger.log_warning(self.module.module_name, UserQuerySessionTypes.__name__, 'delete', 500,
                                           'Integrity error', str(e))
            return gettext('Can\'t delete session type: please delete all sessions with that type before deleting.'
                           ), 500
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySessionTypes.__name__,
                                         'delete', 500, 'Database error', e)
            return gettext('Database error'), 500

        return '', 200
