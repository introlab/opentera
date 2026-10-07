from flask.views import MethodView
from flask import render_template, request, session


class LoginForgotPasswordView(MethodView):

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

        if 'theme' not in session:
            session['theme'] = 'login_style'

        return render_template('login_forgot_password.html', hostname=hostname, port=port,
                                theme_file=session['theme'])