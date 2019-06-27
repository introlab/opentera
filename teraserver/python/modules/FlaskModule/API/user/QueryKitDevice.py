from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraKitDevice import TeraKitDevice
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc


class QueryKitDevice(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = reqparse.RequestParser()
        parser.add_argument('id_device', type=int, help='id_device')
        parser.add_argument('id_kit', type=int, help='id_kit')

        args = parser.parse_args()

        kit_device = []
        # If we have no arguments, return error
        if not any(args.values()):
            return 'Missing arguments.', 400

        if args['id_device']:
            if args['id_device'] in user_access.get_accessible_devices_ids():
                kit_device = TeraKitDevice.query_kit_device_for_device(device_id=args['id_device'])
        else:
            if args['id_kit']:
                if args['id_kit'] in user_access.get_accessible_kits_ids():
                    kit_device = TeraKitDevice.query_kit_device_for_kit(kit_id=args['id_kit'])
        try:
            kit_device_list = []
            for kd in kit_device:
                kit_device_list.append(kd.to_json())
            return jsonify(kit_device_list)

        except InvalidRequestError:
            return '', 500

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('kit_device', type=str, location='json', help='Kit device to create / update',
                            required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        json_kit_devices = request.json['kit_device']
        if not isinstance(json_kit_devices, list):
            json_kit_devices = [json_kit_devices]

        # Validate if we have an id
        for json_kit_device in json_kit_devices:
            if 'id_device' not in json_kit_device and 'id_kit' not in json_kit_device:
                return '', 400

            # Check if current user can modify the posted device
            if json_kit_device['id_kit'] not in user_access.get_accessible_kits_ids(admin_only=True) or \
                    json_kit_device['id_device'] not in user_access.get_accessible_devices_ids(admin_only=True):
                return 'Accès refusé', 403

            # Check if already exists
            kit_device = TeraKitDevice.query_kit_device_for_kit_device(device_id=json_kit_device['id_device'],
                                                                       kit_id=json_kit_device['id_kit'])
            if kit_device:
                json_kit_device['id_kit_device'] = kit_device.id_kit_device
            else:
                json_kit_device['id_kit_device'] = 0

            # Do the update!
            if json_kit_device['id_kit_device'] > 0:
                # Already existing
                try:
                    TeraKitDevice.update_kit_device(json_kit_device['id_kit_device'], json_kit_device)
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500
            else:
                try:
                    new_kit_device = TeraKitDevice()
                    new_kit_device.from_json(json_kit_device)
                    TeraKitDevice.insert_kit_device(new_kit_device)
                    # Update ID for further use
                    json_kit_device['id_kit_device'] = new_kit_device.id_kit_device
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500

        # TODO: Publish update to everyone who is subscribed to devices update...
        update_kit_device = TeraKitDevice.get_kit_device_by_id(json_kit_device['id_kit_device'])

        return jsonify([update_kit_device.to_json()])

    @auth.login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        kit_device = TeraKitDevice.get_kit_device_by_id(id_todel)
        if not kit_device:
            return 'Not found.', 500

        if kit_device.id_kit not in user_access.get_accessible_kits_ids(admin_only=True) or kit_device.id_device not in \
                user_access.get_accessible_devices_ids(admin_only=True):
            return 'Access denied', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraKitDevice.delete_kit_device(id_kit_device=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200
