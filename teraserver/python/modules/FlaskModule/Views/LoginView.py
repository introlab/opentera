from flask.views import MethodView
from flask import render_template, request, session, abort
from modules.FlaskModule.FlaskModule import get_locale
from opentera.db.models import TeraService
from opentera.utils.TeraVersions import TeraVersions
import json


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
            # Get client informations from code
            auth_infos = self.flaskModule.redisGet('service_auth_code_' + session['auth_code'])
            if not auth_infos:
                abort(403)
            auth_infos = json.loads(auth_infos)
            client_name = auth_infos.get('client_name', 'OpenTera-Web-Client')
            client_version = auth_infos.get('client_version', None)
        else:
            # Generate generic clients information
            client_name = 'OpenTera-Web-Client'
            versions = TeraVersions()
            versions.load_from_db()
            client_version = versions.version_short_string

        session['client_name'] = client_name
        session['client_version'] = client_version

        theme_file = 'login_style'
        if 'theme' in request.args:
            if request.args['theme'] == 'light':
                theme_file = 'login_style_light'
        session['theme'] = theme_file

        if 'lang' in request.args:  # Force a specific language
            session['lang'] = request.args['lang']
        else:
            session['lang'] = get_locale()

        # Indicate if EmailService is enabled
        has_email_service = False
        email_service = TeraService.get_service_by_key('EmailService')
        if email_service:
            has_email_service = email_service.service_enabled

        # Check if we are embedded (i.e. OpenTeraPlus)
        embedded_view = 'X_CLIENT_NAME' in request.headers and request.headers['X_CLIENT_NAME'] == 'OpenTeraPlus'

        return render_template('login.html', hostname=hostname, port=port,
                               client_name=session['client_name'], client_version=session['client_version'],
                               show_logo=show_logo, theme_file=session['theme'], show_forgot_password=has_email_service,
                               with_websocket=with_websocket, current_locale=session['lang'], embedded=embedded_view)
