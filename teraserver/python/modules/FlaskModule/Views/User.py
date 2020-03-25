from flask.views import MethodView
from flask import render_template, request
from modules.LoginModule.LoginModule import user_multi_auth


class User(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    def get(self):
        hostname = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']

        if 'X_EXTERNALHOST' in request.headers:
            if ':' in request.headers['X_EXTERNALHOST']:
                hostname, port = request.headers['X_EXTERNALHOST'].split(':', 1)
            else:
                hostname = request.headers['X_EXTERNALHOST']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        return render_template('user.html', hostname=hostname, port=port)


