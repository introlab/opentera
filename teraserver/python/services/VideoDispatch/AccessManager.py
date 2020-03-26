from werkzeug.local import LocalProxy
from functools import wraps
from flask import _request_ctx_stack, request, redirect
from flask_restplus import reqparse

from services.VideoDispatch.Globals import api_user_token_key, api_participant_token_key, TokenCookieName
from services.VideoDispatch.TeraUserClient import TeraUserClient
from services.VideoDispatch.TeraParticipantClient import TeraParticipantClient

# Current client identity, stacked
current_user_client = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_user_client', None))
current_participant_client = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_participant_client', None))


class AccessManager:
    @staticmethod
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):

            login_path = '/login'

            # Using a reverse proxy?
            if 'X-Script-Name' in request.headers:
                login_path = request.headers['X-Script-Name'] + login_path

            # Check if we have a token in the request itself
            parser = reqparse.RequestParser()
            parser.add_argument('participant_token', type=str, help='Participant Token', required=False)
            parser.add_argument('user_token', type=str, help='User Token', required=False)

            # Parse arguments
            request_args = parser.parse_args(strict=False)

            if request_args['participant_token']:
                # Handle participant tokens
                token_value = request_args['participant_token']

                # Verify token from redis
                import jwt
                try:
                    token_dict = jwt.decode(token_value, api_participant_token_key)
                except jwt.exceptions.InvalidSignatureError as e:
                    print(e)
                    return 'Unauthorized', 403

                if token_dict['participant_uuid']:
                    _request_ctx_stack.top.current_participant_client = \
                        TeraParticipantClient(token_dict['participant_uuid'], token_value)
                    return f(*args, **kwargs)

                # Default, not authorized
                return 'Unauthorized', 403
            else:

                token_value = request_args['user_token']

                # If not, check if we have a token in the cookies
                if token_value is None:
                    if TokenCookieName in request.cookies:
                        token_value = request.cookies[TokenCookieName]

                # If we don't have any token, refuse access and redirect to login
                if token_value is None:
                    return redirect(login_path)

                # Verify token from redis
                import jwt
                try:
                    token_dict = jwt.decode(token_value, api_user_token_key)
                except jwt.exceptions.InvalidSignatureError as e:
                    print(e)
                    return redirect(login_path)

                if token_dict['user_uuid']:
                    _request_ctx_stack.top.current_user_client = TeraUserClient(token_dict['user_uuid'], token_value)
                    return f(*args, **kwargs)

                # Any other case, do not call function
                return redirect(login_path)

        return decorated
