from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext


class QueryDeviceParticipants(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = reqparse.RequestParser()
        parser.add_argument('id_device', type=int, help='id_device')
        parser.add_argument('id_participant', type=int, help='id_participant')
        parser.add_argument('list', type=bool)

        args = parser.parse_args()

        device_part = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Arguments manquants'), 400

        if args['id_device']:
            if args['id_device'] in user_access.get_accessible_devices_ids():
                device_part = TeraDeviceParticipant.query_participants_for_device(device_id=args['id_device'])
        else:
            if args['id_participant']:
                if args['id_participant'] in user_access.get_accessible_participants_ids():
                    device_part = TeraDeviceParticipant.query_devices_for_participant(
                        participant_id=args['id_participant'])
        try:
            device_part_list = []
            for dp in device_part:
                json_dp = dp.to_json()
                if args['list'] is None:
                    json_dp['participant_name'] = dp.device_participant_participant.participant_name
                    json_dp['device_name'] = dp.device_participant_device.device_name
                device_part_list.append(json_dp)

            return jsonify(device_part_list)

        except InvalidRequestError:
            return '', 400

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('device_participant', type=str, location='json',
                            help='Device participant to create / update', required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        json_device_parts = request.json['device_participant']
        if not isinstance(json_device_parts, list):
            json_device_parts = [json_device_parts]

        # Validate if we have an id
        for json_device_part in json_device_parts:
            if 'id_participant' not in json_device_part and 'id_device' not in json_device_part:
                return '', 400

            # Check if current user can modify the posted device
            if json_device_part['id_participant'] not in user_access.get_accessible_participants_ids(admin_only=True) \
                    or json_device_part['id_device'] not in user_access.get_accessible_devices_ids(admin_only=True):
                return gettext('Accès refusé'), 403

            # Check if already exists
            device_part = TeraDeviceParticipant.query_device_participant_for_participant_device(
                device_id=json_device_part['id_device'], participant_id=json_device_part['id_participant'])

            if device_part:
                json_device_part['id_device_participant'] = device_part.id_device_site
            else:
                json_device_part['id_device_participant'] = 0

            # Do the update!
            if json_device_part['id_device_participant'] > 0:
                # Already existing
                try:
                    TeraDeviceParticipant.update_device_participant(json_device_part['id_device_participant'],
                                                                    json_device_part)
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500
            else:
                try:
                    new_device_part = TeraDeviceParticipant()
                    new_device_part.from_json(json_device_part)
                    TeraDeviceParticipant.insert_device_participant(new_device_part)
                    # Update ID for further use
                    json_device_part['id_device_participant'] = new_device_part.id_device_participant
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500

        # TODO: Publish update to everyone who is subscribed to devices update...
        update_device_part = json_device_parts

        return jsonify(update_device_part)

    @auth.login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        device_part = TeraDeviceParticipant.get_device_participant_by_id(id_todel)
        if not device_part:
            return gettext('Non-trouvé'), 500

        if device_part.id_participant not in user_access.get_accessible_participants_ids(admin_only=True) or \
                device_part.id_device not in user_access.get_accessible_devices_ids(admin_only=True):
            return gettext('Accès refusé'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraDeviceParticipant.delete_device_participant(id_device_participant=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return gettext('Erreur base de données'), 500

        return '', 200
