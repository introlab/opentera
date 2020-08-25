from flask.views import MethodView
from flask import render_template, request
from services.VideoDispatch.AccessManager import AccessManager, current_user_client, current_participant_client

import json


class Dashboard(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @AccessManager.token_required
    def get(self):
        # print('get')

        hostname = self.flaskModule.config.service_config['hostname']
        port = self.flaskModule.config.service_config['port']
        backend_hostname = self.flaskModule.config.backend_config['hostname']
        backend_port = self.flaskModule.config.backend_config['port']
        if 'X_EXTERNALHOST' in request.headers:
            backend_hostname = request.headers['X_EXTERNALHOST']

        if 'X_EXTERNALPORT' in request.headers:
            backend_port = request.headers['X_EXTERNALPORT']

        user_fullname = "???"
        is_participant = True
        if current_user_client:
            user_reply = current_user_client.do_get_request_to_backend('/api/user/users?user_uuid='
                                                                       + current_user_client.user_uuid)
            # print(current_user_client.get_role_for_site(1))
            # print(current_user_client.get_role_for_project(1))
            if user_reply.status_code == 200:
                user_json = json.loads(user_reply.content)
                user_fullname = user_json[0]['user_name']
            is_participant = False
        else:
            if current_participant_client:
                # Get information from service API
                from services.VideoDispatch.Globals import service
                params = {'participant_uuid': current_participant_client.participant_uuid}
                participant_reply = service.get_from_opentera('/api/service/participants', params)

                if participant_reply.status_code == 200:
                    participant_json = participant_reply.json()
                    user_fullname = participant_json['participant_name']

        return render_template('dashboard.html', hostname=hostname, port=port,
                               backend_hostname=backend_hostname, backend_port=backend_port,
                               user_fullname=user_fullname, is_participant=is_participant
                               )

    def post(self):
        print('post')
        pass