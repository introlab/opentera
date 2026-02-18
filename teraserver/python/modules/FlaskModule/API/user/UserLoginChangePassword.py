from flask_babel import gettext

from modules.FlaskModule.API.user.UserLoginBase import UserLoginBase, InvalidAuthCodeError
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.LoginModule.LoginModule import LoginModule, current_user
from modules.FlaskModule.FlaskUtils import FlaskUtils
from opentera.db.models.TeraUser import TeraUser, UserPasswordInsecure, UserNewPasswordSameAsOld

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

            self._verify_auth_code()

            # Validate if new password and confirm password are the same
            if new_password != confirm_password:
                return gettext('New password and confirm password do not match'), 400

            if not current_user.user_force_password_change:
                return gettext('User not required to change password'), 400

            # Change password, will be encrypted
            # Will also reset force password change flag
            try:
                TeraUser.update(current_user.id_user, {'user_password': new_password,
                                                       'user_force_password_change': False})
            except InvalidAuthCodeError as e:
                return str(e), 403
            except UserPasswordInsecure as e:
                return FlaskUtils.get_password_weaknesses_text(e.weaknesses, '<br>'), 400
            except UserNewPasswordSameAsOld:
                return gettext('New password same as old password'), 400

            return gettext('Password changed'), 200
        except Exception as e:
            # Something went wrong, logout user
            self._user_logout()
            raise e
