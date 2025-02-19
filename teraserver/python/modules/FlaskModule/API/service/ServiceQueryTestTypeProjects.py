from flask import request
from flask_restx import Resource, reqparse, inputs

from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc, inspect
from flask_babel import gettext

from modules.LoginModule.LoginModule import current_service, LoginModule
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraTestTypeProject import TeraTestTypeProject
from opentera.db.models.TeraTestTypeSite import TeraTestTypeSite
from opentera.db.models.TeraTestType import TeraTestType
from opentera.db.models.TeraProject import TeraProject
from modules.DatabaseModule.DBManager import DBManager


# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_project', type=int, help='Project ID to query associated test types from')
get_parser.add_argument('id_test_type', type=int, help='Test type ID to query associated projects from')

get_parser.add_argument('with_sites', type=inputs.boolean, help='Used with id_test_type. Also return site '
                                                                'information of the returned projects.')

post_parser = api.parser()
post_schema = api.schema_model('service_test_type_project', {'properties': TeraTestTypeProject.get_json_schema(),
                                                             'type': 'object',
                                                             'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific test type - project association ID to delete. '
                                                'Be careful: this is not the test-type or project ID, but the ID'
                                                ' of the association itself!', required=True)


class ServiceQueryTestTypeProjects(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get test types that are associated with a project. Only one "ID" parameter required and '
                         'supported at once.',
             responses={200: 'Success - returns list of test-types - projects association',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error when getting association'},
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        """
        Get test types associated with a project
        """
        service_access = DBManager.serviceAccess(current_service)
        args = get_parser.parse_args()

        test_type_projects = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        if args['id_project']:
            if args['id_project'] in service_access.get_accessible_projects_ids():
                test_type_projects = TeraTestTypeProject.get_tests_types_for_project(args['id_project'])
        elif args['id_test_type']:
            if args['id_test_type'] in service_access.get_accessible_tests_types_ids():
                test_type_projects = TeraTestTypeProject.get_projects_for_test_type(args['id_test_type'])
        try:
            ttp_list = []
            for ttp in test_type_projects:
                json_ttp = ttp.to_json()
                obj_type = inspect(ttp)
                if not obj_type.transient:
                    json_ttp['test_type_name'] = ttp.test_type_project_test_type.test_type_name
                    json_ttp['project_name'] = ttp.test_type_project_project.project_name
                    if args['with_sites']:
                        json_ttp['id_site'] = ttp.test_type_project_project.id_site
                        json_ttp['site_name'] = ttp.test_type_project_project.project_site.site_name
                else:
                    # Temporary object, a not-committed object, result of listing projects not associated to a
                    # test type.
                    if ttp.id_test_type:
                        tt: TeraTestType = TeraTestType.get_test_type_by_id(ttp.id_test_type)
                        json_ttp['test_type_name'] = tt.test_type_name
                    else:
                        json_ttp['test_type_name'] = None
                    if ttp.id_project:
                        proj = TeraProject.get_project_by_id(ttp.id_project)
                        json_ttp['project_name'] = proj.project_name
                        if args['with_sites']:
                            json_ttp['id_site'] = proj.id_site
                            json_ttp['site_name'] = proj.project_site.site_name
                    else:
                        json_ttp['project_name'] = None
                ttp_list.append(json_ttp)

            return ttp_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryTestTypeProjects.__name__,
                                         'get', 500, 'InvalidRequestError', e)
            return '', 500

    @api.doc(description='Create/update test-type - project association.',
             responses={200: 'Success',
                        403: 'Logged service can\'t modify association (not associated to project or test type)',
                        400: 'Badly formed JSON or missing fields in the JSON body',
                        500: 'Internal error occurred when saving association'},
             params={'token': 'Access token'})
    @api.expect(post_schema)
    @LoginModule.service_token_or_certificate_required
    def post(self):
        """
        Create / update test types -> project association
        """
        service_access = DBManager.serviceAccess(current_service)

        accessible_projects_ids = service_access.get_accessible_projects_ids(admin_only=True)
        if 'test_type' in request.json:
            # We have a test_type. Get list of items
            if 'id_test_type' not in request.json['test_type']:
                return gettext('Missing id_test_type'), 400
            if 'projects' not in request.json['test_type']:
                return gettext('Missing projects'), 400
            id_test_type = request.json['test_type']['id_test_type']

            if id_test_type not in service_access.get_accessible_tests_types_ids():
                return gettext("Forbidden"), 403

            # Get all current association for test type
            current_projects = TeraTestTypeProject.get_projects_for_test_type(test_type_id=id_test_type)
            current_projects_ids = [proj.id_project for proj in current_projects]

            for proj_id in current_projects_ids:
                if proj_id not in accessible_projects_ids:
                    return gettext('Access denied to at least one project'), 403

            received_proj_ids = [proj['id_project'] for proj in request.json['test_type']['projects']]
            # Difference - we must delete sites not anymore in the list
            todel_ids = set(current_projects_ids).difference(received_proj_ids)
            # Also filter projects already there
            received_proj_ids = set(received_proj_ids).difference(current_projects_ids)
            try:
                for proj_id in todel_ids:
                    if proj_id in accessible_projects_ids:  # Don't remove from the list if not admin for that project!
                        TeraTestTypeProject.delete_with_ids(test_type_id=id_test_type, project_id=proj_id,
                                                            autocommit=False)
                TeraTestTypeProject.commit()
            except exc.IntegrityError as e:
                self.module.logger.log_warning(self.module.module_name, ServiceQueryTestTypeProjects.__name__, 'delete',
                                               500, 'Integrity error', str(e))
                return gettext('Can\'t delete test type from project: please delete all tests of that type in the '
                               'project before deleting.'), 500
            # Build projects association to add
            json_ttp = [{'id_test_type': id_test_type, 'id_project': proj_id} for proj_id in received_proj_ids]
        elif 'project' in request.json:
            # We have a project. Get list of items
            if 'id_project' not in request.json['project']:
                return gettext('Missing project ID'), 400
            if 'testtypes' not in request.json['project']:
                return gettext('Missing test types'), 400
            id_project = request.json['project']['id_project']

            # Check if accessibles
            if id_project not in accessible_projects_ids:
                return gettext('Forbidden'), 403

            # Get all current association
            current_tests_types = TeraTestTypeProject.get_tests_types_for_project(project_id=id_project)
            current_tests_types_ids = [tt.id_test_type for tt in current_tests_types]
            received_tt_ids = [tt['id_test_type'] for tt in request.json['project']['testtypes']]
            # Difference - we must delete types not anymore in the list
            todel_ids = set(current_tests_types_ids).difference(received_tt_ids)
            # Also filter types already there
            received_tt_ids = set(received_tt_ids).difference(current_tests_types_ids)
            try:
                for tt_id in todel_ids:
                    TeraTestTypeProject.delete_with_ids(test_type_id=tt_id, project_id=id_project, autocommit=False)
                TeraTestTypeProject.commit()
            except exc.IntegrityError as e:
                self.module.logger.log_warning(self.module.module_name, ServiceQueryTestTypeProjects.__name__, 'delete',
                                               500, 'Integrity error', str(e))
                return gettext('Can\'t delete test type from project: please delete all tests of that type in the '
                               'project before deleting.'), 500
            # Build associations to add
            json_ttp = [{'id_test_type': tt_id, 'id_project': id_project} for tt_id in received_tt_ids]
        elif 'test_type_project' in request.json:
            json_ttp = request.json['test_type_project']
            if not isinstance(json_ttp, list):
                json_ttp = [json_ttp]
        else:
            return gettext('Unknown format'), 400

        # Validate if we have an id and access
        for json_tt in json_ttp:
            if 'id_test_type' not in json_tt or 'id_project' not in json_tt:
                return gettext('Badly formatted request'), 400

            if json_tt['id_project'] not in accessible_projects_ids:
                return gettext('Forbidden'), 403

            proj = TeraProject.get_project_by_id(json_tt['id_project'])
            site_access = TeraTestTypeSite.get_test_type_site_for_test_type_and_site(site_id=proj.id_site,
                                                                                     test_type_id=
                                                                                     json_tt['id_test_type']
                                                                                     )
            if not site_access:
                # At service level, if we have access to the project, we automatically associate the test type to its
                # site, since we know we are allowed to (prevent a call to another API)
                ttts = TeraTestTypeSite()
                ttts.id_test_type = json_tt['id_test_type']
                ttts.id_site = proj.id_site
                TeraTestTypeSite.insert(ttts)

        for json_tt in json_ttp:
            if 'id_test_type_project' not in json_tt:
                # Check if already exists
                tt = TeraTestTypeProject.\
                    get_test_type_project_for_test_type_project(project_id=int(json_tt['id_project']),
                                                                test_type_id=int(json_tt['id_test_type']))
                if tt:
                    json_tt['id_test_type_project'] = tt.id_test_type_project
                else:
                    json_tt['id_test_type_project'] = 0

            # Do the update!
            if int(json_tt['id_test_type_project']) == 0:
                try:
                    new_ttp = TeraTestTypeProject()
                    new_ttp.from_json(json_tt)
                    new_ttp = TeraTestTypeProject.insert(new_ttp)
                    # Update ID for further use
                    json_tt['id_test_type_project'] = new_ttp.id_test_type_project
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 ServiceQueryTestTypeProjects.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500

        return json_ttp

    @api.doc(description='Delete a specific test-type - project association.',
             responses={200: 'Success',
                        403: 'Logged service can\'t delete association (no access to test-type or project)',
                        400: 'Association not found (invalid id?)'},
             params={'token': 'Access token'})
    @api.expect(delete_parser)
    @LoginModule.service_token_or_certificate_required
    def delete(self):
        """
        Delete a specific test type -> project association
        """
        service_access = DBManager.serviceAccess(current_service)
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        ttp = TeraTestTypeProject.get_test_type_project_by_id(id_todel)
        if not ttp:
            return gettext('Not found'), 400

        if ttp.id_project not in service_access.get_accessible_projects_ids() or ttp.id_test_type \
                not in service_access.get_accessible_tests_types_ids():
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraTestTypeProject.delete(id_todel=id_todel)
        except exc.IntegrityError as e:
            # Causes that could make an integrity error when deleting:
            # - Associated project still have sessions with tests of that type
            self.module.logger.log_warning(self.module.module_name, ServiceQueryTestTypeProjects.__name__, 'delete',
                                           500, 'Integrity error', str(e))
            return gettext('Can\'t delete test type from project: please delete all tests of that type in the project '
                           'before deleting.'), 500
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryTestTypeProjects.__name__,
                                         'delete', 500, 'Database error', e)
            return gettext('Database error'), 500

        return '', 200
