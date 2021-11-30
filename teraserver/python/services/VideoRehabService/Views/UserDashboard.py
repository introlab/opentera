from flask.views import MethodView
from flask import render_template, request
from flask_babel import gettext
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_user_client, current_login_type, \
    LoginType


class UserDashboard(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @ServiceAccessManager.token_required(allow_static_tokens=False, allow_dynamic_tokens=True)
    def get(self):
        # print('get')

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

        user_name = gettext('Anonymous')
        if current_user_client:
            user_info = current_user_client.get_user_info()
            if user_info and 'user_name' in user_info:
                user_name = user_info['user_name']

        return render_template('user_dashboard.html', hostname=hostname, port=port,
                               backend_hostname=backend_hostname, backend_port=backend_port,
                               user_name=user_name,
                               user_token=current_user_client.user_token,
                               user_uuid=current_user_client.user_uuid
                               )
