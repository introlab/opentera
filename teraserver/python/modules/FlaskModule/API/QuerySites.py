from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth, db_man
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSiteAccess import TeraSiteAccess


class QuerySites(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id_site', type=int, help='id_site', required=False)
        self.parser.add_argument('user_uuid', type=str, help='uuid')

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        args = self.parser.parse_args()

        sites = []
        # If we have no arguments, return all accessible sites
        queried_user = current_user
        if not any(args.values()):
            sites = queried_user.get_accessible_sites()

        # If we have a user_uuid, query for the site of that user
        if args['user_uuid']:
            queried_user = TeraUser.get_user_by_uuid(args['user_uuid'])
            if queried_user is not None:
                sites = queried_user.get_accessible_sites()

        try:
            sites_list = []
            for site in sites:
                site_json = site.to_json()
                site_json['site_role'] = queried_user.get_site_role(site)
                sites_list.append(site_json)
            return jsonify(sites_list)
        except InvalidRequestError:
            return '', 500

    def post(self):
        return '', 501

    def delete(self):
        return '', 501
