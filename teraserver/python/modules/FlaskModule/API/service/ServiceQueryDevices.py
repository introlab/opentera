from flask import request
from flask_restx import Resource, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule, current_service
from modules.FlaskModule.FlaskModule import service_api_ns as api
from modules.DatabaseModule.DBManager import DBManager
from modules.DatabaseModule.DBManagerTeraServiceAccess import DBManagerTeraServiceAccess
from opentera.db.models.TeraDevice import TeraDevice

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('device_uuid', type=str, help='Device uuid of the device to query', default=None)
get_parser.add_argument('id_device', type=int, help='Device ID to query', default=None)
get_parser.add_argument('with_device_type', type=inputs.boolean, help='Give more information about type',
                        default=False)
get_parser.add_argument('with_device_subtype', type=inputs.boolean, help='Give more information about subtype',
                        default=False)
get_parser.add_argument('with_device_assets', type=inputs.boolean, help='Give more information about assets',
                        default=False)


post_parser = api.parser()

device_schema = api.schema_model('service_device',
                                 {'properties': TeraDevice.get_json_schema(), 'type': 'object', 'location': 'json'})


class ServiceQueryDevices(Resource):

    # Handle auth
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Return device information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Service doesn\'t have permission to access the requested data'},
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        """
        Query device information
        """
        args = get_parser.parse_args()
        service_access : DBManagerTeraServiceAccess = DBManager.serviceAccess(current_service)

        # args['device_uuid'] Will be None if not specified in args
        if args['device_uuid'] or args['id_device']:

            if args['device_uuid']:
                device: TeraDevice = TeraDevice.get_device_by_uuid(args['device_uuid'])
            else:
                device: TeraDevice = TeraDevice.get_device_by_id(args['id_device'])

            if device:
                if device.id_device not in service_access.get_accessible_devices_ids():
                    return gettext('Forbidden'), 403

                device_json = device.to_json()

                if args['with_device_type']:
                    if device.device_type:
                        device_json['device_type'] = device.device_type.to_json(minimal=True)

                if args['with_device_subtype']:
                    # Device_subtype can be null
                    if device.device_subtype:
                        device_json['device_subtype'] = device.device_subtype.to_json(minimal=True)
                    else:
                        device_json['device_subtype'] = None

                if args['with_device_assets']:
                    device_json['device_assets'] = []
                    for asset in device.device_assets:
                        device_json['device_assets'].append(asset.to_json(minimal=True))

                return device_json

        return gettext('Missing arguments'), 400

    @api.doc(description='Update device information ',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Service doesn\'t have permission to access the requested data'},
             params={'token': 'Access token'})
    @api.expect(device_schema, validate=True)
    @LoginModule.service_token_or_certificate_required
    def post(self):
        """
        Create / update device
        """
        # args = post_parser.parse_args()
        # Using request.json instead of parser, since parser messes up the json!
        if 'device' not in request.json:
            return gettext('Missing arguments'), 400

        device_info = request.json['device']

        # All fields validation
        if device_info['id_device_type'] < 1:
            return gettext('Unknown device type'), 403

        # id_device_subtype = 0 means no subtype
        if device_info['id_device_subtype'] < 0:
            return gettext('Unknown device subtype'), 403

        # Everything ok...
        device: TeraDevice = TeraDevice()

        # Create a new device?
        if device_info['id_device'] == 0:
            # Create device
            device.device_name = device_info['device_name']
            device.id_device_type = device_info['id_device_type']
            device.id_device_subtype = device_info['id_device_subtype']

            # By default enabled & onlineable ?
            device.device_enabled = True
            device.device_onlineable = True

            # Will generate token, last online
            TeraDevice.insert(device)
        else:
            if device_info['id_device'] not in DBManager.serviceAccess(current_service).get_accessible_devices_ids():
                return gettext('Forbidden'), 403

            # Update device
            TeraDevice.update(device_info['id_device'], device_info)
            # Update info
            device = TeraDevice.get_device_by_id(device_info['id_device'])

        # Return device information
        return device.to_json(minimal=False)
