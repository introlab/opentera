from flask import jsonify, session, request
from flask_restx import Resource

from services.BureauActif.AccessManager import AccessManager, current_login_type, LoginType
from services.BureauActif.Globals import config_man
from services.BureauActif.FlaskModule import default_api_ns as api, flask_app


class QueryServiceInfos(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @api.doc(description='Gets service informations',
             responses={200: 'Success', 403: 'Forbidden - only logged user can get that information'})
    @AccessManager.token_required
    def get(self):

        if current_login_type != LoginType.USER_LOGIN:
            return '', 403

        infos = {'service_name': config_man.service_config['name'],
                 'service_uuid': config_man.service_config['ServiceUUID']
                 }

        return jsonify(infos)

