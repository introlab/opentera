from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError


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

        args = parser.parse_args()

        groups = []
        # If we have no arguments, return all accessible participants
        if not any(args.values()):
            groups = user_access.get_accessible_groups()
        elif args['id_group']:
            if args['id_group'] in user_access.get_accessible_groups_ids():
                groups = TeraParticipantGroup.get_participant_group_by_id(args['id_group'])
        elif args['id_project']:
            if args['id_project'] in user_access.get_accessible_projects_ids():
                groups = TeraParticipantGroup.get_participant_group_for_project(args['id_project'])

        try:
            group_list = []
            for group in groups:
                group_json = group.to_json()
                group_list.append(group_json)
            return jsonify(group_list)

        except InvalidRequestError:
            return '', 500

    @auth.login_required
    def post(self):
        return '', 501

    @auth.login_required
    def delete(self):
        return '', 501
