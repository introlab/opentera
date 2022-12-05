from flask_login import logout_user
from flask_restx import Resource, reqparse
from flask_babel import gettext
from flask import session
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.LoginModule.LoginModule import user_multi_auth, current_user


class UserLogout(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Logout from the server')
    @user_multi_auth.login_required
    def get(self):
        if current_user:
            print('logout user')
            logout_user()
            session.clear()
            self.module.send_user_disconnect_module_message(current_user.user_uuid)
            return gettext("User logged out."), 200
        else:
            return gettext("User not logged in"), 403

