from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc


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
        parser.add_argument('id', type=int)
        parser.add_argument('id_kit', type=int)
        parser.add_argument('id_site', type=int, help='id site')
        parser.add_argument('id_group', type=int)
        parser.add_argument('list', type=bool)
        # parser.add_argument('participant_uuid', type=str, help='participant_uuid')
        # parser.add_argument('participant_name', type=str, help='participant_name')

        args = parser.parse_args()

        participants = []
        if args['id']:
            args['id_participant'] = args['id']

        # If we have no arguments, return all accessible participants
        if not any(args.values()):
            participants = user_access.get_accessible_participants()
        elif args['id_participant']:
            if args['id_participant'] in user_access.get_accessible_participants_ids():
                participants = [TeraParticipant.get_participant_by_id(args['id_participant'])]
        elif args['id_kit']:
            participants = user_access.query_participants_for_kit(args['id_kit'])
        elif args['id_site']:
            participants = user_access.query_participants_for_site(args['id_site'])
        elif args['id_group']:
            participants = user_access.query_participants_for_group(args['id_group'])

        try:
            participant_list = []
            for participant in participants:
                if args['list'] is None:
                    participant_json = participant.to_json()
                    if args['id_kit']:
                        # Adds kit information to participant
                        participant_json['id_kit'] = args['id_kit']
                    participant_list.append(participant_json)
                else:
                    participant_json = participant.to_json(minimal=True)
                    participant_list.append(participant_json)

            return jsonify(participant_list)

        except InvalidRequestError:
            return '', 500

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('participant', type=str, location='json', help='Partiicpant to create / update',
                            required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        if 'participant' not in request.json:
            return '', 400

        json_participant = request.json['participant']

        # Validate if we have an id
        if 'id_participant' not in json_participant or 'id_participant_group' not in json_participant:
            return '', 400

        # Check if current user can modify the posted group
        # User can modify or add a group if it has admin access to that project
        if json_participant['id_participant_group'] not in user_access.get_accessible_groups_ids(admin_only=True):
            return '', 403

        # Do the update!
        if json_participant['id_participant'] > 0:
            # Already existing
            try:
                TeraParticipant.update_participant(json_participant['id_participant'], json_participant)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # New
            try:
                new_part = TeraParticipant()
                new_part.from_json(json_participant)
                TeraParticipant.insert_participant(new_part)
                # Update ID for further use
                json_participant['id_participant'] = new_part.id_participant
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_participant = TeraParticipant.get_participant_by_id(json_participant['id_participant'])

        return jsonify([update_participant.to_json()])

    @auth.login_required
    def delete(self):
        return '', 501
