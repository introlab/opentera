from flask.views import MethodView
from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user
from opentera.utils.TeraVersions import TeraVersions
from opentera.db.models.TeraUser import TeraUser
from modules.LoginModule.LoginModule import LoginModule
from flask_babel import gettext
from modules.LoginModule.LoginModule import current_user, LoginModule

class LoginChangePasswordView(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @LoginModule.user_session_required
    def get(self):
        hostname = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']

        if 'X_EXTERNALSERVER' in request.headers:
            hostname = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        versions = TeraVersions()
        versions.load_from_db()

        return render_template('login_change_password.html', hostname=hostname, port=port,
                               server_version=versions.version_string, username=current_user.user_username)

    @LoginModule.user_session_required
    def post(self):

        # Verify if form is complete
        if ('old_password' not in request.form or 'new_password' not in request.form
                or 'confirm_password' not in request.form):
            return gettext('Missing information'), 400

        # Get form information
        old_password = request.form['old_password']
        new_password = request.form['new_password']
        confirm_password = request.form['confirm_password']

        # Validate if new password and confirm password are the same
        if new_password != confirm_password:
            logout_user()
            return gettext('New password and confirm password do not match'), 400

        # Validate if old password is correct
        if TeraUser.verify_password(current_user.user_username, old_password) is None:
            logout_user()
            return gettext('Invalid old password'), 400

        # Change password, will be encrypted
        # Will also reset force password change flag
        TeraUser.update(current_user.id_user, {'user_password': new_password,
                                               'user_force_password_change': False })

        logout_user()

        return redirect(url_for('login'))
