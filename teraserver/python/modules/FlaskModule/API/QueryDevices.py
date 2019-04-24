from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraDevice import TeraDevice
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from libtera.db.DBManager import DBManager


class QueryDevices(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = reqparse.RequestParser()
        parser.add_argument('id_device', type=int, help='id_device')
        # parser.add_argument('device_uuid', type=str, help='device_uuid')

        args = parser.parse_args()

        devices = []
        # If we have no arguments, return all accessible devices
        if not any(args.values()):
            devices = user_access.get_accessible_devices()

        if args['id_device']:
            devices.append(user_access.query_device_by_id(device_id=args['id_device']))

        try:
            device_list = []
            for device in devices:
                if device is not None:
                    device_json = device.to_json()
                    device_list.append(device_json)
            return jsonify(device_list)

        except InvalidRequestError:
            return '', 500

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('device', type=str, location='json', help='Device to create / update', required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_device = request.json['device']

        # Validate if we have an id
        if 'id_device' not in json_device:
            return '', 400

        # Check if current user can modify the posted device
        if json_device['id_site'] not in user_access.get_accessible_sites_ids(admin_only=True) and \
                json_device['id_site'] > 0:
            return '', 403

        # Do the update!
        if json_device['id_device'] > 0:
            # Already existing
            try:
                TeraDevice.update_device(json_device['id_device'], json_device)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # New
            try:
                new_device = TeraDevice()
                new_device.from_json(json_device)
                TeraDevice.insert_device(new_device)
                # Update ID for further use
                json_device['id_device'] = new_device.id_device
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        # TODO: Publish update to everyone who is subscribed to devices update...
        update_device = TeraDevice.get_device_by_id(json_device['id_device'])

        return jsonify([update_device.to_json()])

    @auth.login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        if user_access.query_device_by_id(device_id=id_todel) is None:
            return '', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraDevice.delete_device(id_device=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200
