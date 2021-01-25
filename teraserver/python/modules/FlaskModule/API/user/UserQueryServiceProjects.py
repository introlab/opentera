from flask import jsonify, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraServiceProject import TeraServiceProject
from opentera.db.models.TeraServiceRole import TeraServiceRole
from opentera.db.models.TeraService import TeraService
from opentera.db.models.TeraProject import TeraProject
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc, inspect
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_project', type=int, help='Project ID to query associated services')
get_parser.add_argument('id_service', type=int, help='Service ID to query associated projects from')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information '
                                                          '(ids only)')
get_parser.add_argument('with_projects', type=inputs.boolean, help='Used with id_service. Also return projects that '
                                                                   'don\'t have any association with that service')
get_parser.add_argument('with_services', type=inputs.boolean, help='Used with id_project. Also return services that '
                                                                   'don\'t have any association with that project')
get_parser.add_argument('with_roles', type=inputs.boolean, help='Used with id_project. Returns detailled information on'
                                                                'each role for this service.')

# post_parser = reqparse.RequestParser()
# post_parser.add_argument('service_project', type=str, location='json',
#                          help='Service - project association to create / update', required=True)
post_schema = api.schema_model('user_service_project', {'properties': TeraServiceProject.get_json_schema(),
                                                        'type': 'object',
                                                        'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific service - project association ID to delete. '
                                                'Be careful: this is not the service or project ID, but the ID'
                                                ' of the association itself!', required=True)


class UserQueryServiceProjects(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get services that are associated with a project. Only one "ID" parameter required and '
                         'supported at once.',
             responses={200: 'Success - returns list of services - projects association',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error when getting association'})
    def get(self):
        # current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()

        service_projects = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        if args['id_project']:
            if args['id_project'] in user_access.get_accessible_projects_ids():
                service_projects = user_access.query_services_projects_for_project(project_id=args['id_project'],
                                                                                   include_other_services=args['with_services'])
        else:
            if args['id_service']:
                if args['id_service'] in user_access.get_accessible_services_ids():
                    service_projects = user_access.query_projects_for_service(service_id=args['id_service'],
                                                                              include_other_projects=
                                                                              args['with_projects'])
        try:
            sp_list = []
            for sp in service_projects:
                json_sp = sp.to_json()
                if args['list'] is None:
                    obj_type = inspect(sp)
                    if not obj_type.transient:
                        json_sp['service_name'] = sp.service_project_service.service_name
                        json_sp['project_name'] = sp.service_project_project.project_name
                    else:
                        # Temporary object, a not-committed object, result of listing projects not associated in a
                        # service.
                        if sp.id_service:
                            json_sp['service_name'] = TeraService.get_service_by_id(sp.id_service).service_name
                        else:
                            json_sp['service_name'] = None
                        if sp.id_project:
                            json_sp['project_name'] = TeraProject.get_project_by_id(sp.id_project).project_name
                        else:
                            json_sp['project_name'] = None
                if args['with_roles']:
                    service_roles = TeraServiceRole.get_service_roles(sp.id_service)
                    json_roles = []
                    for role in service_roles:
                        json_roles.append(role.to_json(ignore_fields=['id_service']))
                    json_sp['service_roles'] = json_roles
                sp_list.append(json_sp)
            return sp_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryServiceProjects.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create/update service - project association. If a "service" json is received, the list of '
                         '"projects" is replaced. If a "project" json is received, the list of "services" is replaced.'
                         'If a "service_project" is received, each of the item in the list is added.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify association (only site admin can modify association)',
                        400: 'Badly formed JSON or missing fields(id_project or id_service) in the JSON body',
                        500: 'Internal error occured when saving association'})
    def post(self):
        # parser = post_parser
        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        if 'service' in request.json:
            # We have a service. Get list of items
            if 'id_service' not in request.json['service']:
                return gettext('Missing id_service'), 400
            if 'projects' not in request.json['service']:
                return gettext('Missing projects'), 400
            id_service = request.json['service']['id_service']

            # Only super admins can modify a service like that
            if not current_user.user_superadmin:
                return '', 403

            # Get all current association for service
            current_projects = TeraServiceProject.get_projects_for_service(id_service=id_service)
            current_projects_ids = [proj.id_project for proj in current_projects]
            received_projects_ids = [proj['id_project'] for proj in request.json['service']['projects']]
            # Difference - we must delete projects not anymore in the list
            todel_ids = set(current_projects_ids).difference(received_projects_ids)
            # Also filter projects already there
            received_projects_ids = set(received_projects_ids).difference(current_projects_ids)
            for proj_id in todel_ids:
                TeraServiceProject.delete_with_ids(service_id=id_service, project_id=proj_id)
            # Build projects association to add
            json_sps = [{'id_service': id_service, 'id_project': project_id} for project_id in received_projects_ids]
        elif 'project' in request.json:
            # We have a project. Get list of items
            if 'id_project' not in request.json['project']:
                return gettext('Missing id_project'), 400
            if 'services' not in request.json['project']:
                return gettext('Missing services'), 400
            id_project = request.json['project']['id_project']
            # Only site admin can modify
            from opentera.db.models.TeraProject import TeraProject
            project = TeraProject.get_project_by_id(id_project)
            if user_access.get_site_role(project.id_site) != 'admin':
                return gettext('Access denied'), 403

            # Get all current association for project
            current_services = TeraServiceProject.get_services_for_project(id_project=id_project)
            current_services_ids = [service.id_service for service in current_services]
            received_services_ids = [service['id_service'] for service in request.json['project']['services']]
            # Difference - we must delete services not anymore in the list
            todel_ids = set(current_services_ids).difference(received_services_ids)
            # Also filter services already there
            received_services_ids = set(received_services_ids).difference(current_services_ids)
            for service_id in todel_ids:
                TeraServiceProject.delete_with_ids(service_id=service_id, project_id=id_project)
            # Build projects association to add
            json_sps = [{'id_service': service_id, 'id_project': id_project} for service_id in received_services_ids]
        elif 'service_project' in request.json:
            json_sps = request.json['service_project']
            if not isinstance(json_sps, list):
                json_sps = [json_sps]
        else:
            return '', 400

        # Validate if we have an id and access
        for json_sp in json_sps:
            if 'service_uuid' in json_sp:
                # Get id for that uuid
                from opentera.db.models.TeraService import TeraService
                json_sp['id_service'] = TeraService.get_service_by_uuid(json_sp['service_uuid']).id_service
                del json_sp['service_uuid']

            if 'id_service' not in json_sp or 'id_project' not in json_sp:
                return '', 400

            # Check if current user can modify the posted information
            # if json_sp['id_service'] not in user_access.get_accessible_services_ids(admin_only=True):
            #     return gettext('Access denied'), 403

            from opentera.db.models.TeraProject import TeraProject
            project = TeraProject.get_project_by_id(json_sp['id_project'])
            if user_access.get_site_role(project.id_site) != 'admin':
                return gettext('Access denied'), 403

        for json_sp in json_sps:
            if 'id_service_project' not in json_sp:
                # Check if already exists
                sp = TeraServiceProject.get_service_project_for_service_project(project_id=int(json_sp['id_project']),
                                                                                service_id=int(json_sp['id_service']))
                if sp:
                    json_sp['id_service_project'] = sp.id_service_project
                else:
                    json_sp['id_service_project'] = 0

            # Do the update!
            if int(json_sp['id_service_project']) > 0:
                # Already existing
                try:
                    TeraServiceProject.update(int(json_sp['id_service_project']), json_sp)
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryServiceProjects.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500
            else:
                try:
                    new_sp = TeraServiceProject()
                    new_sp.from_json(json_sp)
                    TeraServiceProject.insert(new_sp)
                    # Update ID for further use
                    json_sp['id_service_project'] = new_sp.id_service_project
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQueryServiceProjects.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500

        update_sp = json_sps

        return jsonify(update_sp)

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific service - project association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete association (not site admin of the associated project)',
                        500: 'Association not found or database error.'})
    def delete(self):
        parser = delete_parser
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        sp = TeraServiceProject.get_service_project_by_id(id_todel)
        if not sp:
            return gettext('Not found'), 400

        if sp.service_project_project.id_site not in user_access.get_accessible_sites_ids(admin_only=True):
            return gettext('Operation not completed'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraServiceProject.delete(id_todel=id_todel)
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryServiceProjects.__name__,
                                         'delete', 500, 'Database error', str(e))
            return gettext('Database error'), 500

        return '', 200
