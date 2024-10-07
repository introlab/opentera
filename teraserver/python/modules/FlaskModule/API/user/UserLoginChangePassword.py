from modules.FlaskModule.API.user.UserLoginBase import UserLoginBase
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.LoginModule.LoginModule import LoginModule, current_user
from opentera.db.models.TeraUser import TeraUser, UserPasswordInsecure, UserNewPasswordSameAsOld
from modules.FlaskModule.FlaskUtils import FlaskUtils

from flask_babel import gettext
from flask import redirect

post_parser = api.parser()
post_parser.add_argument('new_password', type=str, required=True, help='New password for the user')
post_parser.add_argument('confirm_password', type=str, required=True, help='Password confirmation for the user')

class UserLoginChangePassword(UserLoginBase):
    """
    UserLoginChangePassword endpoint resource.
    """

    @api.doc(description='Change password for the user. This API will only work if forced change is required on login. '
                         'Otherwise, use the standard \'api/user\' endpoint.')
    @api.expect(post_parser, validate=True)
    @LoginModule.user_session_required
    def post(self):
        """
        Change password for a user on login (forced change)
        """
        try:
            args = post_parser.parse_args(strict=True)
            new_password = args['new_password']
            confirm_password = args['confirm_password']

            # Validate if new password and confirm password are the same
            if new_password != confirm_password:
                return gettext('New password and confirm password do not match'), 400

            # Change password, will be encrypted
            # Will also reset force password change flag
            try:
                TeraUser.update(current_user.id_user, {'user_password': new_password,
                                                       'user_force_password_change': False})
            except UserPasswordInsecure as e:
                return FlaskUtils.get_password_weaknesses_text(e.weaknesses, '<br>'), 400
            except UserNewPasswordSameAsOld:
                return gettext('New password same as old password'), 400

            return redirect(self._generate_login_url())
        except Exception as e:
            # Something went wrong, logout user
            self._user_logout()
            raise e
