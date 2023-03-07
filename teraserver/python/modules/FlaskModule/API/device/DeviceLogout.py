from flask import jsonify, session
from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_device
from modules.FlaskModule.FlaskModule import device_api_ns as api
from flask_login import logout_user

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('token', type=str, help='Secret Token')


class DeviceLogout(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Device logout.',
             responses={200: 'Success',
                        403: 'Device isn\'t logged in'})
    @api.expect(get_parser)
    @LoginModule.device_token_or_certificate_required
    def get(self):
        if current_device:
            logout_user()
            session.clear()
            self.module.send_device_disconnect_module_message(current_device.device_uuid)
            return gettext("Device logged out."), 200
        else:
            return gettext("Device not logged in"), 403

