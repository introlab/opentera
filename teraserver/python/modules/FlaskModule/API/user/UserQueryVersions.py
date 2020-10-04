from flask import session, request
from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraServerSettings import TeraServerSettings
import json
from libtera.db.models.TeraUser import TeraUser

# Parser definition(s)
# GET
get_parser = api.parser()

# POST
post_parser = api.parser()


class UserQueryVersions(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get server versions',
             responses={200: 'Success - returns list of assets',
                        400: 'Required parameter is missing',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        # As soon as we are authorized, we can output the server versions
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        args = get_parser.parse_args()

        current_settings = json.loads(TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerVersions))
        return current_settings

    @user_multi_auth.login_required
    @api.doc(description='Post server versions',
             responses={200: 'Success - asset posted',
                        500: 'Database error occurred',
                        403: 'Logged user doesn\'t have permission to delete the requested asset (must be an user of'
                             'the related project)'})
    @api.expect(post_parser)
    def post(self):

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        args = post_parser.parse_args()

        # Only superuser can change the versions settings
        # Only some fields can be changed.
        if current_user.user_superadmin:
            current_settings = json.loads(
                TeraServerSettings.get_server_setting_value(TeraServerSettings.ServerVersions))
            return current_settings

        # Not superadmin
        return gettext('Not authorized'), 403
