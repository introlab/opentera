from flask.views import MethodView
from flask import render_template, request
from opentera.utils.TeraVersions import TeraVersions


class LoginView(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    def get(self):
        hostname = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']

        if 'X_EXTERNALSERVER' in request.headers:
            hostname = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        show_logo = 'no_logo' not in request.args

        endpoint_url = ""
        if 'endpoint' in request.args:
            endpoint_url = request.args['endpoint']

        versions = TeraVersions()
        versions.load_from_db()

        return render_template('login.html', hostname=hostname, port=port,
                               server_version=versions.version_string, show_logo=show_logo, endpoint_url=endpoint_url)
