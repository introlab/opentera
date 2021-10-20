from flask.views import MethodView
from flask import render_template, request
from flask_babel import gettext
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_user_client, current_login_type, \
    LoginType


class UserSessionLobby(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @ServiceAccessManager.token_required(allow_static_tokens=False, allow_dynamic_tokens=True)
    def get(self):

        hostname = self.flaskModule.config.service_config['hostname']
        port = self.flaskModule.config.service_config['port']
        backend_hostname = self.flaskModule.config.backend_config['hostname']
        backend_port = self.flaskModule.config.backend_config['port']
        if 'X_EXTERNALSERVER' in request.headers:
            backend_hostname = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            backend_port = request.headers['X_EXTERNALPORT']

        if current_login_type != LoginType.USER_LOGIN:
            return render_template('user_error.html', backend_hostname=backend_hostname,
                                   backend_port=backend_port,
                                   error_msg=gettext('Only users can access this page. Sorry.'))

        if 'session_uuid' not in request.args:
            return render_template('user_error.html', backend_hostname=backend_hostname,
                                   backend_port=backend_port,
                                   error_msg=gettext('An existing session needs to be specified.'))

        # Get session
        response = current_user_client.do_get_request_to_backend('/api/user/sessions?session_uuid='
                                                                 + request.args['session_uuid'])

        if response.status_code == 200:
            # Parse JSON reply
            import json
            sessions = json.loads(response.text)
            if not sessions:
                return render_template('user_error.html', backend_hostname=backend_hostname,
                                       backend_port=backend_port,
                                       error_msg=gettext("Unknown session"))
            current_session = sessions[0]

        else:
            return render_template('user_error.html', backend_hostname=backend_hostname,
                                   backend_port=backend_port,
                                   error_msg=gettext("Can't query session information: Error ") +
                                   str(response.status_code))

        user_info = current_user_client.get_user_info()

        return render_template('user_session_lobby.html', hostname=hostname, port=port,
                               backend_hostname=backend_hostname, backend_port=backend_port,
                               user_token=current_user_client.user_token,
                               session_uuid=request.args['session_uuid'],
                               session_name=current_session['session_name'],
                               session_users=current_session['session_users'],
                               session_participants=current_session['session_participants'],
                               session_devices=current_session['session_devices']
                               )
