from flask.views import MethodView
from flask import render_template, request, session
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

        # Not specified or with no value will default to true
        with_websocket = request.args.get('with_websocket', '').lower() in ['true', '1', 'yes', 'on', '']

        # if 'auth_code' in session:
        #     session.pop('auth_code')
        if 'auth_code' in request.args:
            session['auth_code'] = request.args['auth_code']

        versions = TeraVersions()
        versions.load_from_db()

        return render_template('login.html', hostname=hostname, port=port,
                               server_version=versions.version_string, show_logo=show_logo, with_websocket=with_websocket)
