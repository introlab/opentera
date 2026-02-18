from flask.views import MethodView
from flask import render_template, request, session
from modules.FlaskModule.FlaskModule import get_locale
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

        theme_file = 'login_style'
        if 'theme' in request.args:
            if request.args['theme'] == 'light':
                theme_file = 'login_style_light'
        session['theme'] = theme_file

        if 'lang' in request.args:  # Force a specific language
            session['lang'] = request.args['lang']
        else:
            session['lang'] = get_locale()

        versions = TeraVersions()
        versions.load_from_db()

        return render_template('login.html', hostname=hostname, port=port,
                               server_version=versions.version_string, show_logo=show_logo, theme_file=session['theme'],
                               with_websocket=with_websocket, current_locale=session['lang'])
