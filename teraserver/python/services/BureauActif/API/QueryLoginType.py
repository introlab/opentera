from flask import jsonify, session, request
from flask_restx import Resource

from services.shared.ServiceAccessManager import ServiceAccessManager, current_login_type, current_device_client, \
    current_participant_client, current_user_client, LoginType
from services.BureauActif.FlaskModule import default_api_ns as api, flask_app


class QueryLoginType(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @api.doc(description='Gets current login type: device, participant or user and associated informations',
             responses={200: 'Success'})
    @ServiceAccessManager.token_required
    def get(self):
        login_infos = {
            'login_type': 'unknown',
            'login_id': 0,
            'is_super_admin': False
        }

        if current_login_type == LoginType.DEVICE_LOGIN:
            login_infos['login_type'] = 'device'
            login_infos['login_id'] = current_device_client.id_device

        if current_login_type == LoginType.PARTICIPANT_LOGIN:
            login_infos['login_type'] = 'participant'
            login_infos['login_id'] = current_participant_client.id_participant

        if current_login_type == LoginType.USER_LOGIN:
            login_infos['login_type'] = 'user'
            login_infos['login_id'] = current_user_client.id_user
            login_infos['is_super_admin'] = current_user_client.user_superadmin

        return login_infos

