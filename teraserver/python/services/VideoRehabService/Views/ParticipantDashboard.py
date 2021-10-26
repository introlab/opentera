from flask.views import MethodView
from flask import render_template, request
from flask_babel import gettext
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_participant_client, current_login_type\
    , LoginType


class ParticipantDashboard(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @ServiceAccessManager.token_required(allow_static_tokens=True, allow_dynamic_tokens=False)
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

        participant_name = gettext('Anonymous')

        if current_login_type != LoginType.PARTICIPANT_LOGIN:
            return render_template('participant_error.html', backend_hostname=backend_hostname,
                                   backend_port=backend_port,
                                   error_msg=gettext('Only participants can access this page. Sorry.'))

        if current_participant_client:
            participant_info = current_participant_client.get_participant_infos()
            if participant_info and 'participant_name' in participant_info:
                participant_name = participant_info['participant_name']

        return render_template('participant_dashboard.html', hostname=hostname, port=port,
                               backend_hostname=backend_hostname, backend_port=backend_port,
                               participant_name=participant_name,
                               participant_token=current_participant_client.participant_token,
                               participant_uuid=current_participant_client.participant_uuid
                               )
