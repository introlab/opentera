from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from sqlalchemy import exc
from modules.Globals import auth
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSite import TeraSite
from libtera.db.DBManager import DBManager


class QuerySites(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id_site', type=int, help='id_site', required=False)
        parser.add_argument('id', type=int, help='id_site', required=False)
        parser.add_argument('id_device', type=int, help='ID Device')
        parser.add_argument('user_uuid', type=str, help='uuid')

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        args = parser.parse_args()

        sites = []
        if args['id']:
            args['id_site'] = args['id']

        # If we have no arguments, return all accessible sites
        if not any(args.values()):
            sites = user_access.get_accessible_sites()
        # If we have a user_uuid, query for the site of that user
        elif args['user_uuid']:
            queried_user = TeraUser.get_user_by_uuid(args['user_uuid'])
            if queried_user is not None:
                current_sites = user_access.get_accessible_sites()
                user_access = DBManager.userAccess(queried_user)
                queried_sites = user_access.get_accessible_sites()
                # Match with accessible sites for the current user
                for site in queried_sites:
                    if site in current_sites:
                        sites.append(site)
        elif args['id_site']:
            if args['id_site'] in user_access.get_accessible_sites_ids():
                sites = sites.append(TeraSite.get_site_by_id(site_id=args['id_site']))
        elif args['id_device']:
            sites = user_access.query_sites_for_device(args['id_device'])

        try:
            sites_list = []
            for site in sites:
                if site is not None:
                    site_json = site.to_json()
                    site_json['site_role'] = user_access.get_site_role(site_json['id_site'])
                    if args['id_device']:
                        site_json['id_device'] = args['id_device']
                    sites_list.append(site_json)
            return jsonify(sites_list)
        except InvalidRequestError:
            return '', 500

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('site', type=str, location='json', help='Site to create / update', required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_site = request.json['site']

        # Validate if we have an id
        if 'id_site' not in json_site:
            return '', 400

        # Check if current user can modify the posted site
        if json_site['id_site'] not in user_access.get_accessible_sites_ids(admin_only=True) and \
                json_site['id_site'] > 0:
            return '', 403

        # Do the update!
        if json_site['id_site'] > 0:
            # Already existing
            try:
                TeraSite.update_site(json_site['id_site'], json_site)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # New
            try:
                new_site = TeraSite()
                new_site.from_json(json_site)
                TeraSite.insert_site(new_site)
                # Update ID for further use
                json_site['id_site'] = new_site.id_site
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_site = TeraSite.get_site_by_id(json_site['id_site'])

        return jsonify([update_site.to_json()])

    @auth.login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # Only superadmin can delete sites from here
        if not current_user.user_superadmin:
            return '', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraSite.delete_site(id_site=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200
