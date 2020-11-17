from flask.views import MethodView
from flask import send_from_directory
from services.BureauActif.FlaskModule import flask_app
from flask import render_template, request
from werkzeug.exceptions import NotFound


class Index(MethodView):
    # Decorators everywhere?
    # decorators = [auth.login_required]

    def __init__(self, *args, **kwargs):
        print('Index.__init__', args, kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        print(self.flaskModule)

    def get(self):
        try:
            return flask_app.send_static_file('default_index.html')
        except NotFound:
            # If the file was not found, send the default index file
            return flask_app.send_static_file('default_index.html')
