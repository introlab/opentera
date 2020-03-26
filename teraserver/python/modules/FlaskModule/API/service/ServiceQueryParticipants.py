from flask import jsonify, session, request
from flask_restplus import Resource, reqparse, fields, inputs
from modules.LoginModule.LoginModule import LoginModule
from modules.FlaskModule.FlaskModule import service_api_ns as api
from libtera.db.models.TeraParticipant import TeraParticipant
from libtera.db.models.TeraParticipantGroup import TeraParticipantGroup
from libtera.db.DBManager import DBManager, db
import uuid
from datetime import datetime

# Parser definition(s)
get_parser = api.parser()
post_parser = api.parser()


participant_schema = api.schema_model('participant', {
    'properties': {
        'participant': {
            'type': 'object',
            'properties': {
                'id_participant': {
                    'type': 'integer'
                },
                'id_project': {
                    'type': 'integer'
                },
                'participant_email': {
                    'type': 'string'
                },
                'participant_name': {
                    'type': 'string'
                }
            },
            'required': ['id_participant', 'id_project', 'participant_email', 'participant_name']
        },

    },
    'type': 'object',
    'required': ['participant']
})


class ServiceQueryParticipants(Resource):

    # Handle auth
    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @LoginModule.service_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return participant information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        print('hello')
        return 'Not implemented', 501

    @LoginModule.service_token_or_certificate_required
    # @api.expect(post_parser)
    @api.expect(participant_schema, validate=True)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def post(self):
        args = post_parser.parse_args()

        # Using request.json instead of parser, since parser messes up the json!
        if 'participant' not in request.json:
            return '', 400

        participant_info = request.json['participant']

        # All fields validation
        if participant_info['id_project'] < 1:
            return 'Unknown project', 403

        if not participant_info['participant_name']:
            return 'Invalid participant name', 403

        if not participant_info['participant_email']:
            return 'Invalid participant email', 403

        # Everything ok...
        # Create a new participant?
        if participant_info['id_participant'] == 0:
            # Create participant
            participant = TeraParticipant()
            participant.participant_uuid = str(uuid.uuid4())
            participant.participant_name = participant_info['participant_name']
            participant.participant_email = participant_info['participant_email']
            participant.id_project = participant_info['id_project']
            participant.participant_enabled = True
            participant.participant_login_enabled = True
            participant.participant_lastonline = datetime.now()
            # Generate token
            participant.create_token()
            db.session.add(participant)
            db.session.commit()
        else:
            # Update participant
            participant = TeraParticipant.get_participant_by_id(participant_info['id_participant'])
            participant.participant_name = participant_info['participant_name']
            participant.participant_email = participant_info['participant_email']
            participant.participant_enabled = True
            participant.participant_login_enabled = True
            participant.participant_lastonline = datetime.now()
            # Re-Generate token
            participant.create_token()
            db.session.add(participant)
            db.session.commit()

        # Return participant information
        return participant.to_json(minimal=False)
