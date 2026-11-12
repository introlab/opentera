
import bcrypt

from flask import jsonify, request
from flask_restx import Resource, inputs
from flask_babel import gettext
from sqlalchemy import exc

from modules.LoginModule.LoginModule import participant_multi_auth, current_participant
from modules.FlaskModule.FlaskModule import participant_api_ns as api
from modules.DatabaseModule.DBManager import DBManager
from opentera.db.models.TeraParticipant import TeraParticipant


# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')

post_schema = api.schema_model('participant_self_update', {
    'type': 'object',
    'properties': {
        'participant': {
            'type': 'object',
            'properties': {
                'participant_name': {'type': 'string'},
                'participant_email': {'type': 'string'}
            },
            'additionalProperties': False
        }
    },
    'required': ['participant'],
    'additionalProperties': False,
    'location': 'json'
})


class ParticipantQueryParticipants(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return participant information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        403: 'Logged user doesn\'t have permission to access the requested data'},
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @participant_multi_auth.login_required(role='limited')
    def get(self):
        """
        Get current participant informations
        """
        args = get_parser.parse_args(strict=True)

        if current_participant.fullAccess:
            minimal = False
            if args['list']:
                minimal = True

            return current_participant.to_json(minimal=minimal)
        else:
            return {
                'participant_name': current_participant.participant_name,
                'participant_email': current_participant.participant_email
            }

    @api.doc(description='Update current participant information. Name and email can be modified '
                         'with limited access. Password changes require full access.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    @api.expect(post_schema)
    @participant_multi_auth.login_required(role='limited')
    def post(self):
        """
        Update current participant informations
        """

        # Using request.json instead of parser, since parser messes up the json!
        if not request.is_json or not isinstance(request.json, dict):
            return gettext('Badly formed JSON'), 400

        if 'participant' not in request.json:
            return gettext('Missing participant'), 400

        json_participant = request.json['participant']

        if not isinstance(json_participant, dict):
            return gettext('Invalid participant information'), 400

        # Only allow participants to modify their name, email and password
        allowed_fields = {
            'participant_name',
            'participant_email',
            'participant_password',
            'current_password',
            'confirm_password'
        }

        if any(field not in allowed_fields for field in json_participant):
            return gettext('Invalid participant fields'), 400

        # Query current participant information
        participant = TeraParticipant.get_participant_by_id(
            current_participant.id_participant
        )

        if not participant:
            return gettext('Participant not found'), 404

        # No ID is required in the JSON, since the participant can only modify itself
        update_values = {}

        # Check if participant name needs to be updated
        if 'participant_name' in json_participant:
            participant_name = json_participant['participant_name']

            if not isinstance(participant_name, str) or not participant_name.strip():
                return gettext('Invalid participant name'), 400

            update_values['participant_name'] = participant_name.strip()

        # Check if participant email needs to be updated
        if 'participant_email' in json_participant:
            participant_email = json_participant['participant_email']

            if not isinstance(participant_email, str) or not participant_email.strip():
                return gettext('Invalid participant email'), 400

            try:
                participant_email = inputs.email()(participant_email.strip())
            except ValueError:
                return gettext('Invalid participant email'), 400

            update_values['participant_email'] = participant_email

        # Check if we have anything to update
        if not update_values:
            return gettext('No participant information to update'), 400

        # Do the update!
        try:
            TeraParticipant.update(participant.id_participant, update_values)

        except exc.IntegrityError as e:
            TeraParticipant.db().session.rollback()

            if self.module:
                self.module.logger.log_warning(
                    self.module.module_name,
                    ParticipantQueryParticipants.__name__,
                    'update', 400, 'Integrity error', str(e)
                )

            return gettext('Can\'t update participant: integrity error'), 400

        except exc.SQLAlchemyError as e:
            TeraParticipant.db().session.rollback()

            if self.module:
                self.module.logger.log_error(
                    self.module.module_name,
                    ParticipantQueryParticipants.__name__,
                    'post', 500, 'Database error', str(e)
                )

            return gettext('Database Error'), 500

        # Query updated participant information
        update_participant = TeraParticipant.get_participant_by_id(
            participant.id_participant
        )

        # Return participant information according to its access level
        if current_participant.fullAccess:
            update_participant_json = update_participant.to_json()
        else:
            update_participant_json = {
                'participant_name': update_participant.participant_name,
                'participant_email': update_participant.participant_email
            }

        return jsonify([update_participant_json])
