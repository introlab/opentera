from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from modules.LoginModule.LoginModule import multi_auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSessionEvent import TeraSessionEvent
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext


class QuerySessionEvents(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @multi_auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = reqparse.RequestParser()
        parser.add_argument('id_session', type=int, help='id_session')

        args = parser.parse_args()

        sessions_events = []
        # Can't query sessions event, unless we have a parameter - id_session
        if not any(args.values()):
            return '', 500
        elif args['id_session']:
            sessions_events = user_access.query_session_events(args['id_session'])

        try:
            events_list = []
            for event in sessions_events:
                event_json = event.to_json(minimal=False)
                events_list.append(event_json)

            return jsonify(events_list)

        except InvalidRequestError:
            return '', 500

    @multi_auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('session_event', type=str, location='json', help='Event to create / update',
                            required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        if 'session_event' not in request.json:
            return '', 400

        json_event = request.json['session_event']

        # Validate if we have an id
        if 'id_session' not in json_event or 'id_session_event' not in json_event:
            return '', 400

        # Check if current user can modify the posted event
        # User can modify or add an event if they have access to the parent session

        parent_session = user_access.query_session(json_event['id_session'])

        if not parent_session:
            return '', 403

        # Do the update!
        if json_event['id_session_event'] > 0:
            # Already existing
            try:
                TeraSessionEvent.update(json_event['id_session_event'], json_event)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # New
            try:
                new_event = TeraSessionEvent()
                new_event.from_json(json_event)
                TeraSessionEvent.insert(new_event)
                # Update ID for further use
                json_event['id_session_event'] = new_event.id_session
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_event = TeraSessionEvent.get_session_event_by_id(json_event['id_session_event'])

        return jsonify([update_event.to_json()])

    @multi_auth.login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        session_event = TeraSessionEvent.get_session_event_by_id(event_id=args['id'])
        # User can delete a session event if it has access to the session
        parent_session = user_access.query_session(session_event.id_session)

        if not parent_session:
            return '', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraSessionEvent.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200
