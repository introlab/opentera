from flask.views import MethodView
from flask import render_template, request
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_user_client
from flask_babel import gettext


class UserError(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @ServiceAccessManager.token_required(allow_static_tokens=False, allow_dynamic_tokens=True)
    def get(self):
        backend_hostname = self.flaskModule.config.backend_config['hostname']
        backend_port = self.flaskModule.config.backend_config['port']

        if 'X_EXTERNALSERVER' in request.headers:
            backend_hostname = request.headers['X_EXTERNALSERVER']

        if 'X_EXTERNALPORT' in request.headers:
            backend_port = request.headers['X_EXTERNALPORT']

        if 'error' in request.args:
            error_msg = request.args['error']
        else:
            error_msg = gettext('Unknown error')

        # Get participant information
        if current_user_client:
            return render_template('user_error.html', backend_hostname=backend_hostname,
                                   backend_port=backend_port,
                                   user_token=current_user_client.user_token,
                                   error_msg=error_msg)
        else:
            return 'Unauthorized', 403
