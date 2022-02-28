from flask import request
from flask_restx import Resource, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import LoginModule
from modules.FlaskModule.FlaskModule import service_api_ns as api
from opentera.db.models.TeraDevice import TeraDevice
from opentera.db.models.TeraDeviceType import TeraDeviceType
from opentera.db.models.TeraDeviceSubType import TeraDeviceSubType
from modules.DatabaseModule.DBManager import db
import uuid
from datetime import datetime

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('device_uuid', type=str, help='Device uuid of the device to query')
get_parser.add_argument('with_device_type', type=inputs.boolean, help='Give more information about type',
                        default=False)
get_parser.add_argument('with_device_subtype', type=inputs.boolean, help='Give more information about subtype',
                        default=False)
get_parser.add_argument('with_device_assets', type=inputs.boolean, help='Give more information about assets',
                        default=False)
# Unused for now
# post_parser = api.parser()

device_schema = api.schema_model('device', {
    'properties': {
        'device': {
            'type': 'object',
            'properties': {
                'id_device': {
                    'type': 'integer'
                },
                'id_device_type': {
                    'type': 'integer'
                },
                'id_device_subtype': {
                    'type': 'integer'
                },
                'device_name': {
                    'type': 'string'
                },
            },
            'required': ['id_device', 'device_name', 'id_device_type', 'id_device_subtype']
        },

    },
    'type': 'object',
    'required': ['device']
})


class ServiceQueryDevices(Resource):

    # Handle auth
    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)

    @LoginModule.service_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return device information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        args = get_parser.parse_args()
        # args['device_uuid'] Will be None if not specified in args
        if args['device_uuid']:
            device: TeraDevice = TeraDevice.get_device_by_uuid(args['device_uuid'])

            if device:
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

    @LoginModule.service_token_or_certificate_required
    @api.expect(device_schema, validate=True)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success - To be documented',
                        500: 'Required parameter is missing',
                        501: 'Not implemented.',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def post(self):
        # args = post_parser.parse_args()

        # Using request.json instead of parser, since parser messes up the json!
        if 'device' not in request.json:
            return gettext('Missing arguments'), 400

        device_info = request.json['device']

        # All fields validation
        if device_info['id_device_type'] < 1:
            return gettext('Unknown device type'), 403

        if device_info['id_device_subtype'] < 1:
            return gettext('Unknown device subtype'), 403

        # Everything ok...
        # Create a new device?
        if device_info['id_device'] == 0:
            # Create device
            device: TeraDevice = TeraDevice()
            device.device_name = device_info['device_name']
            device.device_uuid = str(uuid.uuid4())
            device.id_device_type = device_info['id_device_type']
            device.id_device_subtype = device_info['id_device_subtype']

            # By default enabled & onlineable ?
            device.device_enabled = True
            device.device_onlineable = True
            device.device_lastonline = datetime.now()

            # Generate token
            device.create_token()
            db.session.add(device)
            db.session.commit()
        else:
            # Update device
            device: TeraDevice = TeraDevice.get_device_bt_id(device_info['id_device'])
            device.device_name = device_info['device_name']
            device.id_device_type = device_info['id_device_type']
            device.id_device_subtype = device_info['id_device_subtype']

            device.device_enabled = True
            device.device_onlineable = True
            device.device_lastonline = datetime.now()
            # Re-Generate token
            device.create_token()
            db.session.add(device)
            db.session.commit()

        # Return device information
        return device.to_json(minimal=False)
