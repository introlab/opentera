from flask_login import logout_user
from flask_restx import Resource, reqparse
from flask_babel import gettext
from flask import session, request
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.LoginModule.LoginModule import user_multi_auth, current_user, LoginModule

# Parser definition(s)
get_parser = api.parser()


class UserLogout(Resource):
    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Logout from the server', params={'token': 'Secret token'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        if current_user:
            logout_user()
            session.clear()
            self.module.send_user_disconnect_module_message(current_user.user_uuid)

            # Add token to disabled set
            if 'Authorization' in request.headers:
                scheme, old_token = request.headers['Authorization'].split(None, 1)
                if scheme == 'OpenTera':
                    LoginModule.user_add_disabled_token(old_token)

            return gettext("User logged out."), 200
        else:
            return gettext("User not logged in"), 403

