from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask_babel import gettext

from modules.FlaskModule.FlaskModule import flask_app, session
from modules.FlaskModule.API.user.UserLoginBase import UserLoginBase
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.FlaskModule.FlaskUtils import FlaskUtils
from modules.LoginModule.LoginModule import LoginModule, current_user

from opentera.db.models.TeraUser import TeraUser
from opentera.redis.RedisRPCClient import RedisRPCClient

import time
import secrets
import re

limiter = Limiter(get_remote_address, app=flask_app, storage_uri="memory://")

post_parser = api.parser()
post_parser.add_argument('requested_user', type=str, required=True, help='Requested username or email to reset password')

put_parser = api.parser()
put_parser.add_argument('reset_code', type=str, required=True, help='Reset code to validate')


def get_post_limited_account_id():
    args = post_parser.parse_args()
    if 'requested_user' in args:
        return args['requested_user']
    return ''

def get_put_limited_account_id():
    if '_user_id' in session:
        return session['_user_id']
    return ''


class UserLoginForgotPassword(UserLoginBase):
    """
    UserLoginForgotPassword endpoint resource.
    """

    @staticmethod
    def get_redis_key_for_user(user_uuid: str):
        return 'user.' + user_uuid + '.ResetCode'

    @api.doc(description='Reset password for the specified user.',
             responses={200: 'Success - will be returned even if specified user isn\'t found',
                        400: 'Badly formed request',
                        429: 'Too many requests for the current username / email'}
             )
    @api.expect(post_parser, validate=True)
    @limiter.limit("6/minute", error_message='Rate Limited', key_func=get_post_limited_account_id)
    def post(self):
        args = post_parser.parse_args(strict=True)

        # Regex pattern matching standard email formatting
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

        # Check if user exists
        if re.fullmatch(pattern, args['requested_user']):
            user = TeraUser.get_user_by_email(args['requested_user'])
        else:
            user = TeraUser.get_user_by_username(args['requested_user'])

        if user:
            # Super admins and disabled users passwords can't be reset here
            if not user.user_superadmin and user.user_enabled and user.user_email:
                if re.fullmatch(pattern, user.user_email):
                    # Valid email - Initiate reset process
                    # Generate reset code
                    code = FlaskUtils.generate_unique_code(8)

                    # Save code associated with user in redis
                    redis_key = UserLoginForgotPassword.get_redis_key_for_user(user.user_uuid)
                    self.module.redis.set(redis_key, code, ex=600) # Expire after 10 minutes

                    # Send email with reset code
                    rpc = RedisRPCClient(self.module.config.redis_config)
                    email_infos = {'email_subject': gettext('Password reset request'),
                                   'email_body': gettext('Hi') + ' <b>' + user.user_firstname + '</b>,<br><br>' +
                                                 gettext('A password reset has been requested. Here\'s your code '
                                                         'to initiate the reset') + '<br><br><b>' + code + '</b><br><br>' +
                                                 gettext('This code is valid for 10 minutes.') + '<br><br>' +
                                                 gettext('If you didn\'t request a password reset, you can ignore this '
                                                         'message.') + '<br><br>----<br>' +
                                                 gettext('This email was sent from the server') + ': ' +
                                                 self.module.config.server_config['name'] + '.<br>' +
                                                 gettext('If you have any issue, contact your local support - don\'t reply '
                                                         'to this email address.'),
                                   'email_recipients': user.user_email, 'email_sender': ''}
                    answer = rpc.call_service('EmailService', 'send_email',
                                              email_infos["email_subject"], email_infos["email_body"],
                                              email_infos["email_recipients"], email_infos["email_sender"])
                    if answer:
                        session['_user_id'] = user.user_uuid
                        return 200
        # Sleep for a random time between 2 and 4 seconds, to simulate email sending
        sleep_time = 2 + secrets.randbelow(2000)/1000
        time.sleep(sleep_time)
        return 200

    @api.doc(description='Validate reset code for the current user in session.',
             responses={200: 'Success - code is valid for the user in current session',
                        401: 'Bad code or unauthorized access',
                        429: 'Too many requests for the current user'}
             )
    @api.expect(put_parser, validate=True)
    @LoginModule.user_session_required
    @limiter.limit("1/second,50/hour", error_message='Rate Limited', key_func=get_put_limited_account_id)
    def put(self):
        args = put_parser.parse_args(strict=True)
        redis_key = UserLoginForgotPassword.get_redis_key_for_user(current_user.user_uuid)
        compare_code = self.module.redis.get(redis_key)
        reset_code = str(args['reset_code']).replace(' ', '')
        if compare_code and compare_code.decode('utf8') == reset_code:
            self.module.redis.delete(redis_key)
            session["password_resetting"] = True
            return 200
        return 'Unauthorized', 401