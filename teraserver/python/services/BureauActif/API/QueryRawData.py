import datetime
import uuid
import os

from flask import request
from flask_restx import Resource
from werkzeug.utils import secure_filename

from services.BureauActif import Globals
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_login_type, current_device_client, \
    LoginType

from services.BureauActif.FlaskModule import default_api_ns as api, flask_app
from services.BureauActif.libbureauactif.db.Base import db
from services.BureauActif.libbureauactif.db.models.BureauActifData import BureauActifData
from services.BureauActif.libbureauactif.db.DBManager import DBManager


# Parser definition(s)
post_parser = api.parser()


class QueryRawData(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @api.expect(post_parser)
    @api.doc(description='To be documented '
                         'To be documented',
             responses={200: 'Success',
                        400: 'Missing parameters',
                        403: 'Logged client doesn\'t have permission to access the requested data',
                        404: 'Session to attach data doesn\'t exists or is not available for the logged client',
                        500: 'No participant associated to that device'})
    @ServiceAccessManager.token_required
    def post(self):
        data_process = DBManager.dataProcess()

        # Only devices can upload data for now
        if current_login_type != LoginType.DEVICE_LOGIN:
            return 'Wrong login type', 403

        if request.content_type == 'application/octet-stream':
            if 'X-Id-Session' not in request.headers:
                return 'No ID Session specified', 400

            if 'X-Filename' not in request.headers:
                return 'No file specified', 400

            id_session = int(request.headers['X-Id-Session'])
            filename = secure_filename(request.headers['X-Filename'])
            creation_date = datetime.datetime.strptime(request.headers['X-Filedate'], '%Y-%m-%d %H:%M:%S')

            # Check if device is allowed to access the specified session
            # TODO - right now, this API was disabled for security reasons
            # if not current_device_client.can_access_session(id_session):
            #     return 'Session not available', 404

            # Get participants for that session
            device_info = current_device_client.get_device_infos()
            if 'participants_info' not in device_info or len(device_info['participants_info']) == 0:
                return 'No participant associated to that device', 500

            # Get device id
            if 'device_info' not in device_info and 'id_device' not in device_info['device_info']:
                return 'No valid device!', 500
            id_device = device_info['device_info']['id_device']

            # Loads data in JSON structure in memory for processing
            import json
            try:
                raw_data = json.loads(request.data.decode())
            except ValueError:
                return 'Unable to decode raw data', 400

            # Only considers the first participant in the list for now
            participant_uuid = device_info['participants_info'][0]['participant_uuid']

            # Create file entry in database
            file_db_entry = BureauActifData()
            file_db_entry.id_device = id_device
            file_db_entry.id_session = id_session
            file_db_entry.data_participant_uuid = participant_uuid
            file_db_entry.data_original_filename = filename
            file_db_entry.data_name = filename
            file_db_entry.data_saved_date = creation_date
            file_db_entry.data_uuid = str(uuid.uuid4())
            file_db_entry.data_filesize = len(request.data)
            db.session.add(file_db_entry)

            db.session.commit()

            # Save file on disk
            fo = open(os.path.join(flask_app.config['UPLOAD_FOLDER'], file_db_entry.data_uuid), "wb")
            fo.write(request.data)
            fo.close()

            # Send new asset to OpenTera
            json_asset = {'asset': {'id_asset': 0,  # Will create a new asset
                                    'id_session': id_session,
                                    'id_device': id_device,
                                    'asset_name': filename,
                                    'asset_type': 2  # Hard coded for now as RAW_DATA
                                    }}

            post_result = Globals.service.post_to_opentera(api_url='/api/service/assets', json_data=json_asset)
            if post_result.status_code != 200:
                print('Error sending asset to OpenTera: : Code=' + str(post_result.status_code) + ', Message=' +
                      post_result.content.decode())

            # Data is in raw_data and stored in the "t_data" table.
            # Format is a dict with:
            # data -> A list of list which each item is a row in the raw data file:
            #          Timestamp, current_height, button_pressed, present, raw_sensor_values
            # timers -> dict of values for "minutes_up" and "minutes_down", corresponding to the current Bureau config
            # config -> dict of values for the "max_height" and the "min_height" of the Bureau

            data_process.process_data(raw_data, file_db_entry)

            return '', 200

        return '', 400

