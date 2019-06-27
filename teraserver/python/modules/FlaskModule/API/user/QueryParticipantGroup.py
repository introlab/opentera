from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc


class QueryParticipantGroup(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = reqparse.RequestParser()
        parser.add_argument('id_group', type=int)
        parser.add_argument('id_project', type=int)
        parser.add_argument('list', type=bool)
        parser.add_argument('id', type=int)

        args = parser.parse_args()

        groups = []
        # If we have no arguments, return all accessible participants
        if args['id']:
            args['id_group'] = args['id']

        if not any(args.values()):
            groups = user_access.get_accessible_groups()
        elif args['id_group']:
            if args['id_group'] in user_access.get_accessible_groups_ids():
                groups = [TeraParticipantGroup.get_participant_group_by_id(args['id_group'])]
        elif args['id_project']:
            if args['id_project'] in user_access.get_accessible_projects_ids():
                groups = TeraParticipantGroup.get_participant_group_for_project(args['id_project'])

        try:
            group_list = []
            for group in groups:
                if args['list'] is None:
                    group_json = group.to_json()
                    group_list.append(group_json)
                else:
                    group_json = group.to_json(minimal=True)
                    group_json['group_participant_count'] = len(user_access.query_participants_for_group(
                        group.id_participant_group))
                    group_list.append(group_json)
            return jsonify(group_list)

        except InvalidRequestError:
            return '', 500

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('group', type=str, location='json', help='Group to create / update', required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        if 'group' not in request.json:
            return '', 400

        json_group = request.json['group']

        # Validate if we have an id
        if 'id_participant_group' not in json_group or 'id_project' not in json_group:
            return '', 400

        # Check if current user can modify the posted group
        # User can modify or add a group if it has admin access to that project
        if json_group['id_project'] not in user_access.get_accessible_projects_ids(admin_only=True):
            return '', 403

        # Do the update!
        if json_group['id_participant_group'] > 0:
            # Already existing
            try:
                TeraParticipantGroup.update_participant_group(json_group['id_participant_group'], json_group)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # New
            try:
                new_group = TeraParticipantGroup()
                new_group.from_json(json_group)
                TeraParticipantGroup.insert_participant_group(new_group)
                # Update ID for further use
                json_group['id_participant_group'] = new_group.id_participant_group
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_group = TeraParticipantGroup.get_participant_group_by_id(json_group['id_participant_group'])

        return jsonify([update_group.to_json()])

    @auth.login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # Only projects admins can delete a group
        group = TeraParticipantGroup.get_participant_group_by_id(id_todel)

        if user_access.get_project_role(group.id_project) != 'admin':
            return '', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraParticipantGroup.delete_participant_group(id_participant_group=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200
