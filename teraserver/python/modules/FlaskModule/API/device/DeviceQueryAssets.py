from flask import jsonify, session, request
from flask_restx import Resource, reqparse
from modules.LoginModule.LoginModule import LoginModule
from flask_babel import gettext
from modules.Globals import db_man
from modules.FlaskModule.FlaskModule import device_api_ns as api
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraAsset import TeraAsset

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('token', type=str, help='Secret Token')
get_parser.add_argument('id_asset', type=int, help='Asset it to query', default=None)
post_parser = api.parser()


class DeviceQueryAssets(Resource):

    def __init__(self, _api, flaskModule=None):
        Resource.__init__(self, _api)
        self.module = flaskModule

    @LoginModule.device_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Get device assets',
             responses={403: 'Forbidden for devices for security reasons.'})
    def get(self):

        # device = TeraDevice.get_device_by_uuid(session['_user_id'])
        # args = get_parser.parse_args()
        #
        # device_access = db_man.deviceAccess(device)
        #
        # # TODO id_asset args
        # assets = device_access.get_accessible_assets(id_asset=args['id_asset'])
        #
        # # Create response
        # response = {'device_assets': []}
        #
        # # Serialize to json
        # for asset in assets:
        #     response['device_assets'].append(asset.to_json(minimal=True))
        #
        # return response
        return '', 403

    @LoginModule.device_token_or_certificate_required
    @api.expect(post_parser)
    @api.doc(description='Login device with Token.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'})
    def post(self):
        return '', 501
