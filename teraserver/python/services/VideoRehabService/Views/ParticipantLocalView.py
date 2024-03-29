from flask.views import MethodView
from flask import render_template, request
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_login_type, LoginType
from flask_babel import gettext


class ParticipantLocalView(MethodView):

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

        if current_login_type != LoginType.PARTICIPANT_LOGIN:
            return render_template('participant_error.html', backend_hostname=backend_hostname,
                                   backend_port=backend_port,
                                   error_msg=gettext('Only participants can access this page. Sorry.'))

        message = gettext('Your session will start soon. Thank you for your patience!')
        if 'message' in request.args:
            message = request.args['message']
        message_type = 'info'
        if 'message_type' in request.args:
            message_type = request.args['message_type']

        # Query full participant infos
        # participant_info = current_participant_client.get_participant_infos()

        return render_template('participant_localview.html', hostname=hostname, port=port,
                               backend_hostname=backend_hostname, backend_port=backend_port, message=message,
                               message_type=message_type)

        # Get participant information
        # response = current_participant_client.do_get_request_to_backend('/api/participant/participants')
        #
        # if response.status_code == 200:
        #     participant_info = response.json()
        #
        #     return render_template('participant.html', hostname=hostname, port=port,
        #                            backend_hostname=backend_hostname, backend_port=backend_port,
        #                            participant_name=participant_info['participant_name'],
        #                            participant_email=participant_info['participant_email'])
        # else:
        #     return 'Unauthorized', 403

