from flask import jsonify, session, request
from flask_restx import Resource, reqparse
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule
from modules.Globals import db_man
from modules.FlaskModule.FlaskModule import device_api_ns as api
from opentera.db.models.TeraDevice import TeraDevice

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('token', type=str, help='Secret Token')
post_parser = api.parser()


class DeviceQueryParticipants(Resource):
    def __init__(self, _api, flaskModule=None):
        Resource.__init__(self, _api)
        self.module = flaskModule

    @LoginModule.device_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return participant information, if allowed.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'})
    def get(self):

        device = TeraDevice.get_device_by_uuid(session['_user_id'])
        args = get_parser.parse_args()

        # Device must have device_onlineable flag
        if device and device.device_onlineable:
            response = {'participants_info': []}

            # Get all participants
            for participant in device.device_participants:
                response['participants_info'].append(participant.to_json(minimal=False))

            return response

        return gettext('Invalid request'), 403
