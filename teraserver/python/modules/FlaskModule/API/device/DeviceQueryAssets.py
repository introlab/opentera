from flask import session, request
from flask_restx import Resource
from modules.LoginModule.LoginModule import LoginModule
from modules.Globals import db_man
from modules.FlaskModule.FlaskModule import device_api_ns as api
from opentera.db.models.TeraDevice import TeraDevice

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('asset_uuid', type=str, help='Asset UUID to query', default=None)
get_parser.add_argument('id_asset', type=int, help='Asset ID to query', default=None)

post_parser = api.parser()


class DeviceQueryAssets(Resource):

    def __init__(self, _api, flaskModule = None):
        Resource.__init__(self, _api)
        self.module = flaskModule

    @LoginModule.device_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Get device assets based on the ID or, if no parameters, get all assets',
             responses={200: 'Success',
                        403: 'Device doesn\'t have access to the specified asset'})
    def get(self):

        device = TeraDevice.get_device_by_uuid(session['_user_id'])
        args = get_parser.parse_args()

        device_access = db_man.deviceAccess(device)
        assets = device_access.get_accessible_assets(id_asset=args['id_asset'], uuid_asset=args['asset_uuid'])

        # Create response
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']
        if 'X_EXTERNALSERVER' in request.headers:
            servername = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        services_infos = [{service.service_uuid: service.service_clientendpoint}
                          for service in device_access.get_accessible_services()]
        assets_json = []
        for asset in assets:
            asset_json = asset.to_json()

            # We have previously verified that the service is available to the user
            if asset.asset_uuid in services_infos:
                asset_json['asset_infos_url'] = 'https://' + servername + ':' + str(port) \
                                                + services_infos[asset.asset_service_uuid] \
                                                + 'api/assets/infos?asset_uuid=' + asset.asset_uuid
                asset_json['asset_url'] = 'https://' + servername + ':' + str(port) \
                                          + services_infos[asset.asset_service_uuid] \
                                          + 'api/assets?asset_uuid=' + asset.asset_uuid
            else:
                # Service not found or unavaiable for current user
                asset_json['asset_infos_url'] = None
                asset_json['asset_url'] = None

            assets_json.append(asset_json)

        return assets_json

