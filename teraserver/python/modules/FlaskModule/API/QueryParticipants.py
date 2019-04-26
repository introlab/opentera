from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError


class QueryParticipants(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = reqparse.RequestParser()
        parser.add_argument('id_participant', type=int, help='id_participant')
        parser.add_argument('id_kit', type=int)
        # parser.add_argument('participant_uuid', type=str, help='participant_uuid')
        # parser.add_argument('participant_name', type=str, help='participant_name')

        args = parser.parse_args()

        participants = []
        # If we have no arguments, return all accessible participants
        if not any(args.values()):
            participants = user_access.get_accessible_participants()
        elif args['id_participant']:
            if args['id_participant'] in user_access.get_accessible_participants_ids():
                participants = TeraParticipant.get_participant_by_id(args['id_participant'])
        elif args['id_kit']:
            participants = user_access.query_participants_for_kit(args['id_kit'])

        try:
            participant_list = []
            for participant in participants:
                participant_json = participant.to_json()
                if args['id_kit']:
                    # Adds kit information to participant
                    participant_json['id_kit'] = args['id_kit']
                participant_list.append(participant_json)
            return jsonify(participant_list)

        except InvalidRequestError:
            return '', 500

    @auth.login_required
    def post(self):
        return '', 501

    @auth.login_required
    def delete(self):
        return '', 501
