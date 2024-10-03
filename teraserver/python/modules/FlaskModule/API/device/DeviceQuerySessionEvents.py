from flask import request
from flask_restx import Resource
from flask_babel import gettext
from opentera.db.models.TeraSessionEvent import TeraSessionEvent
from modules.LoginModule.LoginModule import LoginModule, current_device
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy import exc
from modules.FlaskModule.FlaskModule import device_api_ns as api

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_session', type=int, help='Session ID', required=True)

post_parser = api.parser()


class DeviceQuerySessionEvents(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get session events',
             responses={403: 'Forbidden for security reasons.'},
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @LoginModule.device_token_or_certificate_required
    def get(self):
        """
        Get events for a specific session
        """
        return gettext('Forbidden for security reasons'), 403

    @api.doc(description='Update/Create session events',
             responses={200: 'Success',
                        400: 'Required parameter is missing',
                        500: 'Internal server error',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'},
             params={'token': 'Access token'})
    @api.expect(post_parser)
    @LoginModule.device_token_or_certificate_required
    def post(self):
        """
        Create / update session events
        """
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
                json_event['id_session_event'] = new_event.id_session_event
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             DeviceQuerySessionEvents.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        update_event = TeraSessionEvent.get_session_event_by_id(json_event['id_session_event'])

        return [update_event.to_json()]

    @LoginModule.device_token_or_certificate_required
    def delete(self):
        """
        Delete session events
        """
        return gettext('Forbidden for security reasons'), 403
