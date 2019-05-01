from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraKit import TeraKit
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc


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
            else:
                return '', 403
        elif args['id_project']:
            if args['id_project'] in user_access.get_accessible_projects_ids():
                kits = TeraKit.get_kits_for_project(project_id=args['id_project'])
            else:
                return '', 403
        elif args['id_site']:
            if args['id_site'] in user_access.get_accessible_sites_ids():
                kits = TeraKit.get_kits_for_site(site_id=args['id_site'])
            else:
                return '', 403

        try:
            kit_list = []
            for kit in kits:
                kit_json = kit.to_json()
                if args['id_project']:
                    # Append participant(s) using that kit if querying for a specific project
                    part_list = []
                    for part in kit.kit_participants:
                        part_json = {'id_participant': part.id_participant, 'participant_name': part.participant_name}
                        part_list.append(part_json)
                    kit_json['kit_participants'] = part_list
                kit_list.append(kit_json)
            return jsonify(kit_list)

        except InvalidRequestError:
            return '', 500

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('kit', type=str, location='json', help='Kit to create / update', required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_kit = request.json['kit']

        # Validate if we have an id
        if 'id_kit' not in json_kit and 'id_site' not in json_kit:
            return '', 400

        # Check if current user can modify the posted kit
        # User can modify or add a kit if it is the site admin of that kit
        if json_kit['id_site'] not in user_access.get_accessible_sites_ids(admin_only=True) and \
                json_kit['id_site'] > 0:
            return '', 403

        # Do the update!
        if json_kit['id_kit'] > 0:
            # Already existing
            try:
                TeraKit.update_kit(json_kit['id_kit'], json_kit)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # New
            try:
                new_kit = TeraKit()
                new_kit.from_json(json_kit)
                TeraKit.insert_kit(new_kit)
                # Update ID for further use
                json_kit['id_kit'] = new_kit.id_kit
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_kit = TeraKit.get_kit_by_id(json_kit['id_kit'])

        return jsonify([update_kit.to_json()])

    @auth.login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # Only site admins can delete
        kit = TeraKit.get_kit_by_id(id_todel)

        if user_access.get_site_role(kit.kit_site) != 'admin':
            return '', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraKit.delete_kit(id_kit=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200
