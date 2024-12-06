from flask_restx import Resource
from flask_babel import gettext

from opentera.db.models import TeraUser
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from modules.DatabaseModule.DBManager import DBManager
from modules.DatabaseModule.DBManagerTeraServiceAccess import DBManagerTeraServiceAccess

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user', type=int, help='User id of the user to query', default=None)
get_parser.add_argument('user_uuid', type=str, help='User uuid of the user to query', default=None)


class ServiceQueryUsers(Resource):

    # Handle auth
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return user information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Service doesn\'t have permission to access the requested data'},
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        """
        Get specific user information
        """
        args = get_parser.parse_args(strict=True)
        service_access : DBManagerTeraServiceAccess = DBManager.serviceAccess(current_service)

        # args['user_id'] Will be None if not specified in args
        if args['user_uuid']:
            if args['user_uuid'] not in service_access.get_accessible_users_uuids():
                return gettext('Service doesn\'t have permission to access the requested data'), 403
            user = TeraUser.get_user_by_uuid(args['user_uuid'])
            if user:
                return user.to_json()

        # args['id_user'] Will be None if not specified in args
        if args['id_user']:
            if args['id_user'] not in service_access.get_accessible_users_ids():
                return gettext('Service doesn\'t have permission to access the requested data'), 403
            user = TeraUser.get_user_by_id(args['id_user'])
            if user:
                return user.to_json()

        return gettext('Missing arguments'), 400
