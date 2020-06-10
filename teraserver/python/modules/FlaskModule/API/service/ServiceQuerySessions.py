from flask import request
from flask_restx import Resource
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from libtera.db.models.TeraParticipant import TeraParticipant
from modules.DatabaseModule.DBManager import db
import uuid
from datetime import datetime
from libtera.db.models.TeraService import TeraService
from libtera.db.models.TeraSession import TeraSession
from libtera.db.models.TeraUser import TeraUser
import datetime

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

        # Get Service
        service = TeraService.get_service_by_id(3)

        # Get the creator of the session
        user = TeraUser.get_user_by_id(1)

        # Create session
        session = TeraSession()
        session.id_creator_user = user.id_user
        session.id_session_type = 1

        session.session_comments = 'Created by service'
        session.session_start_datetime = datetime.datetime.now()

        # Add participants


        db.session.add(session)
        db.session.commit()

        return 'Not implemented', 501
