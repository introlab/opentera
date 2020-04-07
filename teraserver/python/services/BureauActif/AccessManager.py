from werkzeug.local import LocalProxy
from functools import wraps
from flask import _request_ctx_stack, request, redirect
from flask_restx import reqparse

from services.BureauActif.Globals import api_user_token_key, TokenCookieName
from services.BureauActif.TeraClient import TeraClient

# Current client identity, stacked
current_client = LocalProxy(lambda: getattr(_request_ctx_stack.top, 'current_client', None))


class AccessManager:

    @staticmethod
    def token_required(f):
        @wraps(f)
        def decorated(*args, **kwargs):
            # Check if we have a token in the request itself
            parser = reqparse.RequestParser()
            parser.add_argument('token', type=str, help='Token', required=False)

            request_args = parser.parse_args(strict=False)
            token_value = request_args['token']

            # If not, check if we have a token in the cookies
            if token_value is None:
                if TokenCookieName in request.cookies:
                    token_value = request.cookies[TokenCookieName]

            # If we don't have any token, refuse access and redirect to login
            if token_value is None:
                return redirect("login")

            # Verify token from redis
            import jwt
            try:
                token_dict = jwt.decode(token_value, api_user_token_key)
            except jwt.exceptions.InvalidSignatureError as e:
                print(e)
                return redirect("login")

            if token_dict['user_uuid']:
                _request_ctx_stack.top.current_client = TeraClient(token_dict['user_uuid'], token_value, )

                # TODO: Validate user_uuid from online users list in Redis?
                return f(*args, **kwargs)
            #
            # _request_ctx_stack.top.current_participant = TeraParticipant.get_participant_by_token(args['token'])
            #
            #
            #
            # if current_participant and current_participant.participant_enabled:
            #     # Returns the function if authenticated with token
            #     return f(*args, **kwargs)
            #
            # # Load device from DB
            # _request_ctx_stack.top.current_device = TeraDevice.get_device_by_token(args['token'])
            #
            # if current_device and current_device.device_enabled:
            #     # Returns the function if authenticated with token
            #     return f(*args, **kwargs)

            # Any other case, do not call function
            return redirect("login")

        return decorated
