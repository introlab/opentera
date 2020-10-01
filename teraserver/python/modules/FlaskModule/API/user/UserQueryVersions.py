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
        return gettext('Not authorized'), 403

    @user_multi_auth.login_required
    @api.doc(description='Post server versions',
             responses={200: 'Success - asset posted',
                        500: 'Database error occurred',
                        403: 'Logged user doesn\'t have permission to delete the requested asset (must be an user of'
                             'the related project)'})
    @api.expect(post_parser)
    def post(self):
        # TODO What to do here exactly?
        return gettext('Not authorized'), 403
