from flask_restx import Resource
from opentera.services.ServiceAccessManager import ServiceAccessManager, current_login_type, current_device_client, \
    current_participant_client, current_user_client, LoginType
from services.BureauActif.FlaskModule import default_api_ns as api


class QueryAccountInfos(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @api.doc(description='Gets current login type: device, participant or user and associated informations',
             responses={200: 'Success'})
    @ServiceAccessManager.token_required
    def get(self):
        account_infos = {
            'login_type': 'unknown',
            'login_id': 0,
            'is_super_admin': False,
            'username': 'unknown'
        }

        if current_login_type == LoginType.DEVICE_LOGIN:
            account_infos['login_type'] = 'device'
            account_infos['login_id'] = current_device_client.id_device

        if current_login_type == LoginType.PARTICIPANT_LOGIN:
            participant = current_participant_client.get_participant_infos()
            account_infos['login_type'] = 'participant'
            account_infos['login_id'] = current_participant_client.id_participant
            account_infos['username'] = participant['participant_username']

        if current_login_type == LoginType.USER_LOGIN:
            user = current_user_client.get_user_info()
            account_infos['login_type'] = 'user'
            account_infos['login_id'] = current_user_client.id_user
            account_infos['is_super_admin'] = current_user_client.user_superadmin
            account_infos['username'] = user[0]['user_username']
            account_infos.update({'sites': user[0]['sites']})

        return account_infos

