from flask import jsonify, session, request
from flask_restx import Resource

from services.shared.ServiceAccessManager import ServiceAccessManager, current_login_type, LoginType

from services.BureauActif.Globals import config_man
from services.BureauActif.FlaskModule import default_api_ns as api

from services.BureauActif.libbureauactif.db.models.BureauActifParticipantInfos import BureauActifParticipantInfo

from sqlalchemy import exc

get_parser = api.parser()
get_parser.add_argument('participant_uuid', type=str, help='Participant uuid of the participant to query')
get_parser.add_argument('uuid', type=str, help='Alias for "participant_uuid"')

# post_parser = reqparse.RequestParser()
post_schema = api.schema_model('participant_info', {'properties': BureauActifParticipantInfo.get_json_schema(),
                                                    'type': 'object',
                                                    'location': 'json'})


class QueryParticipantInfos(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @api.doc(description='Gets current participant informations',
             responses={200: 'Success',
                        400: 'Missing parameter',
                        403: 'Forbidden - only logged user can get that information'})
    @api.expect(get_parser)
    @ServiceAccessManager.token_required
    def get(self):

        if current_login_type != LoginType.USER_LOGIN:
            return '', 403

        parser = get_parser

        args = parser.parse_args()

        if args['uuid']:
            args['participant_uuid'] = args['uuid']

        if not args['participant_uuid']:
            return 'Missing participant UUID', 400

        # TODO: Check if requester can access that participant or not.

        # Query informations from database
        infos = BureauActifParticipantInfo.get_infos_for_participant(part_uuid=args['participant_uuid'])

        if infos:
            return infos.to_json()

        return None

    @api.expect(post_schema)
    @api.doc(description='Update participants information',
             responses={200: 'Success',
                        400: 'Missing parameters',
                        403: 'Logged client doesn\'t have permission to access the requested data'
                        })
    @ServiceAccessManager.token_required
    def post(self):

        # Only device can update for now
        if current_login_type != LoginType.DEVICE_LOGIN:
            return '', 403

        if 'participant_info' not in request.json:
            return 'Missing participant infos', 400

        json_infos = request.json['participant_info']

        # TODO: Check if that device can update that participant

        # Check if we already have infos for that participant
        if 'participant_info_participant_uuid' not in json_infos:
            return 'Missing participant uuid', 400

        infos = BureauActifParticipantInfo.get_infos_for_participant(
            part_uuid=json_infos['participant_info_participant_uuid'])

        if infos:
            # Update query
            try:
                BureauActifParticipantInfo.update(infos.id_participant_info, json_infos)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                return e.args, 500

        else:
            # New query
            try:
                infos = BureauActifParticipantInfo()
                infos.from_json(json_infos)
                BureauActifParticipantInfo.insert(infos)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                return e.args, 500

        return infos.to_json()





