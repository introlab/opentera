from flask import jsonify, session, request
from flask_restplus import Resource, reqparse
from sqlalchemy import exc
from modules.LoginModule.LoginModule import multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from libtera.db.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user', type=int, help='ID of the user from which to request all projects roles')
get_parser.add_argument('id_project', type=int, help='ID of the project from which to request all users roles')

post_parser = reqparse.RequestParser()
post_parser.add_argument('project_access', type=str, location='json',
                         help='Project access to create / update', required=True)


class QueryProjectAccess(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get user roles for projects. Only one  parameter required and supported at once.',
             responses={200: 'Success - returns list of users roles in projects',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error occured when loading project roles'})
    def get(self):
        parser = get_parser

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        args = parser.parse_args()

        access = None
        # If we have no arguments, return bad request
        if not any(args.values()):
            return "ProjectAccess: missing argument.", 400

        # Query access for user id
        if args['id_user']:
            user_id = args['id_user']

            if user_id in user_access.get_accessible_users_ids():
                access = user_access.query_project_access_for_user(user_id=user_id)

        # Query access for project id
        if args['id_project']:
            project_id = args['id_project']
            access = user_access.query_access_for_project(project_id=project_id)

        if access is not None:
            access_list = []
            for proj_access in access:
                if proj_access is not None:
                    access_list.append(proj_access.to_json())
            return jsonify(access_list)

        return 'Unknown error', 500

    @multi_auth.login_required
    @api.expect(post_parser)
    @api.doc(description='Create/update project access for an user.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify this project or user access (project admin access required)',
                        400: 'Badly formed JSON or missing fields(id_user or id_project) in the JSON body',
                        500: 'Database error'})
    def post(self):
        parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_projects = request.json['project_access']

        if not isinstance(json_projects, list):
            json_projects = [json_projects]

        # Validate if we have everything needed
        json_rval = []
        for json_project in json_projects:
            if 'id_user' not in json_project:
                return 'Missing id_user', 400
            if 'id_project' not in json_project:
                return 'Missing id_project', 400

            # Check if current user can change the access for that site
            if user_access.get_project_role(project_id=json_project['id_project']) != 'admin':
                return 'Forbidden', 403

            # Do the update!
            try:
                access = TeraProjectAccess.update_project_access(json_project['id_user'], json_project['id_project'],
                                                                 json_project['project_access_role'])
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

            # TODO: Publish update to everyone who is subscribed to site access update...
            if access:
                json_rval.append(access.to_json())

        return jsonify(json_rval)

    # @multi_auth.login_required
    # def delete(self):
    #
    #     return '', 501

