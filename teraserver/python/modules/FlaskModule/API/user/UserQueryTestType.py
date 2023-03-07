from flask import session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraServiceSite import TeraServiceSite
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError, IntegrityError
from sqlalchemy import exc
from flask_babel import gettext

from opentera.redis.RedisVars import RedisVars

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_test_type', type=int, help='ID of the test type to query')
get_parser.add_argument('test_type_key', type=str, help='Key of the test type to query')
get_parser.add_argument('id_project', type=int, help='ID of the project to get test types for')
get_parser.add_argument('id_site', type=int, help='ID of the site to get test types for')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')
get_parser.add_argument('with_urls', type=inputs.boolean, help='Also include test types urls')
get_parser.add_argument('with_only_token', type=inputs.boolean, help='Only includes the access token. '
                                                                     'Will ignore with_urls if specified.')

post_parser = api.parser()
post_schema = api.schema_model('user_test_type', {'properties': TeraTestType.get_json_schema(), 'type': 'object',
                                                  'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Test type ID to delete', required=True)


class UserQueryTestTypes(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get test type information. If no id_test_type specified, returns all available test types',
             responses={200: 'Success - returns list of test types',
                        500: 'Database error'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        user_access = DBManager.userAccess(current_user)
        args = get_parser.parse_args()

        if args['id_test_type']:
            test_types = [user_access.query_test_type(args['id_test_type'])]
        elif args['test_type_key']:
            test_type = TeraTestType.get_test_type_by_key(args['test_type_key'])
            test_types = [user_access.query_test_type(test_type.id_test_type)]  # Call to filter access if needed
        elif args['id_project']:
            test_types_projects = user_access.query_test_types_for_project(args['id_project'])
            test_types = [ttp.test_type_project_test_type for ttp in test_types_projects]
        elif args['id_site']:
            if args['id_site'] not in user_access.get_accessible_sites_ids():
                return gettext('Forbidden'), 403
            test_types_sites = user_access.query_test_types_sites_for_site(args['id_site'])
            test_types = [tts.test_type_site_test_type for tts in test_types_sites]
        else:
            test_types = user_access.get_accessible_test_types()

        try:
            test_types_list = []
            servername = self.module.config.server_config['hostname']
            port = self.module.config.server_config['port']
            if 'X_EXTERNALSERVER' in request.headers:
                servername = request.headers['X_EXTERNALSERVER']

            if 'X_EXTERNALPORT' in request.headers:
                port = request.headers['X_EXTERNALPORT']

            for tt in test_types:
                if args['with_only_token']:
                    tt_json = {'test_type_uuid': tt.test_type_uuid}
                else:
                    tt_json = tt.to_json(minimal=args['list'])

                if args['with_urls'] or args['with_only_token']:
                    # Access token
                    token_key = self.module.redisGet(RedisVars.RedisVar_ServiceTokenAPIKey)
                    projects_ids = [proj.id_project for proj in
                                    TeraTestTypeProject.get_projects_for_test_type(tt.id_test_type)]
                    admin_projects_ids = user_access.get_accessible_projects_ids(admin_only=True)

                    # Is project admin in at least one of the related project? If so, can edit the test type
                    is_project_admin = len(set(projects_ids).difference(admin_projects_ids)) != len(projects_ids)

                    access_token = TeraTestType.get_access_token(test_type_uuids=tt.test_type_uuid,
                                                                 token_key=token_key,
                                                                 requester_uuid=current_user.user_uuid,
                                                                 can_edit=is_project_admin,
                                                                 expiration=1800)
                    tt_json['access_token'] = access_token

                if args['with_urls']:
                    tt_json.update(tt.get_service_urls(server_url=servername, server_port=port))

                test_types_list.append(tt_json)

            return test_types_list

        except InvalidRequestError:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryTestTypes.__name__,
                                         'get', 500, 'InvalidRequestError')
            return gettext('Invalid request'), 500

    @api.doc(description='Create / update test type. id_test_type must be set to "0" to create a new '
                         'type. A test type can be created/modified if the user has access to a related test type'
                         'project.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified test type',
                        400: 'Badly formed JSON or missing field in the JSON body',
                        500: 'Internal error when saving test type'},
             params={'token': 'Secret token'})
    @api.expect(post_schema)
    @user_multi_auth.login_required
    def post(self):
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        if 'test_type' not in request.json:
            return gettext('Missing test_type'), 400

        json_test_type = request.json['test_type']

        # Validate if we have an id
        if 'id_test_type' not in json_test_type:
            return gettext('Missing id_test_type'), 400

        # Check if current user can modify the posted type
        if json_test_type['id_test_type'] > 0:
            projects_ids = [proj.id_project for proj in
                            TeraTestTypeProject.get_projects_for_test_type(json_test_type['id_test_type'])]
            admin_projects_ids = user_access.get_accessible_projects_ids(admin_only=True)

            if len(set(projects_ids).difference(admin_projects_ids)) == len(projects_ids):
                return gettext('Not project admin in at least one project'), 403
        else:
            # Test types can be created without a project if super admin, but require a project otherwise
            if 'test_type_projects' not in json_test_type and not current_user.user_superadmin:
                return gettext('Missing project(s) to associate that test type to'), 400
            # Will check for admin access in each site later on

        # Check if we have a test type of type "service" and, if there's changes in the id_service, it won't break
        # any project association

        # Check if we have a service id associated
        current_service_id = None
        if 'id_service' in json_test_type:
            # Get service id directly from the request
            current_service_id = json_test_type['id_service']
        else:
            # Get service id from the exiting session type
            test_type: TeraTestType = TeraTestType.get_test_type_by_id(json_test_type['id_test_type'])
            if test_type:
                current_service_id = test_type.id_service
        if current_service_id not in user_access.get_accessible_services_ids():
            return gettext('Forbidden'), 403

        tt_sites_ids = []
        admin_sites_ids = []
        update_tt_sites = False
        if 'test_type_sites' in json_test_type:
            test_type_sites = json_test_type.pop('test_type_sites')
            if not isinstance(test_type_sites, list):
                test_type_sites = [test_type_sites]
            tt_sites_ids = [site['id_site'] for site in test_type_sites]
            admin_sites_ids = user_access.get_accessible_sites_ids(admin_only=True)
            if set(tt_sites_ids).difference(admin_sites_ids):
                # We have some sites where we are not admin
                return gettext('No site admin access for at least one site in the list'), 403
            # Check if we have a service test type and if that service is associated to that site
            if not current_user.user_superadmin:  # Super admin can always add service to a site, but not site admins
                if 'id_service' in json_test_type:
                    for site_id in tt_sites_ids:
                        service_site = TeraServiceSite.\
                            get_service_site_for_service_site(site_id=site_id,
                                                              service_id=json_test_type['id_service'])
                        if not service_site:
                            return gettext('At least one site isn\'t associated with the service of that test type'),\
                                   403
            update_tt_sites = True

        tt_projects_ids = []
        admin_projects_ids = []
        update_tt_projects = False
        if 'test_type_projects' in json_test_type:
            test_type_projects = json_test_type.pop('test_type_projects')
            # Check if the current user is project admin in all of those projects
            tt_projects_ids = [project['id_project'] for project in test_type_projects]
            admin_projects_ids = user_access.get_accessible_projects_ids(admin_only=True)
            if set(tt_projects_ids).difference(admin_projects_ids):
                # We have some projects where we are not admin
                return gettext('No project admin access for at a least one project in the list'), 403

            update_tt_projects = True

        # Do the update!
        new_tt = None
        if json_test_type['id_test_type'] > 0:
            # Already existing
            try:
                TeraTestType.update(json_test_type['id_test_type'], json_test_type)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryTestTypes.__name__,
                                             'post', 500, 'Database error', e)
                return gettext('Database error'), 500
        else:
            # New
            try:
                new_tt = TeraTestType()
                new_tt.from_json(json_test_type)
                TeraTestType.insert(new_tt)
                # Update ID for further use
                json_test_type['id_test_type'] = new_tt.id_test_type
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             UserQueryTestTypes.__name__,
                                             'post', 500, 'Database error', e)
                return gettext('Database error'), 500

        update_test_type = TeraTestType.get_test_type_by_id(json_test_type['id_test_type'])

        # Update test type sites, if needed
        if update_tt_sites:
            from opentera.db.models.TeraSite import TeraSite
            if new_tt:
                # New test type - directly update the list
                update_test_type.test_type_sites = [TeraSite.get_site_by_id(site_id) for site_id in tt_sites_ids]
            else:
                # Updated test type - first, we add sites not already there
                update_tt_current_sites = [site.id_site for site in update_test_type.test_type_sites]
                sites_to_add = set(tt_sites_ids).difference(update_tt_current_sites)
                update_test_type.test_type_sites.extend([TeraSite.get_site_by_id(site_id) for site_id in tt_sites_ids])

                # Then, we delete sites that the current user has access, but are not present in the posted list,
                # without touching sites already there
                update_tt_current_sites.extend(list(sites_to_add))
                missing_sites = set(admin_sites_ids).difference(tt_sites_ids)
                for site_id in missing_sites:
                    if site_id in update_tt_current_sites:
                        update_test_type.test_type_sites.remove(TeraSite.get_site_by_id(site_id))

            # Commit the changes we made!
            update_test_type.commit()

            # Ensure that the newly added session types sites have a correct service site association, if required
            for tts in update_test_type.test_type_test_type_sites:
                TeraTestTypeSite.check_integrity(tts)

        # Update test type projects, if needed
        if update_tt_projects:
            from opentera.db.models.TeraProject import TeraProject
            if new_tt:
                # New test type - directly update the list
                update_test_type.test_type_projects = [TeraProject.get_project_by_id(project_id)
                                                       for project_id in tt_projects_ids]
            else:
                # Updated test type - first, we add projects not already there
                update_tt_current_projects = [project.id_project for project in update_test_type.test_type_projects]
                projects_ids_to_add = set(tt_projects_ids).difference(update_tt_current_projects)
                projects_to_add = [TeraProject.get_project_by_id(project_id) for project_id in projects_ids_to_add]

                # Check if each project is part of that test site
                if not update_tt_sites:
                    tt_sites = [site.id_site for site in update_test_type.test_type_sites]
                    for project in projects_to_add:
                        if project.id_site not in tt_sites:
                            return gettext('Session type not associated to project site'), 400

                update_test_type.test_type_projects.extend(projects_to_add)

                # Then, we delete projects that the current user has access, but are not present in the posted list,
                # without touching projects already there
                update_tt_current_projects.extend(list(projects_to_add))
                missing_projects = set(admin_projects_ids).difference(tt_projects_ids)
                for project_id in missing_projects:
                    if project_id in update_tt_current_projects:
                        update_test_type.test_type_projects.remove(TeraProject.get_project_by_id(project_id))

            # Commit the changes we made!
            update_test_type.commit()

            # Ensure that the newly added test types projects have a correct service project association, if required
            for ttp in update_test_type.test_type_test_type_projects:
                try:
                    TeraTestTypeProject.check_integrity(ttp)
                except IntegrityError:
                    return gettext('Test type has a a service not associated to its site'), 400

        return [update_test_type.to_json()]

    @api.doc(description='Delete a specific test type',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete test type (no admin access to project related to that type '
                             'or tests of that type exists in the system somewhere)',
                        500: 'Database error.'},
             params={'token': 'Secret token'})
    @api.expect(delete_parser)
    @user_multi_auth.login_required
    def delete(self):
        user_access = DBManager.userAccess(current_user)
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        test_type = TeraTestType.get_test_type_by_id(id_todel)

        # Check if we are admin of all projects of that test type
        if len(test_type.test_type_projects) > 0:
            for proj in test_type.test_type_projects:
                if user_access.get_project_role(proj.id_project) != "admin":
                    return gettext('Cannot delete because you are not admin in all projects.'), 403
        else:
            # No project right now for that test type - must at least project admin somewhere to delete
            if len(user_access.get_accessible_projects(admin_only=True)) == 0:
                return gettext('Unable to delete - not admin in at least one project'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraTestType.delete(id_todel=id_todel)
        except exc.IntegrityError as e:
            # Causes that could make an integrity error when deleting:
            # - Associated tests of that test type
            self.module.logger.log_warning(self.module.module_name, UserQueryTestTypes.__name__, 'delete', 500,
                                           'Integrity error', str(e))
            return gettext('Can\'t delete test type: please delete all tests of that type before deleting.'), 500
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryTestTypes.__name__,
                                         'delete', 500, 'Database error', e)
            return gettext('Database error'), 500

        return '', 200
