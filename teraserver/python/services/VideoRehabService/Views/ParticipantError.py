from flask.views import MethodView
from flask import render_template, request
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_participant_client
from flask_babel import gettext


class ParticipantError(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @ServiceAccessManager.static_token_required
    def get(self):
        backend_hostname = self.flaskModule.config.backend_config['hostname']
        backend_port = self.flaskModule.config.backend_config['port']

        if 'X_EXTERNALHOST' in request.headers:
            backend_hostname = request.headers['X_EXTERNALHOST']

        if 'X_EXTERNALPORT' in request.headers:
            backend_port = request.headers['X_EXTERNALPORT']

        if 'error' in request.args:
            error_msg = request.args['error']
        else:
            error_msg = gettext('Unknown error')

        participant_name = 'Anonymous'

        # Get participant information
        if current_participant_client:
            return render_template('participant_error.html', backend_hostname=backend_hostname,
                                   backend_port=backend_port,
                                   participant_token=current_participant_client.participant_token,
                                   error_msg=error_msg)
        else:
            return 'Unauthorized', 403
