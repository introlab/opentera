from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from sqlalchemy import exc
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.DBManager import DBManager


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
        user_access = DBManager.userAccess(current_user)
        args = parser.parse_args()

        access = None
        # If we have no arguments, return bad request
        if not any(args.values()):
            return "SiteAccess: missing argument.", 400

        # Query access for user id
        if args['id_user']:
            user_id = args['id_user']

            if user_id in current_user.get_accessible_users_ids():
                access = user_access.query_access_for_user(user_id=user_id)

        # Query access for site id
        if args['id_site']:
            site_id = args['id_site']
            access = user_access.query_access_for_site(site_id=site_id)

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
        json_sites = request.json['site_access']

        if not isinstance(json_sites, list):
            json_sites = [json_sites]

        # Validate if we have everything needed
        json_rval = []
        for json_site in json_sites:
            if 'id_user' not in json_site:
                return 'Missing id_user', 400
            if 'id_site' not in json_site:
                return 'Missing id_site', 400

            # Check if current user can change the access for that site
            if current_user.get_site_role(site=json_site) != 'admin':
                return 'Forbidden', 403

            # Do the update!
            try:
                access = TeraSiteAccess.update_site_access(json_site['id_user'], json_site['id_site'],
                                                           json_site['site_access_role'])
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

            # TODO: Publish update to everyone who is subscribed to site access update...
            if access:
                json_rval.append(access.to_json())

        return jsonify(json_rval)

    @auth.login_required
    def delete(self):

        return '', 501

