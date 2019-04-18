from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from sqlalchemy import exc
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from flask_babel import gettext


class QuerySiteAccess(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id_user', type=int, help='User ID')
        parser.add_argument('id_site', type=int, help='Site ID')

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        args = parser.parse_args()

        access = None
        # If we have no arguments, return bad request
        if not any(args.values()):
            return "SiteAccess: missing argument.", 400

        # Query access for user id
        if args['id_user']:
            user_id = args['id_user']

            if user_id in current_user.get_accessible_users_ids():
                access = TeraSiteAccess.query_access_for_user(current_user=current_user, user_id=user_id)

        # Query access for site id
        if args['id_site']:
            site_id = args['id_site']
            access = TeraSiteAccess.query_access_for_site(current_user=current_user, site_id=site_id)

        if access is not None:
            access_list = []
            for site_access in access:
                if site_access is not None:
                    access_list.append(site_access.to_json())
            return jsonify(access_list)

        return 'Unknown error', 500

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('site_access', type=str, location='json', help='Site access to create / update',
                            required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        # Using request.json instead of parser, since parser messes up the json!
        json_site = request.json['site_access']

        # Validate if we have an id_user
        if 'id_site_access' not in json_site:
            return 'Missing id_site_access', 400

        # Check if current user can change the access for that site
        if current_user.get_site_role(site=json_site) != 'admin':
            return 'Forbidden', 403

        # Do the update!
        try:
            access = TeraSiteAccess.update_access(json_site['id_user'], json_site['id_site'], json_site['site_role'])
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return '', 500

        # TODO: Publish update to everyone who is subscribed to site access update...

        return jsonify(access.to_json())

    @auth.login_required
    def delete(self):
        # parser = reqparse.RequestParser()
        # parser.add_argument('id', type=int, help='ID to delete', required=True)
        # current_user = TeraUser.get_user_by_uuid(session['user_id'])
        #
        # args = parser.parse_args()
        # id_todel = args['id']
        #
        # # Check if current user can delete
        # # Only superadmin can delete users from here
        # if not current_user.user_superadmin:
        #     return '', 403
        #
        # # If we are here, we are allowed to delete that user. Do so.
        # try:
        #     TeraUser.delete_user(id_user=id_todel)
        # except exc.SQLAlchemyError:
        #     import sys
        #     print(sys.exc_info())
        #     return 'Database error', 500

        return '', 501

