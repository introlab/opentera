from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from sqlalchemy import exc
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from flask_babel import gettext
from libtera.db.DBManager import DBManager
from libtera.db.DBManagerTeraUserAccess import DBManagerTeraUserAccess


class QueryUsers(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user_uuid', type=str, help='uuid')
        parser.add_argument('id_user', type=int, help='User ID')
        parser.add_argument('list', type=bool, help='Request user list (ID, name, enabled)')

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        args = parser.parse_args()

        user_access = DBManager.userAccess(current_user)

        users = []
        # If we have no arguments, return all accessible users
        if not any(args.values()):
            users = user_access.get_accessible_users()

        # If we have a user_uuid, query for that user if accessible
        if args['user_uuid']:
            if args['user_uuid'] in user_access.get_accessible_users_uuids():
                users.append(TeraUser.get_user_by_uuid(args['user_uuid']))
        if args['id_user']:
            if args['id_user'] in user_access.get_accessible_users_ids():
                users.append(current_user.get_user_by_id(args['id_user']))

        # If we have a id_project, query for users of that project, if accessible
        # TODO

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

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('user', type=str, location='json', help='User to create / update', required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])

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

        # Check if we have site access to handle separately
        json_sites = None
        if 'sites' in json_user:
            json_sites = json_user.pop('sites')

        # Check if we have project access to handle separately
        json_projects = None
        if 'projects' in json_user:
            json_projects = json_user.pop('projects')

        # Do the update!
        if json_user['id_user'] > 0:
            # Already existing user
            try:
                TeraUser.update_user(json_user['id_user'], json_user)
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
                TeraUser.insert_user(new_user)
                # Update ID User for further use
                json_user['id_user'] = new_user.id_user;
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        if json_sites:
            for site in json_sites:
                # Check if current user is admin of that site
                if user_access.get_site_role(site=site) == 'admin':
                    try:
                        TeraSiteAccess.update_site_access(json_user['id_user'], site['id_site'], site['site_role'])
                    except exc.SQLAlchemyError:
                        import sys
                        print(sys.exc_info())
                        return '', 500

        if json_projects:
            for project in json_projects:
                # Check if current user is admin of that site
                if user_access.get_project_role(project=project) == 'admin':
                    try:
                        TeraProjectAccess.update_project_access(id_user=json_user['id_user'],
                                                                id_project=project['id_project'],
                                                                rolename=project['project_role'])
                    except exc.SQLAlchemyError:
                        import sys
                        print(sys.exc_info())
                        return '', 500

        # TODO: Publish update to everyone who is subscribed to users update...
        update_user = TeraUser.get_user_by_id(json_user['id_user'])

        return jsonify([update_user.to_json()])

    @auth.login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        userAccess = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # Only superadmin can delete users from here
        if not current_user.user_superadmin:
            return '', 403

        # If we are here, we are allowed to delete that user. Do so.
        try:
            TeraUser.delete_user(id_user=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200
