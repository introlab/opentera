from flask_restx import Resource, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule
from modules.FlaskModule.FlaskModule import service_api_ns as api
from opentera.db.models.TeraService import TeraService
from sqlalchemy.exc import InvalidRequestError
from flask import request

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_service', type=int, help='ID of the service to query')
get_parser.add_argument('uuid_service', type=str, help='UUID of the service to query')
get_parser.add_argument('service_key', type=str, help='Key of the service to query')
get_parser.add_argument('with_base_url', type=inputs.boolean, help='Also include base external URL for that service')


class ServiceQueryServices(Resource):

    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @LoginModule.service_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return services information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        parser = get_parser
        args = parser.parse_args()

        services = []
        # Can only query service with a key, id or uuid
        if not args['service_key'] and not args['id_service'] and not args['uuid_service']:
            return gettext('Missing service key, id or uuid', 400)

        if args['id_service']:
            services = [TeraService.get_service_by_id(args['id_service'])]
        if args['uuid_service']:
            services = [TeraService.get_service_by_uuid(args['uuid_service'])]
        if args['service_key']:
            services = [TeraService.get_service_by_key(args['service_key'])]

        try:
            services_list = []
            for service in services:
                service_json = service.to_json(minimal=True)
                if args['with_base_url']:
                    # Build urls
                    hostname = service.service_hostname
                    port = service.service_port
                    if hostname == 'localhost' or hostname == '127.0.0.1':
                        # We have a service hosted on localhost - set server URL
                        hostname = self.module.config.server_config['hostname']
                        port = self.module.config.server_config['port']

                        if 'X_EXTERNALSERVER' in request.headers:
                            hostname = request.headers['X_EXTERNALSERVER']

                        if 'X_EXTERNALPORT' in request.headers:
                            port = request.headers['X_EXTERNALPORT']

                    base_url = 'https://' + hostname + ':' + str(port) + service.service_clientendpoint
                    service_json['service_base_url'] = base_url
                services_list.append(service_json)

            return services_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQueryServices.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500
