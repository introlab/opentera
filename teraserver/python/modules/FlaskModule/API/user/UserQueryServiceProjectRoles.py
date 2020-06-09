from flask import jsonify, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraServiceProjectRole import TeraServiceProjectRole
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_project', type=int, help='Project ID to query associated services roles')
get_parser.add_argument('id_service', type=int, help='Service ID to query associated roles from')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information '
                                                          '(ids only)')
get_parser.add_argument('with_usergroups', type=inputs.boolean, help='Also return user groups information even for '
                                                                     'those without any role in that service-project')

post_parser = reqparse.RequestParser()
post_parser.add_argument('service_project_role', type=str, location='json',
                         help='Role for specific service and project to create / update', required=True)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific service project role association ID to delete. '
                                                'Be careful: this is not the service or project ID, but the ID'
                                                ' of the association itself!', required=True)


class UserQueryServiceProjectRoles(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get roles for a services in a project. Only one "ID" parameter required and '
                         'supported at once.',
             responses={200: 'Success - returns list of roles',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error when getting association'})
    def get(self):
        # current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()

        service_project_roles = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        if args['id_project']:
            if args['id_project'] in user_access.get_accessible_projects_ids():
                service_project_roles = user_access.query_services_roles_for_project(project_id=args['id_project'])
        else:
            if args['id_service']:
                if args['id_service'] in user_access.get_accessible_services_ids():
                    service_project_roles = user_access.query_services_roles_for_service(service_id=args['id_service'])

        if args['with_usergroups']:
            # Check if there's user groups without any access and creates them, if needed, for each service
            service_ids = [spr.id_service for spr in service_project_roles]
            project_ids = [spr.id_project for spr in service_project_roles]
            user_group_ids = user_access.get_accessible_users_groups_ids()
            for service_id in service_ids:
                for project_id in project_ids:
                    service_user_groups = [spr.id_user_group for spr in service_project_roles
                                           if spr.id_service == service_id and spr.id_project == project_id]
                    missing_user_groups_ids = set(user_group_ids).difference(service_user_groups)
                    for user_group_id in missing_user_groups_ids:
                        new_spr = TeraServiceProjectRole()
                        new_spr.id_service = service_id
                        new_spr.id_project = project_id
                        new_spr.id_user_group = user_group_id
                        new_spr.id_service_role = None
                        service_project_roles.append(new_spr)
        # Sort by service
        service_project_roles.sort(key=lambda x: x.id_service)
        try:
            spr_list = []
            for spr in service_project_roles:
                json_spr = spr.to_json(minimal=args['list'])
                spr_list.append(json_spr)
            return spr_list

        except InvalidRequestError:
            return '', 500

    @user_multi_auth.login_required
    @api.expect(post_parser)
    @api.doc(description='Create/update service - project - role association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify association (only site admin can modify association)',
                        400: 'Badly formed JSON or missing fields(id_project or id_service) in the JSON body',
                        500: 'Internal error occured when saving association'})
    def post(self):
        # parser = post_parser
        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        if 'service_project_role' in request.json:
            json_spr = request.json['service_project_role']
            if not isinstance(json_spr, list):
                json_spr = [json_spr]
        else:
            return '', 400

        # Validate if we have an id and access
        for json_sp in json_spr:
            if 'id_service' not in json_sp or 'id_project' not in json_sp or 'id_service_project_role' not in json_sp \
                    or 'id_service_role' not in json_sp:
                return '', 400

            # Check if current user can modify the posted information
            if json_sp['id_service'] not in user_access.get_accessible_services_ids(admin_only=True):
                return gettext('Acces refuse'), 403

            from libtera.db.models.TeraProject import TeraProject
            project = TeraProject.get_project_by_id(json_sp['id_project'])
            if user_access.get_site_role(project.id_site) != 'admin':
                return 'Access denied', 403

        for json_sp in json_spr:
            # Do the update!
            if json_sp['id_service_project_role'] > 0:
                # Already existing
                try:
                    TeraServiceProjectRole.update(json_sp['id_service_project_role'], json_sp)
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500
            else:
                try:
                    new_sp = TeraServiceProjectRole()
                    new_sp.from_json(json_sp)
                    TeraServiceProjectRole.insert(new_sp)
                    # Update ID for further use
                    json_sp['id_service_project_role'] = new_sp.id_service_project_role
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500

        update_sp = json_spr

        return jsonify(update_sp)

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific service - project - role.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete association (not site admin of the associated project)',
                        500: 'Association not found or database error.'})
    def delete(self):
        parser = delete_parser
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        sp = TeraServiceProjectRole.get_service_project_role_by_id(id_todel)
        if not sp:
            return gettext('Not found'), 500

        if sp.service_project_role_project.id_site not in user_access.get_accessible_sites_ids(admin_only=True):
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraServiceProjectRole.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return gettext('Database error'), 500

        return '', 200
