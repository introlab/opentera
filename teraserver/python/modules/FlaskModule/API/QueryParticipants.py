from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from sqlalchemy.exc import InvalidRequestError


class QueryParticipants(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id_participant', type=int, help='id_participant')
        self.parser.add_argument('participant_uuid', type=str, help='participant_uuid')
        self.parser.add_argument('participant_name', type=str, help='participant_name')

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        args = self.parser.parse_args()

        participants = []
        # If we have no arguments, return all accessible devices
        try:
            if not any(args.values()):
                participants = current_user.get_accessible_participants()

            participant_list = []
            for participant in participants:
                participant_json = participant.to_json()
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
