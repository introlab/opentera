from flask import jsonify, request, session
from flask_restx import Resource, reqparse
from flask_babel import gettext
from opentera.db.models.TeraSessionEvent import TeraSessionEvent
from modules.LoginModule.LoginModule import LoginModule
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy import exc
from modules.FlaskModule.FlaskModule import device_api_ns as api
from opentera.db.models.TeraDevice import TeraDevice

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('token', type=str, help='Secret Token')
get_parser.add_argument('id_session', type=int, help='Session ID', required=True)

post_parser = api.parser()


class DeviceQuerySessionEvents(Resource):

    def __init__(self, _api, flaskModule=None):
        Resource.__init__(self, _api)
        self.module = flaskModule

    @LoginModule.device_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Get session events',
             responses={403: 'Forbidden for security reasons.'})
    def get(self):

        # current_device = TeraDevice.get_device_by_uuid(session['_user_id'])
        # device_access = DBManager.deviceAccess(current_device)
        # args = get_parser.parse_args()
        #
        # sessions_events = []
        #
        # parent_session = device_access.query_session(args['id_session'])
        # if not parent_session:
        #     return '', 403
        #
        # sessions_events = TeraSessionEvent.get_events_for_session(args['id_session'])
        #
        # try:
        #     events_list = []
        #     for event in sessions_events:
        #         event_json = event.to_json(minimal=False)
        #         events_list.append(event_json)
        #
        #     return jsonify(events_list)
        #
        # except InvalidRequestError:
        #     return '', 500
        return gettext('Forbidden for security reasons'), 403

    @LoginModule.device_token_or_certificate_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('session_event', type=str, location='json', help='Event to create / update',
                            required=True)

        current_device = TeraDevice.get_device_by_uuid(session['_user_id'])
        device_access = DBManager.deviceAccess(current_device)

        # Using request.json instead of parser, since parser messes up the json!
        if 'session_event' not in request.json:
            return gettext('Missing arguments'), 400

        json_event = request.json['session_event']

        # Validate if we have an id
        if 'id_session' not in json_event or 'id_session_event' not in json_event:
            return gettext('Missing arguments'), 400

        # Check if current user can modify the posted event
        # User can modify or add an event if they have access to the parent session

        parent_session = device_access.query_session(json_event['id_session'])

        if not parent_session:
            return gettext('Unauthorized'), 403

        # Do the update!
        if json_event['id_session_event'] > 0:
            # Already existing
            try:
                TeraSessionEvent.update(json_event['id_session_event'], json_event)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             DeviceQuerySessionEvents.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500
        else:
            # New
            try:
                new_event = TeraSessionEvent()
                new_event.from_json(json_event)
                TeraSessionEvent.insert(new_event)
                # Update ID for further use
                json_event['id_session_event'] = new_event.id_session
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             DeviceQuerySessionEvents.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_event = TeraSessionEvent.get_session_event_by_id(json_event['id_session_event'])

        return jsonify([update_event.to_json()])

    @LoginModule.device_token_or_certificate_required
    def delete(self):
        return gettext('Forbidden for security reasons'), 403
