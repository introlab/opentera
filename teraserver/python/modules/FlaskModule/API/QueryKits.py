from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraKit import TeraKit
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError


class QueryKits(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = reqparse.RequestParser()
        parser.add_argument('id_kit', type=int, help='id_kit')
        parser.add_argument('id_site', type=int, help='id site')
        parser.add_argument('id_project', type=int)

        args = parser.parse_args()

        kits = []
        # If we have no arguments, return all accessible devices
        if not any(args.values()):
            kits = user_access.get_accessible_kits()
        elif args['id_kit']:
            if args['id_kit'] in user_access.get_accessible_kits_ids():
                kits = [TeraKit.get_kit_by_id(kit_id=args['id_kit'])]
        elif args['id_project']:
            if args['id_project'] in user_access.get_accessible_projects_ids():
                kits = TeraKit.get_kits_for_project(project_id=args['id_project'])
        elif args['id_site']:
            if args['id_site'] in user_access.get_accessible_sites_ids():
                kits = TeraKit.get_kits_for_site(site_id=args['id_site'])

        try:
            kit_list = []
            for kit in kits:
                kit_json = kit.to_json()
                kit_list.append(kit_json)
            return jsonify(kit_list)

        except InvalidRequestError:
            return '', 500

    @auth.login_required
    def post(self):
        return '', 501

    @auth.login_required
    def delete(self):
        return '', 501
