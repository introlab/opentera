from flask import jsonify, session, request
from flask_restplus import Resource, reqparse, fields, inputs
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext


# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_device', type=int, help='ID of the device from which to request all associated participants'
                        )
get_parser.add_argument('id_participant', type=int, help='ID of the participant from which to request all associated '
                                                         'devices')
get_parser.add_argument('id_site', type=int, help='ID of the site from which to get all devices and associated '
                                                  'participants')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information (ids only)')

post_parser = reqparse.RequestParser()
post_parser.add_argument('device_participant', type=str, location='json',
                         help='Device participant to create / update', required=True)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific device-participant association ID to delete. Be careful: this'
                                                ' is not the device or the participant ID, but the ID of the '
                                                'association itself!', required=True)


model = api.model('QueryDeviceParticipants', {
    'participant_name': fields.String,
    'device_name': fields.String,
    'user_token': fields.String
})


class QueryDeviceParticipants(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get devices that are related to a participant. Only one "ID" parameter required and supported'
                         ' at once.',
             responses={200: 'Success - returns list of devices - participants association',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error occured when loading devices for participant'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = get_parser.parse_args()

        device_part = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Arguments manquants'), 400

        if args['id_device']:
            if args['id_device'] in user_access.get_accessible_devices_ids():
                device_part = TeraDeviceParticipant.query_participants_for_device(device_id=args['id_device'])
        elif args['id_participant']:
            if args['id_participant'] in user_access.get_accessible_participants_ids():
                device_part = TeraDeviceParticipant.query_devices_for_participant(
                    participant_id=args['id_participant'])
        elif args['id_site']:
            # Get devices and participants for that specific site
            device_part = user_access.query_device_participants_for_site(site_id=args['id_site'])

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
            return '', 500

    @user_multi_auth.login_required
    @api.expect(post_parser)
    @api.doc(description='Create/update devices associated with a participant.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify device association',
                        400: 'Badly formed JSON or missing fields(id_participant or id_device) in the JSON body',
                        500: 'Internal error occured when saving device association'})
    def post(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        json_device_parts = request.json['device_participant']
        if not isinstance(json_device_parts, list):
            json_device_parts = [json_device_parts]

        # Validate if we have an id
        for json_device_part in json_device_parts:
            if 'id_participant' not in json_device_part or 'id_device' not in json_device_part:
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
                    TeraDeviceParticipant.update_(json_device_part['id_device_participant'], json_device_part)
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500
            else:
                try:
                    new_device_part = TeraDeviceParticipant()
                    new_device_part.from_json(json_device_part)
                    TeraDeviceParticipant.insert(new_device_part)
                    # Update ID for further use
                    json_device_part['id_device_participant'] = new_device_part.id_device_participant
                    json_device_part['participant_name'] = new_device_part.device_participant_participant.\
                        participant_name
                    json_device_part['device_name'] = new_device_part.device_participant_device.device_name
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500

        # TODO: Publish update to everyone who is subscribed to devices update...
        update_device_part = json_device_parts

        return jsonify(update_device_part)

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific device-participant association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete device association',
                        500: 'Device-participant association not found or database error.'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
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
            TeraDeviceParticipant.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return gettext('Erreur base de données'), 500

        return '', 200
