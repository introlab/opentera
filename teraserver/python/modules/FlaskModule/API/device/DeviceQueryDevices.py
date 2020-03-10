from flask import jsonify, session, request
from flask_restplus import Resource, reqparse
from modules.LoginModule.LoginModule import LoginModule
from modules.Globals import db_man
from modules.FlaskModule.FlaskModule import device_api_ns as api
from libtera.db.models.TeraDevice import TeraDevice

# Parser definition(s)
get_parser = api.parser()


get_parser.add_argument('token', type=str, help='Secret Token')

post_parser = api.parser()


class DeviceQueryDevices(Resource):

    def __init__(self, _api, flaskModule=None):
        Resource.__init__(self, _api)
        self.module = flaskModule

    @LoginModule.token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return device information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'})
    def get(self):

        device = TeraDevice.get_device_by_uuid(session['_user_id'])
        args = get_parser.parse_args()

        # Reply device information
        response = {'device_info': device.to_json(minimal=True)}

        device_access = db_man.deviceAccess(device)

        # Reply participant information
        participants = device_access.get_accessible_participants()
        response['participants_info'] = list()

        for participant in participants:
            response['participants_info'].append(participant.to_json(minimal=True))

        # Reply accessible sessions type ids
        session_types = device_access.get_accessible_session_types()
        response['session_types_info'] = list()

        for st in session_types:
            response['session_types_info'].append(st.to_json(minimal=True))

        # Return reply as json object
        return response
