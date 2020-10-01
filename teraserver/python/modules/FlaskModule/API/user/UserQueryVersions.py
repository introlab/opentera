from flask import session, request
from flask_restx import Resource
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraServerSettings import TeraServerSettings
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraAsset import TeraAsset, AssetType
from libtera.db.models.TeraService import TeraService
from werkzeug.utils import secure_filename

from sqlalchemy import exc
from modules.DatabaseModule.DBManager import DBManager
from modules.RedisVars import RedisVars

import uuid

# Parser definition(s)
# GET
get_parser = api.parser()
# get_parser.add_argument('id_asset', type=int, help='Specific ID of asset to query information.')
# get_parser.add_argument('id_device', type=int, help='ID of the device from which to request all assets')
# get_parser.add_argument('id_session', type=int, help='ID of session from which to request all assets')
# get_parser.add_argument('id_participant', type=int, help='ID of participant from which to request all assets')
# get_parser.add_argument('service_uuid', type=str, help='Service UUID from which to request all assets')
# get_parser.add_argument('all', type=str, help='return all assets accessible from user')

# POST
post_parser = api.parser()
# post_parser.add_argument('id_session', type=int, help='ID of session to add the assets')


class UserQueryVersions(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get asset information. Only one of the ID parameter is supported at once',
             responses={200: 'Success - returns list of assets',
                        400: 'Required parameter is missing',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        return gettext('Not authorized'), 403

    @user_multi_auth.login_required
    @api.doc(description='Post asset.',
             responses={200: 'Success - asset posted',
                        500: 'Database error occurred',
                        403: 'Logged user doesn\'t have permission to delete the requested asset (must be an user of'
                             'the related project)'})
    @api.expect(post_parser)
    def post(self):
        # TODO What to do here exactly?
        return gettext('Not authorized'), 403
