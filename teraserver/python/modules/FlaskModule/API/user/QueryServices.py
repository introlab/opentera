from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraService import TeraService
from libtera.db.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_service', type=int, help='ID of the service to query')
get_parser.add_argument('id', type=int, help='Alias for "id_service"')
get_parser.add_argument('uuid', type=str, help='Service UUID to query')
get_parser.add_argument('key', type=str, help='Service Key to query')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')


post_parser = reqparse.RequestParser()
post_parser.add_argument('service', type=str, location='json', help='Service to create / update', required=True)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Service ID to delete', required=True)


class QueryServices(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get services information. Only one of the ID parameter is supported and required at once.',
             responses={200: 'Success - returns list of services',
                        500: 'Database error'})
    def get(self):
        parser = get_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        args = parser.parse_args()

        services = []
        # If we have no arguments, return all accessible projects
        # queried_user = current_user

        if args['id']:
            args['id_service'] = args['id']

        if args['id_service']:
            if args['id_service'] in user_access.get_accessible_services_ids():
                services = [TeraService.get_service_by_id(args['id_service'])]
        elif args['uuid']:
            # If we have a service uuid, ensure that service is accessible
            service = TeraService.get_service_by_uuid(args['uuid'])
            if service and service.id_service in user_access.get_accessible_services_ids():
                services = [service]
        elif args['key']:
            service = TeraService.get_service_by_key(args['key'])
            if service and service.id_service in user_access.get_accessible_services_ids():
                services = [service]

        try:
            services_list = []

            for service in services:
                service_json = service.to_json()
                services_list.append(service_json)
            return jsonify(services_list)

        except InvalidRequestError:
            return '', 500

    @user_multi_auth.login_required
    @api.expect(post_parser)
    @api.doc(description='Create / update services. id_service must be set to "0" to create a new '
                         'service. A service can be created/modified only by super-admins.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified service',
                        400: 'Badly formed JSON or missing fields(id_service) in the JSON body',
                        500: 'Internal error occured when saving service'})
    def post(self):
        # parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        # Check if user is a super admin
        if not current_user.user_superadmin:
            return '', 403

        # Using request.json instead of parser, since parser messes up the json!
        json_service = request.json['service_project']

        # Validate if we have an id
        if 'id_service' not in json_service:
            return '', 400

        # Do the update!
        if json_service['id_service'] > 0:
            # Already existing
            try:
                TeraService.update(json_service['id_service'], json_service)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # New
            try:
                new_service = TeraService()
                new_service.from_json(json_service)
                TeraService.insert(new_service)
                # Update ID for further use
                json_service['id_service'] = json_service.id_service
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_service = TeraService.get_service_by_id(json_service['id_service'])

        return jsonify([update_service.to_json()])

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific service',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete service (only super admins can delete)',
                        500: 'Database error.'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        if not current_user.user_superadmin:
            return '', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraService.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200
