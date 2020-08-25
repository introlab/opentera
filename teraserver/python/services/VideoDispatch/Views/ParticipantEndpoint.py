from flask.views import MethodView
from flask import render_template, request
from services.VideoDispatch.AccessManager import AccessManager, current_participant_client

import json


class ParticipantEndpoint(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @AccessManager.token_required
    def get(self):
        backend_hostname = self.flaskModule.config.backend_config['hostname']
        backend_port = self.flaskModule.config.backend_config['port']

        if 'X_EXTERNALHOST' in request.headers:
            backend_hostname = request.headers['X_EXTERNALHOST']

        if 'X_EXTERNALPORT' in request.headers:
            backend_port = request.headers['X_EXTERNALPORT']

        # Get information from service API
        from services.VideoDispatch.Globals import service
        params = {'participant_uuid': current_participant_client.participant_uuid}
        response = service.get_from_opentera('/api/service/participants', params)

        if response.status_code == 200:
            participant_info = response.json()

            return render_template('participant_endpoint.html', backend_hostname=backend_hostname,
                                   backend_port=backend_port,
                                   participant_name=participant_info['participant_name'])
        else:
            return 'Unauthorized', 403
