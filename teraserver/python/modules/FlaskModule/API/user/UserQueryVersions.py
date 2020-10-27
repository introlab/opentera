from flask import session, request
from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraServerSettings import TeraServerSettings
from libtera.utils.TeraVersions import TeraVersions, ClientVersions
import json
from libtera.db.models.TeraUser import TeraUser

# Parser definition(s)
# GET
get_parser = api.parser()

# POST
post_schema = api.schema_model('ClientVersions',
                               {'properties': ClientVersions.get_json_schema(), 'type': 'object', 'location': 'json'})


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
    @api.expect(post_schema)
    @api.doc(description='Post server versions',
             responses={200: 'Success - asset posted',
                        500: 'Database error occurred',
                        403: 'Logged user doesn\'t have permission to delete the requested asset (must be an user of'
                             'the related project)'})
    def post(self):

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])

        # Only superuser can change the versions settings
        # Only some fields can be changed.
        if current_user.user_superadmin:
            versions = TeraVersions()
            versions.load_from_db()

            if 'ClientVersions' in request.json:
                try:
                    client_version = ClientVersions()
                    client_version.from_dict(request.json['ClientVersions'])

                    # Update / add versions for the client
                    versions.set_client_version_with_name(client_version.client_name, client_version)

                    # Save to db
                    versions.save_to_db()

                except BaseException as e:
                    return gettext('Wrong ClientVersions') + str(e), 404

            # Return global config
            return versions.to_dict()

        # Not superadmin
        return gettext('Not authorized'), 403
