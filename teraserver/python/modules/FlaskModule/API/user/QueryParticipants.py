from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraSession import TeraSession
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
        parser.add_argument('id_session', type=int)
        parser.add_argument('id_device', type=int)
        parser.add_argument('list', type=bool)
        # parser.add_argument('participant_uuid', type=str, help='participant_uuid')
        # parser.add_argument('participant_name', type=str, help='participant_name')

        args = parser.parse_args()

        participants = []
        if args['id']:
            args['id_participant'] = args['id']

        # If we have no arguments, return nothing
        if not any(args.values()):
            return '', 400
        elif args['id_participant']:
            if args['id_participant'] in user_access.get_accessible_participants_ids():
                participants = [TeraParticipant.get_participant_by_id(args['id_participant'])]
        elif args['id_kit']:
            participants = user_access.query_participants_for_kit(args['id_kit'])
        elif args['id_site']:
            participants = user_access.query_participants_for_site(args['id_site'])
        elif args['id_group']:
            participants = user_access.query_participants_for_group(args['id_group'])
        elif args['id_device']:
            participants = user_access.query_participants_for_device(args['id_device'])
        elif args['id_session']:
            part_session = TeraSession.get_session_by_id(args['id_session'])
            participants = []
            accessibles_parts = user_access.get_accessible_participants_ids()
            for part in part_session.session_participants:
                if part.id_participant in accessibles_parts:
                    participants.append(part)

        try:
            participant_list = []
            for participant in participants:
                if args['list'] is None:
                    participant_json = participant.to_json()
                    if args['id_kit']:
                        # Adds kit information to participant
                        participant_json['id_kit'] = args['id_kit']
                    if args['id_participant']:
                        # Adds project information to participant
                        participant_json['id_project'] = participant.participant_participant_group.id_project
                    if args['id_group']:
                        # Adds last session information to participant
                        participant_sessions = TeraSession.get_sessions_for_participant(
                            part_id=participant.id_participant)
                        if participant_sessions:
                            participant_json['participant_lastsession'] = \
                                participant_sessions[-1].session_start_datetime.isoformat()
                        else:
                            participant_json['participant_lastsession'] = None

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
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # Only project admins can delete a participant
        part = TeraParticipant.get_participant_by_id(id_todel)

        if user_access.get_project_role(part.participant_participant_group.id_project) != 'admin':
            return '', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraParticipant.delete_participant(id_participant=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200

