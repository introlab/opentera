from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_device
from modules.FlaskModule.FlaskModule import device_api_ns as api

# Parser definition(s)
get_parser = api.parser()


class DeviceQueryParticipants(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return participant information, if allowed.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'},
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @LoginModule.device_token_or_certificate_required
    def get(self):
        """
        Get device associated participants information
        """
        # args = get_parser.parse_args()

        # Device must have device_onlineable flag
        if current_device and current_device.device_onlineable:
            response = {'participants_info': []}

            # Get all participants
            for participant in current_device.device_participants:
                response['participants_info'].append(participant.to_json(minimal=False))

            return response

        return gettext('Invalid request'), 403
