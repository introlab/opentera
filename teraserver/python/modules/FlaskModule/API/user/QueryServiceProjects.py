from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraServiceProject import TeraServiceProject
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_project', type=int, help='Project ID to query associated services')
get_parser.add_argument('id_service', type=int, help='Service ID to query associated projects from')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information '
                                                          '(ids only)')

post_parser = reqparse.RequestParser()
post_parser.add_argument('service_project', type=str, location='json',
                         help='Service - project association to create / update', required=True)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific service - project association ID to delete. '
                                                'Be careful: this is not the service or project ID, but the ID'
                                                ' of the association itself!', required=True)


class QueryServiceProjects(Resource):

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
            service_projects = user_access.query_services_for_project(project_id=args['id_project'])
        else:
            if args['id_service']:
                service_projects = user_access.query_projects_for_service(service_id=args['id_service'])
        try:
            sp_list = []
            for sp in service_projects:
                json_sp = sp.to_json()
                if args['list'] is None:
                    json_sp['service_name'] = sp.service_project_service.service_name
                    json_sp['project_name'] = sp.service_project_project.project_name
                sp_list.append(json_sp)

            return sp_list

        except InvalidRequestError:
            return '', 500

    @user_multi_auth.login_required
    @api.expect(post_parser)
    @api.doc(description='Create/update service - project association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify association (only site admin can modify association)',
                        400: 'Badly formed JSON or missing fields(id_project or id_service) in the JSON body',
                        500: 'Internal error occured when saving association'})
    def post(self):
        # parser = post_parser
        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        json_sps = request.json['service_project']
        if not isinstance(json_sps, list):
            json_sps = [json_sps]

        # Validate if we have an id and access
        for json_sp in json_sps:
            if 'service_uuid' in json_sp:
                # Get id for that uuid
                from libtera.db.models.TeraService import TeraService
                json_sp['id_service'] = TeraService.get_service_by_uuid(json_sp['service_uuid']).id_service
                del json_sp['service_uuid']

            if 'id_service' not in json_sp or 'id_project' not in json_sp:
                return '', 400

            # Check if current user can modify the posted information
            if json_sp['id_service'] not in user_access.get_accessible_services_ids(admin_only=True):
                return gettext('Acces refuse'), 403

            from libtera.db.models.TeraProject import TeraProject
            project = TeraProject.get_project_by_id(json_sp['id_project'])
            if user_access.get_site_role(project.id_site) != 'admin':
                return 'Access denied', 403

        for json_sp in json_sps:
            # Check if already exists
            sp = TeraServiceProject.get_service_project_for_service_project(project_id=json_sp['id_project'],
                                                                            service_id=json_sp['id_service'])
            if sp:
                json_sp['id_service_project'] = sp.id_service_project
            else:
                json_sp['id_service_project'] = 0

            # Do the update!
            if json_sp['id_service_project'] > 0:
                # Already existing
                try:
                    TeraServiceProject.update(json_sp['id_service_project'], json_sp)
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500
            else:
                try:
                    new_sp = TeraServiceProject()
                    new_sp.from_json(json_sp)
                    TeraServiceProject.insert(new_sp)
                    # Update ID for further use
                    json_sp['id_service_project'] = new_sp.id_service_project
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500

        # TODO: Publish update to everyone who is subscribed to devices update...
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
            return gettext('Non-trouvé'), 500

        if sp.service_project_project.id_site not in user_access.get_accessible_sites_ids(admin_only=True):
            return gettext('Opération non-permise'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraServiceProject.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return gettext('Erreur base de données'), 500

        return '', 200
