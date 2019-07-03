from flask_restful import Resource, reqparse
from modules.LoginModule.LoginModule import LoginModule, current_device
from flask import request, redirect, flash
from werkzeug.utils import secure_filename
from modules.FlaskModule.FlaskModule import flask_app
import os


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# TODO MAKE THIS CONFIGURABLE?
ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'dat'])


class DeviceUpload(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @LoginModule.certificate_required
    def get(self):
        print(request)
        print('current_device', current_device)
        return '', 200

    @LoginModule.certificate_required
    def post(self):
        print(request)
        print('current_device', current_device)

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return '', 400

        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return '', 400

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file.save(os.path.join(flask_app.config['UPLOAD_FOLDER'], filename))
            return 'TODO Server should save file: ' + str(file) + ' ' + filename + ' in folder: ' \
                   + flask_app.config['UPLOAD_FOLDER']

        return 'File type not allowed: ' + secure_filename(file.filename) + ' allowed extensions : ' \
               + str(ALLOWED_EXTENSIONS), 401
