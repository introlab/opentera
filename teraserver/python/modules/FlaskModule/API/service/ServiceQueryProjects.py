from flask_restx import Resource, reqparse
from flask import request
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from modules.DatabaseModule.DBManager import DBManager

from opentera.db.models.TeraProject import TeraProject
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraSite import TeraSite
from sqlalchemy import exc

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_project', type=int, help='ID of the project to query')
get_parser.add_argument('id_site', type=int, help='ID of the site to query projects for')

post_parser = api.parser()
post_schema = api.schema_model('service_project', {'properties': TeraProject.get_json_schema(), 'type': 'object',
                                                   'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Project ID to delete', required=True)


class ServiceQueryProjects(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return projects information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Service doesn\'t have permission to access the requested data'},
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        """
        Get projects
        """
        args = get_parser.parse_args()
        service_access = DBManager.serviceAccess(current_service)

        projects = []
        # Can only query project with an id
        if not args['id_project'] and not args['id_site']:
            return gettext('Missing parameter'), 400

        if args['id_project']:
            if args['id_project'] not in service_access.get_accessible_projects_ids():
                return gettext('Forbidden'), 403
            projects = [TeraProject.get_project_by_id(args['id_project'])]

        if args['id_site']:
            if args['id_site'] not in service_access.get_accessibles_sites_ids():
                return gettext('Forbidden'), 403
            projects = TeraSite.get_site_by_id(args['id_site']).site_projects

        try:
            projects_list = []
            for project in projects:
                project_json = project.to_json(minimal=True)
                projects_list.append(project_json)

            return projects_list

        except exc.InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryProjects.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @api.doc(description='Create / update projects. id_project must be set to "0" to create a new '
                         'project. A project can be created/modified if the service is associated to the related site',
             responses={200: 'Success',
                        403: 'Logged service can\'t create/update the specified project',
                        400: 'Badly formed JSON or missing fields(id_site or id_project) in the JSON body',
                        500: 'Internal error occured when saving project'},
             params={'token': 'Access token'})
    @api.expect(post_schema)
    @LoginModule.service_token_or_certificate_required
    def post(self):
        """
        Create / update projects
        """
        service_access = DBManager.serviceAccess(current_service)
        # Using request.json instead of parser, since parser messes up the json!
        if 'project' not in request.json:
            return gettext('Missing project'), 400

        json_project = request.json['project']

        # Validate if we have an id
        if 'id_project' not in json_project:
            return gettext('Missing id_project'), 400

        if json_project['id_project'] == 0 and 'id_site' not in json_project:
            return gettext('Missing id_site arguments'), 400

        if 'id_site' in json_project and json_project['id_site'] not in service_access.get_accessibles_sites_ids():
            return gettext('Forbidden'), 403

        # Do the update!
        if json_project['id_project'] > 0:
            # Already existing - can only modifify if service is associated to that project
            project: TeraProject = TeraProject.get_project_by_id(json_project['id_project'])
            if not project or project.id_project not in service_access.get_accessible_projects_ids():
                return gettext('Forbidden'), 403

            try:
                TeraProject.update(json_project['id_project'], json_project)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQueryProjects.__name__,
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

                # Also associate this service to the project
                service_project = TeraServiceProject()
                service_project.id_service = current_service.id_service
                service_project.id_project = new_project.id_project
                TeraServiceProject.insert(service_project)

            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQueryProjects.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        update_project = TeraProject.get_project_by_id(json_project['id_project'])

        return update_project.to_json()

    @api.doc(description='Delete a specific project',
             responses={200: 'Success',
                        403: 'Logged service can\'t delete project (service not associated to)',
                        500: 'Database error.'},
             params={'token': 'Access token'})
    @api.expect(delete_parser)
    @LoginModule.service_token_or_certificate_required
    def delete(self):
        """
        Delete project
        """
        service_access = DBManager.serviceAccess(current_service)
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if current service can delete
        if id_todel not in service_access.get_accessible_projects_ids():
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraProject.delete(id_todel=id_todel)
        except exc.IntegrityError as e:
            # Causes that could make an integrity error when deleting:
            # - Associated participant groups with participants with sessions
            # - Associated participants with sessions
            self.module.logger.log_warning(self.module.module_name, ServiceQueryProjects.__name__, 'delete', 500,
                                           'Integrity error', str(e))
            return gettext('Can\'t delete project: please delete all participants with sessions before deleting.'), 500
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryProjects.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
