from flask_restx import Resource
from flask_babel import gettext

from opentera.db.models import TeraUser
from modules.LoginModule.LoginModule import LoginModule
from modules.FlaskModule.FlaskModule import service_api_ns as api

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('user_uuid', type=str, help='User uuid of the user to query')

post_parser = api.parser()


class ServiceQueryUsers(Resource):

    # Handle auth
    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @LoginModule.service_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return user information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):

        args = get_parser.parse_args()

        # args['user_id'] Will be None if not specified in args
        if args['user_uuid']:
            user = TeraUser.get_user_by_uuid(args['user_uuid'])
            if user:
                return user.to_json()

        return gettext('Missing arguments'), 400
