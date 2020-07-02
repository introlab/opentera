from flask.views import MethodView
from flask import render_template, request
from services.shared.ServiceAccessManager import ServiceAccessManager, current_user_client, \
    current_participant_client, current_device_client

import json


class Dashboard(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @ServiceAccessManager.static_token_required
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

        user_fullname = "Anonymous"
        is_participant = True

        if current_participant_client:
            participant_info = current_participant_client.get_participant_infos()
            if participant_info and 'participant_name' in participant_info:
                user_fullname = participant_info['participant_name']

        # if current_user_client:
        #     user_reply = current_user_client.do_get_request_to_backend('/api/user/users?user_uuid='
        #                                                                + current_user_client.user_uuid)
        #     # print(current_user_client.get_role_for_site(1))
        #     # print(current_user_client.get_role_for_project(1))
        #     if user_reply.status_code == 200:
        #         user_json = json.loads(user_reply.content)
        #         user_fullname = user_json[0]['user_name']
        #     is_participant = False
        # else:
        #     if current_participant_client:
        #         participant_reply = current_participant_client.do_get_request_to_backend(
        #             '/api/participant/participants')
        #
        #         if participant_reply.status_code == 200:
        #             participant_json = json.loads(participant_reply.content)
        #             user_fullname = participant_json['participant_name']

        return render_template('dashboard.html', hostname=hostname, port=port,
                               backend_hostname=backend_hostname, backend_port=backend_port,
                               user_fullname=user_fullname, is_participant=is_participant,
                               participant_token=current_participant_client.participant_token
                               )
