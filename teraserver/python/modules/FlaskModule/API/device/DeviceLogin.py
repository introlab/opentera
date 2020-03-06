from flask import jsonify, session, request
from flask_restplus import Resource, reqparse
from modules.LoginModule.LoginModule import LoginModule, current_device
from modules.Globals import db_man
from modules.FlaskModule.FlaskModule import device_api_ns as api


class DeviceLogin(Resource):

    def __init__(self, _api, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self, _api)
        self.parser = reqparse.RequestParser()

    @LoginModule.token_or_certificate_required
    def get(self):

        # Redis key is handled in LoginModule
        servername = self.module.config.server_config['hostname']
        port = self.module.config.server_config['port']

        if 'X_EXTERNALHOST' in request.headers:
            if ':' in request.headers['X_EXTERNALHOST']:
                servername, port = request.headers['X_EXTERNALHOST'].split(':', 1)
            else:
                servername = request.headers['X_EXTERNALHOST']

        if 'X_EXTERNALPORT' in request.headers:
            port = request.headers['X_EXTERNALPORT']

        # Reply device information
        reply = {'device_info': current_device.to_json()}

        device_access = db_man.deviceAccess(current_device)

        # Reply participant information
        participants = device_access.get_accessible_participants()
        reply['participants_info'] = list()

        for participant in participants:
            reply['participants_info'].append(participant.device_participant_participant.to_json())

        # Reply accessible sessions type ids
        session_types = device_access.get_accessible_session_types()
        reply['session_types_info'] = list()

        for st in session_types:
            reply['session_types_info'].append(st.to_json())

        # TODO Handle sessions
        if current_device.device_onlineable:
            # Permanent ?
            session.permanent = True

            print('DeviceLogin - setting key with expiration in 60s', session['_id'], session['_user_id'])
            self.module.redisSet(session['_id'], session['_user_id'], ex=60)

            # Add websocket URL
            reply['websocket_url'] = "wss://" + servername + ":" + str(port) + "/wss/device?id=" + session['_id']

        # Return reply as json object
        return jsonify(reply)
