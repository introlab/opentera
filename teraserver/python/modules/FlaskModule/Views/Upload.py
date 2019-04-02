"""
Copyright 2019 IntRoLab / ESTRAD, Université de Sherbrooke

Simon Brière, ing., M.Sc.A.
Dominic Létourneau, ing., M.Sc.A

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""


from flask.views import MethodView
from flask import render_template, request, redirect, flash
from modules.Globals import auth
from werkzeug.utils import secure_filename
from modules.FlaskModule.FlaskModule import flask_app
import os


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'dmg'])


class Upload(MethodView):
    # Decorators everywhere?
    decorators = [auth.login_required]

    def __init__(self, *args, **kwargs):
        print('Index.__init__', args, kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        print(self.flaskModule)

    # @auth.login_required
    def get(self):
        print('get')
        return render_template('upload.html')

    # @auth.login_required
    def post(self):
        print('post', request)

        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)

        file = request.files['file']

        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)

        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            # file.save(os.path.join(flask_app.config['UPLOAD_FOLDER'], filename))
            return 'TODO Server should save file: ' + str(file) + ' ' + filename + ' in folder: ' + flask_app.config['UPLOAD_FOLDER']

        return 'File type not allowed: ' + secure_filename(file.filename) + ' allowed extensions : ' \
               + str(ALLOWED_EXTENSIONS), 401

