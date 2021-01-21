from flask import request
from flask_restx import Resource

from opentera.services.ServiceAccessManager import ServiceAccessManager, current_login_type, LoginType

from services.BureauActif.FlaskModule import default_api_ns as api

from services.BureauActif.libbureauactif.db.models.BureauActifDeviceInfos import BureauActifDeviceInfo

from sqlalchemy import exc

get_parser = api.parser()
get_parser.add_argument('device_uuid', type=str, help='Device uuid of the device to query')
get_parser.add_argument('uuid', type=str, help='Alias for "device_uuid"')

# post_parser = reqparse.RequestParser()
post_schema = api.schema_model('device_info', {'properties': BureauActifDeviceInfo.get_json_schema(),
                                               'type': 'object',
                                               'location': 'json'})


class QueryDeviceInfos(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @api.doc(description='Gets current device informations',
             responses={200: 'Success',
                        400: 'Missing parameter',
                        403: 'Forbidden - only logged user can get that information'})
    @api.expect(get_parser)
    @ServiceAccessManager.token_required
    def get(self):

        if current_login_type != LoginType.USER_LOGIN:
            return '', 403

        parser = get_parser

        args = parser.parse_args()

        if args['uuid']:
            args['device_uuid'] = args['uuid']

        if not args['device_uuid']:
            return 'Missing device UUID', 400

        # TODO: Check if requester can access that device or not.

        # Query informations from database
        infos = BureauActifDeviceInfo.get_infos_for_device(device_uuid=args['device_uuid'])

        if infos:
            return infos.to_json()

        return None

    @api.expect(post_schema)
    @api.doc(description='Update devices information',
             responses={200: 'Success',
                        400: 'Missing parameters',
                        403: 'Logged client doesn\'t have permission to access the requested data'
                        })
    @ServiceAccessManager.token_required
    def post(self):

        # Only device can update for now
        if current_login_type != LoginType.DEVICE_LOGIN:
            return '', 403

        if 'device_info' not in request.json:
            return 'Missing device infos', 400

        json_infos = request.json['device_info']

        # TODO: Check if that device can update that device

        # Check if we already have infos for that participant
        if 'device_info_device_uuid' not in json_infos:
            return 'Missing device uuid', 400

        infos = BureauActifDeviceInfo.get_infos_for_device(
            device_uuid=json_infos['device_info_device_uuid'])

        if infos:
            # Update query
            try:
                BureauActifDeviceInfo.update(infos.id_device_info, json_infos)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                return e.args, 500

        else:
            # New query
            try:
                infos = BureauActifDeviceInfo()
                infos.from_json(json_infos)
                BureauActifDeviceInfo.insert(infos)
            except exc.SQLAlchemyError as e:
                import sys
                print(sys.exc_info())
                return e.args, 500

        return infos.to_json()





