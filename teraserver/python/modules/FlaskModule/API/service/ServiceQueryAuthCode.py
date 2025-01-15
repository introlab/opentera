import json
from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from modules.DatabaseModule.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('endpoint_url', type=str, help='Endpoint url requesting access', required=True)



class ServiceQueryAuthCode(Resource):

    # Handle auth
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @api.doc(description='Return auth code used for login / service auth.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Service doesn\'t have permission to access the requested data'},
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        args = get_parser.parse_args(strict=True)

        service_access = DBManager.serviceAccess(current_service)

        endpoint_url = args['endpoint_url']

        # TODO Check if endpoint is allowed ?

        # Generate auth code
        auth_code = service_access.generate_auth_code(endpoint_url)

        # Add auth code to redis
        if not self.module:
            return gettext('Internal error'), 500

        auth_code_data = {'service_uuid': current_service.service_uuid, 'endpoint_url': endpoint_url}

        self.module.redisSet('service_auth_code_' + auth_code, json.dumps(auth_code_data), 300)

        return {'auth_code': auth_code}, 200
