from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraKitDevice import TeraKitDevice
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc


class QueryKitDevice(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])

        parser = reqparse.RequestParser()
        parser.add_argument('id_device', type=int, help='id_device')
        parser.add_argument('id_kit', type=int, help='id_kit')

        args = parser.parse_args()

        kit_device = []
        # If we have no arguments, return error
        if not any(args.values()):
            return 'Missing arguments.', 400

        if args['id_device']:
            kit_device = [TeraKitDevice.query_kit_device_for_device(current_user=current_user,
                                                                    device_id=args['id_device'])]
        else:
            if args['id_kit']:
                kit_device = [TeraKitDevice.query_kit_device_for_kit(current_user=current_user, kit_id=args['id_kit'])]

        if kit_device is None:
            kit_device = []
        try:
            return jsonify(kit_device.to_json())

        except InvalidRequestError:
            return '', 500

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('kit_device', type=str, location='json', help='Kit device to create / update',
                            required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        # Using request.json instead of parser, since parser messes up the json!
        json_kit_device = request.json['kit_device']

        # Validate if we have an id
        if 'id_device' not in json_kit_device and 'id_kit' not in json_kit_device and 'id_kit_device' not \
                in json_kit_device:
            return '', 400

        # Check if current user can modify the posted device
        if json_kit_device['id_kit'] not in current_user.get_accessible_devices_ids(admin_only=True) and \
                json_kit_device['id_kit'] > 0:
            return '', 403

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
            # New
            try:
                new_kit_device = TeraKitDevice()
                new_kit_device.from_json(json_kit_device)
                TeraKitDevice.insert_device(new_kit_device)
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

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        if id_todel not in current_user.get_accessible_devices_ids(admin_only=True) is None:
            return '', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraKitDevice.delete_kit_device(id_kit_device=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200
