from flask.views import MethodView
from flask import render_template, request, redirect, url_for
from flask_login import login_user
from opentera.utils.TeraVersions import TeraVersions
from opentera.db.models.TeraUser import TeraUser
from modules.LoginModule.LoginModule import LoginModule


class LoginView(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    def get(self):
        hostname = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']

        if 'X_EXTERNALSERVER' in request.headers:
            hostname = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        versions = TeraVersions()
        versions.load_from_db()

        return render_template('login.html', hostname=hostname, port=port,
                               server_version=versions.version_string,
                               openteraplus_version=versions.get_client_version_with_name('OpenTeraPlus'))

    def post(self):
        # Verify the form
        if 'username' not in request.form or 'password' not in request.form:
            return 'Missing username or password', 400

        # Get the user's name and password from the form
        username = request.form['username']
        password = request.form['password']
        print(f'Username: {username}, Password: ******')

        # TODO Should use LoginModule instead of TeraUser directly
        # Check the user's credentials
        user = TeraUser.verify_password(username, password)
        if user is None:
            return 'Invalid username or password', 401

        login_user(user, remember=False)

        # Check if the user has 2FA enabled
        # We may want to change the behavior here according to a configuration flag
        if not user.user_2fa_enabled:
            # Redirect to enable 2FA page
            return redirect(url_for('login_enable_2fa'))
        else:
            # Redirect to 2FA validation page
            return redirect(url_for('login_validate_2fa'))

        return 'OK', 200





        # Log the user in

        # redirect to the 2fa page
        return 'Success', 200



