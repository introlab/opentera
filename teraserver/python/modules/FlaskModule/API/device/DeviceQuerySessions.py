from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSession import TeraSession
from libtera.db.DBManager import DBManager
from modules.LoginModule.LoginModule import LoginModule, current_device
from sqlalchemy import exc
from flask_babel import gettext
from sqlalchemy.exc import InvalidRequestError


class DeviceQuerySessions(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @LoginModule.certificate_required
    def get(self):
        device_access = DBManager.deviceAccess(current_device)

        parser = reqparse.RequestParser()
        parser.add_argument('id_session', type=int, help='id_session')
        # parser.add_argument('id_participant', type=int)
        # parser.add_argument('list', type=bool)
        #
        args = parser.parse_args()
        #
        sessions = []
        # Can't query sessions, unless we have a parameter!
        if not any(args.values()):
            return '', 500
        # elif args['id_participant']:
        #     if args['id_participant'] in user_access.get_accessible_participants_ids():
        #         sessions = TeraSession.get_sessions_for_participant(args['id_participant'])
        elif args['id_session']:
            sessions = device_access.query_session(session_id=args['id_session'])

        try:
            sessions_list = []
            for ses in sessions:
                if args['list'] is None:
                    session_json = ses.to_json()
                    sessions_list.append(session_json)
                else:
                    session_json = ses.to_json(minimal=True)
                    sessions_list.append(session_json)

            return jsonify(sessions_list)

        except InvalidRequestError:
            return '', 500

    @LoginModule.certificate_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('session', type=str, location='json', help='Session to create / update',
                            required=True)

        # Using request.json instead of parser, since parser messes up the json!
        if 'session' not in request.json:
            return '', 400

        json_session = request.json['session']

        device_access = DBManager.deviceAccess(current_device)

        # Validate if we have an id
        if 'id_session' not in json_session:
            return '', 400

        can_update = False
        session_parts_ids = []
        if json_session['id_session'] == 0:
            # New session - check if we have a participant list
            if 'session_participants_ids' not in json_session:
                return gettext('Participants absents'), 400
            session_parts_ids = json_session['session_participants_ids']
        else:
            # Query the session
            ses_to_update = TeraSession.get_session_by_id(json_session['id_session'])
            for part in ses_to_update.session_participants:
                session_parts_ids.append(part.id_participant)

        accessibles_ids = device_access.get_accessible_participants_ids()
        for part_id in session_parts_ids:
            if part_id in accessibles_ids:
                can_update = True
                break

        if not can_update:
            return gettext('Vous n\'avez pas acces a au moins un participant de la seance.'), 403

        # Do the update!
        if json_session['id_session'] > 0:
            # Already existing
            try:
                TeraSession.update_session(json_session['id_session'], json_session)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # New
            try:
                new_ses = TeraSession()
                new_ses.from_json(json_session)
                TeraSession.insert_session(new_ses)
                # Update ID for further use
                json_session['id_session'] = new_ses.id_session
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_session = TeraSession.get_session_by_id(json_session['id_session'])

        return jsonify([update_session.to_json()])

    @LoginModule.certificate_required
    def delete(self):
        return '', 403
