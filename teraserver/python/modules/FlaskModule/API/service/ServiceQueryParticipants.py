from flask import request
from flask_restx import Resource
from flask_babel import gettext
from sqlalchemy.exc import IntegrityError
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from modules.DatabaseModule.DBManager import DBManager
from opentera.db.models.TeraParticipant import TeraParticipant
import uuid
from datetime import datetime

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('participant_uuid', type=str, help='Participant uuid of the participant to query')
get_parser.add_argument('id_project', type=int, help='Project ID to query all participants for')
get_parser.add_argument('id_participant_group', type=int, help='Participant group to query all participants for')
get_parser.add_argument('name', type=str, help='Return participants with at least a partial match on their name.')

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
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return participant information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Service doesn\'t have permission to access the requested data'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        args = get_parser.parse_args()

        service_access = DBManager.serviceAccess(current_service)

        # args['participant_uuid'] Will be None if not specified in args
        if args['participant_uuid']:
            if args['participant_uuid'] not in service_access.get_accessible_participants_uuids():
                return gettext('Forbidden'), 403
            participant = TeraParticipant.get_participant_by_uuid(args['participant_uuid'])
            if participant:
                return participant.to_json()

        if args['id_project']:
            if args['id_project'] not in service_access.get_accessible_projects_ids():
                return gettext('Forbidden'), 403
            filters = {'id_project': args['id_project']}
            if not args['name']:
                participants = TeraParticipant.query_with_filters(filters)
            else:
                participants = TeraParticipant.search_participant_by_name(args['name'], filters)
            return [participant.to_json() for participant in participants]

        if args['id_participant_group']:
            if args['id_participant_group'] not in service_access.get_accessible_participants_groups_ids():
                return gettext('Forbidden'), 403
            filters = {'id_participant_group': args['id_participant_group']}
            if not args['name']:
                participants = TeraParticipant.query_with_filters(filters)
            else:
                participants = TeraParticipant.search_participant_by_name(args['name'], filters)
            return [participant.to_json() for participant in participants]

        if args['name']:
            # Search for participants with name in all availables
            participants = (TeraParticipant.query.filter(
                TeraParticipant.id_participant.in_(service_access.get_accessible_participants_ids()))
                            .filter(TeraParticipant.participant_name.like('%' + args['name'] + '%')).all())
            return [participant.to_json(minimal=True) for participant in participants]

        return gettext('Missing arguments'), 400

    @api.doc(description='Update participant',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'},
             params={'token': 'Secret token'})
    @api.expect(participant_schema)
    @LoginModule.service_token_or_certificate_required
    def post(self):
        args = post_parser.parse_args()

        # Using request.json instead of parser, since parser messes up the json!
        if 'participant' not in request.json:
            return gettext('Missing arguments'), 400

        participant_info = request.json['participant']

        # All fields validation
        if participant_info['id_project'] < 1:
            return gettext('Unknown project'), 403

        if not participant_info['participant_name']:
            return gettext('Invalid participant name'), 403

        if not participant_info['participant_email']:
            return gettext('Invalid participant email'), 403

        # Everything ok...
        participant: TeraParticipant = TeraParticipant()

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
            # Will generate token, last online
            try:
                TeraParticipant.insert(participant)
            except IntegrityError as e:
                self.module.logger.log_warning(self.module.module_name, ServiceQueryParticipants.__name__, 'insert',
                                               400, 'Integrity error', str(e))

                if 't_projects' in str(e.args):
                    return gettext('Can\'t insert participant: participant\'s project is disabled or invalid.'), 400
        else:
            # Update participant
            try:
                TeraParticipant.update(participant_info['id_participant'], participant_info)
            except IntegrityError as e:
                self.module.logger.log_warning(self.module.module_name, ServiceQueryParticipants.__name__, 'update',
                                               400, 'Integrity error', str(e))

                if 't_projects' in str(e.args):
                    return gettext('Can\'t update participant: participant\'s project is disabled.'), 400

            # Update info
            participant = TeraParticipant.get_participant_by_id(participant_info['id_participant'])

        # Return participant information
        return participant.to_json(minimal=False)
