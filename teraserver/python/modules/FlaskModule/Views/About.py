from flask.views import MethodView
from flask import render_template, request
from modules.LoginModule.LoginModule import user_multi_auth
from opentera.utils.TeraVersions import TeraVersions


class About(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    # Anybody can view this?
    # @user_multi_auth.login_required
    def get(self):
        hostname = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']

        if 'X_EXTERNALSERVER' in request.headers:
            hostname = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        versions = TeraVersions()
        versions.load_from_db()

        return render_template('about.html', hostname=hostname, port=port,
                               server_version=versions.version_string,
                               openteraplus_version=versions.get_client_version_with_name('OpenTeraPlus'))

    # def post(self):
    #     return request.json
