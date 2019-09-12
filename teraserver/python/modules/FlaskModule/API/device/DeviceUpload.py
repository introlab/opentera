from flask_restful import Resource, reqparse
from modules.LoginModule.LoginModule import LoginModule, current_device
from flask import request, redirect, flash
from werkzeug.utils import secure_filename
from modules.FlaskModule.FlaskModule import flask_app

from libtera.db.models.TeraDeviceData import TeraDeviceData
from libtera.db.DBManager import DBManager
from libtera.db.Base import db

import datetime
import uuid
import os


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


class DeviceUpload(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @LoginModule.token_or_certificate_required
    def get(self):
        print(request)
        print('current_device', current_device)
        return '', 200

    @LoginModule.token_or_certificate_required
    def post(self):
        print(request)
        print('current_device', current_device)

        if request.content_type == 'application/octet-stream':
            if 'X-Id-Session' not in request.headers:
                return 'No ID Session specified', 400

            if 'X-Filename' not in request.headers:
                return 'No file specified', 400

            id_session = int(request.headers['X-Id-Session'])
            filename = secure_filename(request.headers['X-Filename'])
            creation_date = datetime.datetime(request.headers['X-Filedate'])

            # Check if device is allowed to access the specified session
            device_access = DBManager.deviceAccess(current_device)
            file_session = device_access.query_session(session_id=id_session)
            if not file_session:
                return '', 403

            # Create file entry in database
            file_db_entry = TeraDeviceData()
            file_db_entry.devicedata_device = current_device
            # file_db_entry.devicedata_session = file_session
            file_db_entry.id_session = id_session
            file_db_entry.devicedata_original_filename = filename
            file_db_entry.devicedata_name = filename
            file_db_entry.devicedata_saved_date = creation_date
            file_db_entry.devicedata_uuid = str(uuid.uuid4())
            db.session.add(file_db_entry)
            db.session.commit()

            # Save file on disk
            fo = open(os.path.join(flask_app.config['UPLOAD_FOLDER'], file_db_entry.devicedata_uuid), "wb")
            fo.write(request.data)
            fo.close()
            return '', 200

        elif request.content_type.__contains__('multipart/form-data'):
            if 'id_session' not in request.form:
                return 'No ID Session specified', 400

            # check if the post request has the file part
            if 'file' not in request.files:
                return 'No file specified', 400

            file = request.files['file']
            id_session = int(request.form['id_session'])

            # Check if device is allowed to access the specified session
            device_access = DBManager.deviceAccess(current_device)
            file_session = device_access.query_session(session_id=id_session)
            if not file_session:
                return '', 403

            # if user does not select file, browser also
            # submit an empty part without filename
            if file.filename == '':
                return 'No filename specified', 400

            if file:
                filename = secure_filename(file.filename)

                # Create file entry in database
                file_db_entry = TeraDeviceData()
                file_db_entry.devicedata_device = current_device
                # file_db_entry.devicedata_session = file_session
                file_db_entry.id_session = id_session
                file_db_entry.devicedata_original_filename = filename
                file_db_entry.devicedata_saved_date = datetime.datetime.now()
                file_db_entry.devicedata_uuid = str(uuid.uuid4())
                db.session.add(file_db_entry)
                db.session.commit()

                # Save file on disk
                file.save(os.path.join(flask_app.config['UPLOAD_FOLDER'], file_db_entry.devicedata_uuid))
                return '', 200

        return '', 400
