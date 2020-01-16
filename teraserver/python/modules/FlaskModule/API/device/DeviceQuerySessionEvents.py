from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSessionEvent import TeraSessionEvent
from modules.LoginModule.LoginModule import LoginModule, current_device
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc


class DeviceQuerySessionEvents(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @LoginModule.token_or_certificate_required
    def get(self):
        device_access = DBManager.deviceAccess(current_device)

        parser = reqparse.RequestParser()
        parser.add_argument('id_session', type=int, help='id_session')

        args = parser.parse_args()

        sessions_events = []
        # Can't query sessions event, unless we have a parameter - id_session
        if not any(args.values()):
            return '', 500
        elif args['id_session']:
            parent_session = device_access.query_session(args['id_session'])
            if not parent_session:
                return '', 403
            sessions_events = TeraSessionEvent.get_events_for_session(args['id_session'])

        try:
            events_list = []
            for event in sessions_events:
                event_json = event.to_json(minimal=False)
                events_list.append(event_json)

            return jsonify(events_list)

        except InvalidRequestError:
            return '', 500

    @LoginModule.token_or_certificate_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('session_event', type=str, location='json', help='Event to create / update',
                            required=True)

        device_access = DBManager.deviceAccess(current_device)

        # Using request.json instead of parser, since parser messes up the json!
        if 'session_event' not in request.json:
            return '', 400

        json_event = request.json['session_event']

        # Validate if we have an id
        if 'id_session' not in json_event or 'id_session_event' not in json_event:
            return '', 400

        # Check if current user can modify the posted event
        # User can modify or add an event if they have access to the parent session

        parent_session = device_access.query_session(json_event['id_session'])

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

    @LoginModule.token_or_certificate_required
    def delete(self):
        return '', 403
