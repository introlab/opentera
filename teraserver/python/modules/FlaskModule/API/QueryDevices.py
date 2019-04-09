from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from sqlalchemy import exc
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from sqlalchemy.exc import InvalidRequestError
from libtera.db.models.TeraSiteAccess import TeraSiteAccess
from libtera.db.models.TeraProjectAccess import TeraProjectAccess
from flask_babel import gettext


class QueryDevices(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('id_device', type=int, help='id_device')
        self.parser.add_argument('id_kit', type=int, help='id_kit')
        self.parser.add_argument('device_uuid', type=str, help='device_uuid')

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        args = self.parser.parse_args()

        devices = []
        # If we have no arguments, return all accessible devices
        try:
            if not any(args.values()):
                devices = current_user.get_accessible_devices()

            device_list = []
            for device in devices:
                device_json = device.to_json()
                # device_json['project_role'] = queried_user.get_project_role(project)
                device_list.append(device_json)
            return jsonify(device_list)

        except InvalidRequestError:
            return '', 500

    @auth.login_required
    def post(self):
        return '', 501

    @auth.login_required
    def delete(self):
        return '', 501
