from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from sqlalchemy import exc
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from flask_babel import gettext
from modules.DatabaseModule.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user', type=int, help='ID of the user to query')
get_parser.add_argument('user_uuid', type=str, help='User UUID to query')
get_parser.add_argument('username', type=str, help='Username of the user to query')
get_parser.add_argument('self', type=inputs.boolean, help='Query information about the currently logged user')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information '
                                                          '(ID, name, enabled)')
get_parser.add_argument('with_usergroups', type=inputs.boolean, help='Include usergroups information for each user. '
                                                                     'Can\'t be combined with "list" argument.')

post_parser = reqparse.RequestParser()
post_parser.add_argument('user', type=str, location='json', help='User to create / update', required=True)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='User ID to delete', required=True)


class QueryUsers(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get user information. If no id specified, returns all accessible users',
             responses={200: 'Success',
                        500: 'Database error'})
    def get(self):
        parser = get_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        args = parser.parse_args()

        user_access = DBManager.userAccess(current_user)

        users = []

        # If we have a user_uuid, query for that user if accessible
        if args['user_uuid']:
            if args['user_uuid'] in user_access.get_accessible_users_uuids():
                users.append(TeraUser.get_user_by_uuid(args['user_uuid']))
        elif args['id_user']:
            if args['id_user'] in user_access.get_accessible_users_ids():
                users.append(current_user.get_user_by_id(args['id_user']))
        elif args['self'] is not None:
            users.append(current_user)
        elif args['username'] is not None:
            users.append(current_user.get_user_by_username(args['username']))
        else:
            # If we have no arguments, return all accessible users
            users = user_access.get_accessible_users()

        if users:
            users_list = []
            for user in users:
                if user is not None:
                    if args['list'] is None:
                        # If user is "self", append projects and sites roles
                        user_json = user.to_json()
                        if user.id_user == current_user.id_user:
                            # Sites
                            sites = user_access.get_accessible_sites()
                            sites_list = []
                            for site in sites:
                                site_json = site.to_json()
                                site_json['site_role'] = user_access.get_site_role(site.id_site)
                                sites_list.append(site_json)
                            user_json['sites'] = sites_list

                            # Projects
                            projects = user_access.get_accessible_projects()
                            proj_list = []
                            for project in projects:
                                proj_json = project.to_json()
                                proj_json['project_role'] = user_access.get_project_role(project.id_project)
                                proj_list.append(proj_json)
                            user_json['projects'] = proj_list
                        if args['with_usergroups']:
                            # Append user groups
                            user_groups_list = []
                            for user_group in user.user_user_groups:
                                user_groups_list.append(user_group.to_json(minimal=True))
                            user_json['user_groups'] = user_groups_list
                        users_list.append(user_json)
                    else:
                        users_list.append(user.to_json(minimal=True))
            return jsonify(users_list)

        return '', 500
        # try:
        #     users = TeraUser.query_data(my_args)
        #     users_list = []
        #     for user in users:
        #         users_list.append(user.to_json())
        #     return jsonify(users_list)
        # except InvalidRequestError:
        #     return '', 500

    @user_multi_auth.login_required
    @api.expect(post_parser)
    @api.doc(description='Create / update user. id_user must be set to "0" to create a new user. User can be modified '
                         'if: current user is super admin or user is part of a project which the current user is admin.'
                         ' Promoting a user to super admin is restricted to super admins.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified user',
                        400: 'Badly formed JSON or missing field(id_user or missing password when new user) in the '
                             'JSON body',
                        409: 'Username is already taken',
                        500: 'Internal error when saving user'})
    def post(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])

        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        json_user = request.json['user']

        # Validate if we have an id_user
        if 'id_user' not in json_user:
            return '', 400

        # Check if current user can modify the posted user
        if json_user['id_user'] not in user_access.get_accessible_users_ids(admin_only=True) and \
                json_user['id_user'] > 0:
            return '', 403

        # Only superadmin can modify superadmin status
        if not current_user.user_superadmin and json_user['user_superadmin']:
            # Remove field
            json_user.pop('user_superadmin')

        # Do the update!
        if json_user['id_user'] > 0:
            # Already existing user
            try:
                TeraUser.update(json_user['id_user'], json_user)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # New user, check if password is set
            if 'user_password' not in json_user:
                return gettext('Password required'), 400
            if json_user['user_password'] is None or json_user['user_password'] == '':
                return gettext('Invalid password'), 400

            # Check if username is already taken
            if TeraUser.get_user_by_username(json_user['user_username']) is not None:
                return gettext('Username unavailable.'), 409

            # Ok so far, we can try to create the user!
            try:
                new_user = TeraUser()
                new_user.from_json(json_user)
                TeraUser.insert(new_user)
                # Update ID User for further use
                json_user['id_user'] = new_user.id_user
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        # TODO: Publish update to everyone who is subscribed to users update...
        update_user = TeraUser.get_user_by_id(json_user['id_user'])

        return jsonify([update_user.to_json()])

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific user',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete user (only super admin can delete)',
                        500: 'Database error.'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        # userAccess = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        if not current_user.user_superadmin:
            return '', 403

        # If we are here, we are allowed to delete that user. Do so.
        try:
            TeraUser.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200

