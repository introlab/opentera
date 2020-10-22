from flask import jsonify, session, request
from flask_restx import Resource, reqparse
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSessionEvent import TeraSessionEvent
from libtera.db.models.TeraSession import TeraSession
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_session', type=int, help='ID of the session to query events for', required=True)

post_schema = api.schema_model('service_session_event', {'properties': TeraSessionEvent.get_json_schema(),
                                                         'type': 'object', 'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Session event ID to delete', required=True)


class ServiceQuerySessionEvents(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @LoginModule.service_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Get events for a specific session',
             responses={200: 'Success - returns list of events',
                        400: 'Required parameter is missing (id_session)',
                        500: 'Database error'})
    def get(self):
        parser = get_parser

        args = parser.parse_args()

        sessions_events = []

        # Can't query sessions event, unless we have a parameter - id_session
        if not any(args.values()):
            return gettext('Missing arguments'), 400
        elif args['id_session']:
            sessions_events = TeraSessionEvent.get_events_for_session(args['id_session'])

        try:
            events_list = []
            for event in sessions_events:
                event_json = event.to_json(minimal=False)
                events_list.append(event_json)

            return events_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQuerySessionEvents.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @LoginModule.service_token_or_certificate_required
    @api.expect(post_schema)
    @api.doc(description='Create / update session events. id_session_event must be set to "0" to create a new '
                         'event. An event can be created/modified if the user has access to the session.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified event',
                        400: 'Badly formed JSON or missing fields(id_session_event or id_session) in the JSON body',
                        500: 'Internal error when saving device'})
    def post(self):
        # Using request.json instead of parser, since parser messes up the json!
        if 'session_event' not in request.json:
            return gettext('Missing session_event field'), 400

        json_event = request.json['session_event']

        # Validate if we have an id
        if 'id_session' not in json_event or 'id_session_event' not in json_event:
            return gettext('Missing id_session or id_session_event fields'), 400

        parent_session = TeraSession.get_session_by_id(json_event['id_session'])

        if not parent_session:
            return gettext('Forbidden'), 403

        # Do the update!
        if json_event['id_session_event'] > 0:
            # Already existing
            try:
                TeraSessionEvent.update(json_event['id_session_event'], json_event)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                self.module.logger.log_error(self.module.module_name,
                                             ServiceQuerySessionEvents.__name__,
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
                                             ServiceQuerySessionEvents.__name__,
                                             'post', 500, 'Database error', str(e))
                return gettext('Database error'), 500

        update_event = TeraSessionEvent.get_session_event_by_id(json_event['id_session_event'])

        return [update_event.to_json()]

    # No delete for now!

    # @LoginModule.service_token_or_certificate_required
    # @api.expect(delete_parser)
    # @api.doc(description='Delete a specific session event',
    #          responses={200: 'Success',
    #                     403: 'Logged user can\'t delete event (no access to that session)',
    #                     500: 'Database error.'})
    # def delete(self):
    #     parser = delete_parser
    #
    #     args = parser.parse_args()
    #     id_todel = args['id']
    #
    #     # Check if current user can delete
    #     session_event = TeraSessionEvent.get_session_event_by_id(event_id=args['id'])
    #     # User can delete a session event if it has access to the session
    #     parent_session = TeraSession.get_session_by_id(session_event.id_session)
    #
    #     if not parent_session:
    #         return gettext('Forbidden'), 403
    #
    #     # If we are here, we are allowed to delete. Do so.
    #     try:
    #         TeraSessionEvent.delete(id_todel=id_todel)
    #     except exc.SQLAlchemyError:
    #         import sys
    #         print(sys.exc_info())
    #         return gettext('Database error'), 500
    #
    #     return '', 200
