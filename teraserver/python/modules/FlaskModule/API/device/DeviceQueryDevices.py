from flask import jsonify, session, request
from flask_restx import Resource, reqparse
from flask_babel import gettext
from sqlalchemy import exc

from modules.LoginModule.LoginModule import LoginModule
from modules.Globals import db_man
from modules.FlaskModule.FlaskModule import device_api_ns as api
from opentera.db.models.TeraDevice import TeraDevice

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('token', type=str, help='Secret Token')

post_parser = api.parser()


class DeviceQueryDevices(Resource):

    def __init__(self, _api, flaskModule=None):
        Resource.__init__(self, _api)
        self.module = flaskModule

    @LoginModule.device_token_or_certificate_required
    @api.expect(get_parser)
    @api.doc(description='Return device information.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'})
    def get(self):

        device = TeraDevice.get_device_by_uuid(session['_user_id'])
        args = get_parser.parse_args()

        # Reply device information
        response = {'device_info': device.to_json(minimal=True)}

        device_access = db_man.deviceAccess(device)

        # Reply participant information
        participants = device_access.get_accessible_participants()
        response['participants_info'] = list()

        for participant in participants:
            participant_info = {'participant_name': participant.participant_name,
                                'participant_uuid': participant.participant_uuid}
            response['participants_info'].append(participant_info)
            # response['participants_info'].append(participant.to_json(minimal=True))

        # Reply accessible sessions type ids
        session_types = device_access.get_accessible_session_types()
        response['session_types_info'] = list()

        for st in session_types:
            response['session_types_info'].append(st.to_json(minimal=True))

        # Return reply as json object
        return response

    @LoginModule.device_token_or_certificate_required
    @api.doc(description='Update a device. A device can only update its own data. For now, only device_config can be '
                         'updated with that API.',
             responses={200: 'Success',
                        403: 'Logged device can\'t update the specified device',
                        400: 'Badly formed JSON or missing fields(id_device) in the JSON body',
                        500: 'Internal error occured when saving device'})
    def post(self):
        current_device = TeraDevice.get_device_by_uuid(session['_user_id'])
        json_device = request.json['device']

        # Validate if we have an id
        if 'id_device' not in json_device:
            json_device['id_device'] = current_device.id_device  # No id - we put the current device id by default
        # Validate if we have a config
        if 'device_config' not in json_device:
            return gettext('Missing config'), 400

        # Validate the device is only updating its own info
        if json_device['id_device'] != current_device.id_device:
            return gettext('Forbidden'), 403

        # Filter everything except device_config
        unfiltered_keys = {'id_device', 'device_config'}
        json_device = {x: json_device[x] for x in json_device if x in unfiltered_keys}

        try:
            TeraDevice.update(json_device['id_device'], json_device)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return gettext('Database error'), 500

        update_device = TeraDevice.get_device_by_id(json_device['id_device'])

        return [update_device.to_json()]
