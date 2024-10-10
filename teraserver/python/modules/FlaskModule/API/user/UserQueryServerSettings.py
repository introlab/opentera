from flask_restx import Resource, inputs
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraServerSettings import TeraServerSettings

# Parser definition(s)
# GET
get_parser = api.parser()
get_parser.add_argument('uuid', type=inputs.boolean, help='Get server UUID')
get_parser.add_argument('device_register_key', type=inputs.boolean, help='Get device registration key')


class UserQueryServerSettings(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get server setting key',
             responses={200: 'Success - returns setting value',
                        401: 'Logged user doesn\'t have permission to access the requested data'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        """
        Get server settings
        """
        # As soon as we are authorized, we can output the server versions
        args = get_parser.parse_args()

        settings = {}
        if args['uuid']:
            settings |= {'server_uuid': TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerUUID)}

        if args['device_register_key']:
            settings |= {'device_register_key':
                         TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerDeviceRegisterKey)}

        return settings
