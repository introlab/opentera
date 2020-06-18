from flask import request
from flask_restx import Resource
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from libtera.db.models.TeraParticipant import TeraParticipant
from modules.DatabaseModule.DBManager import db
import uuid
from datetime import datetime
from libtera.db.models.TeraService import TeraService
from libtera.db.models.TeraSession import TeraSession, TeraSessionStatus
from libtera.db.models.TeraSessionType import TeraSessionType
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraDevice import TeraDevice
import datetime
import json

# Parser definition(s)
get_parser = api.parser()
post_parser = api.parser()


class ServiceQuerySessions(Resource):

    # Handle auth
    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @LoginModule.service_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return sessions information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        return 'Not implemented', 501

    @LoginModule.service_token_or_certificate_required
    # @api.expect(post_parser)
    # @api.expect(participant_schema, validate=True)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def post(self):

        service_req = request.json
        # TODO validate json
        if 'create_session' in service_req:
            session_args = service_req['create_session']

            # Create session
            session = TeraSession()

            # Get Service
            if 'id_service' in session_args:
                session.id_creator_service = session_args['id_service']
            else:
                return 'Missing id_service', 500

            # Get Creator (always user?)
            if 'id_creator_user' in session_args:
                session.id_creator_user = session_args['id_creator_user']
            else:
                return 'Missing id_creator_user', 500

            # Get session type
            if 'id_session_type' in session_args:
                session.id_session_type = session_args['id_session_type']
            else:
                return 'Missing id_session_type', 500

            # Optional parameters
            if 'parameters' in session_args:
                session.session_parameters = session_args['parameters']

            # Set session name
            session.session_comments = 'Created by service for user ' + str(session.id_creator_user)
            session.session_start_datetime = datetime.datetime.now()
            session.session_name = TeraSessionType.get_session_type_by_id(session.id_session_type).session_type_name + \
                                   ' [' + str(session.session_start_datetime) + ']'
            session.session_status = TeraSessionStatus.STATUS_INPROGRESS.value

            # insert/commit session, will create uuid
            # Required before adding users, participants, etc.
            TeraSession.insert(session)

            # Get users
            if 'users' in session_args:
                for user_uuid in session_args['users']:
                    session.session_users.append(TeraUser.get_user_by_uuid(user_uuid))
            # Get participants
            if 'participants' in session_args:
                for participant_uuid in session_args['participants']:
                    session.session_participants.append(TeraParticipant.get_participant_by_uuid(participant_uuid))

            # (FUTURE) Get devices
            if 'devices' in session_args:
                for device_uuid in session_args['devices']:
                    pass
                    # session.session_devices.append(TeraDevice.get_device_by_uuid(device_uuid))

            session.commit()

            # Return session info
            return session.to_json(minimal=False), 200

        return 'missing json fields', 500
