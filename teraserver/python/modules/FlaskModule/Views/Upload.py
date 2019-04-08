
from flask.views import MethodView
from flask import render_template, request, redirect, flash
from modules.Globals import auth
from werkzeug.utils import secure_filename
from modules.FlaskModule.FlaskModule import flask_app
import os


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


ALLOWED_EXTENSIONS = set(['txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif', 'dat'])


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
            return 'TODO Server should save file: ' + str(file) + ' ' + filename + ' in folder: ' \
                   + flask_app.config['UPLOAD_FOLDER']

        return 'File type not allowed: ' + secure_filename(file.filename) + ' allowed extensions : ' \
               + str(ALLOWED_EXTENSIONS), 401

