from flask import jsonify, session, request
from flask_restplus import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSession import TeraSession
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_session', type=int, help='ID of the session to query')
get_parser.add_argument('id_participant', type=int, help='ID of the participant from which to get all sessions')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')

post_parser = reqparse.RequestParser()
post_parser.add_argument('session', type=str, location='json', help='Session to create / update', required=True)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Session ID to delete', required=True)


class QuerySessions(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get sessions information. Only one of the ID parameter is supported and required at once',
             responses={200: 'Success - returns list of sessions',
                        400: 'No parameters specified at least one id must be used',
                        500: 'Database error'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()

        sessions = []
        # Can't query sessions, unless we have a parameter!
        if not any(args.values()):
            return '', 400

        elif args['id_participant']:
            if args['id_participant'] in user_access.get_accessible_participants_ids():
                sessions = TeraSession.get_sessions_for_participant(args['id_participant'])
        elif args['id_session']:
            sessions = [user_access.query_session(args['id_session'])]

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

    @user_multi_auth.login_required
    @api.expect(post_parser)
    @api.doc(description='Create / update session. id_session must be set to "0" to create a new '
                         'session. A session can be created/modified if the user has access to at least one participant'
                         ' in the session.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified session',
                        400: 'Badly formed JSON or missing fields(session, id_session, session_participants_ids [for '
                             'new sessions]) in the JSON body',
                        500: 'Internal error when saving device'})
    def post(self):
        # parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        if 'session' not in request.json:
            return '', 400

        json_session = request.json['session']

        # Validate if we have an id
        if 'id_session' not in json_session:
            return '', 400

        # Check if current user can modify the posted group
        # User can modify or add a session if they have access (not necessary admin) to at least a participant in the
        # session

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

        accessibles_ids = user_access.get_accessible_participants_ids()
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
                TeraSession.update(json_session['id_session'], json_session)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # New
            try:
                new_ses = TeraSession()
                new_ses.from_json(json_session)
                TeraSession.insert(new_ses)
                # Update ID for further use
                json_session['id_session'] = new_ses.id_session
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        # TODO: Publish update to everyone who is subscribed to sites update...
        update_session = TeraSession.get_session_by_id(json_session['id_session'])

        return jsonify([update_session.to_json()])

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific session',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete session (must have access to at least one participant in the '
                             'session to delete)',
                        500: 'Database error.'})
    def delete(self):
        parser = delete_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        # User can delete a session if it has access to one of its participant
        todel_session = TeraSession.get_session_by_id(id_todel)
        can_delete = False
        for ses_part in todel_session.session_participants:
            if ses_part in user_access.get_accessible_participants():
                can_delete = True
                break

        if not can_delete:
            return gettext('Vous n\'avez pas acces a au moins un participant de la seance.'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraSession.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200
