from flask import jsonify, session, request
from flask_restplus import Resource, reqparse
from modules.LoginModule.LoginModule import multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraDeviceSite import TeraDeviceSite
from libtera.db.models.TeraDeviceParticipant import TeraDeviceParticipant
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_device', type=int, help='ID of the device from which to request all associated sites'
                        )
get_parser.add_argument('id_site', type=int, help='ID of the site from which to get all associated devices')
get_parser.add_argument('list', type=bool, help='Flag that limits the returned data to minimal information (ids only)')

post_parser = reqparse.RequestParser()
post_parser.add_argument('device_site', type=str, location='json',
                         help='Device site association to create / update', required=True)

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific device-site association ID to delete. Be careful: this'
                                                ' is not the device or the site ID, but the ID of the '
                                                'association itself!', required=True)


class QueryDeviceSites(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get devices that are related to a site. Only one "ID" parameter required and supported'
                         ' at once.',
             responses={200: 'Success - returns list of devices - sites association',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error occured when loading devices for sites'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()

        device_site = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Arguments manquants'), 400

        if args['id_device']:
            if args['id_device'] in user_access.get_accessible_devices_ids():
                device_site = TeraDeviceSite.query_sites_for_device(device_id=args['id_device'])
        else:
            if args['id_site']:
                if args['id_site'] in user_access.get_accessible_sites_ids():
                    device_site = TeraDeviceSite.query_devices_for_site(site_id=args['id_site'])
        try:
            device_site_list = []
            for ds in device_site:
                json_ds = ds.to_json()
                if args['list'] is None:
                    json_ds['site_name'] = ds.device_site_site.site_name
                    json_ds['device_name'] = ds.device_site_device.device_name
                    json_ds['device_available'] = not ds.device_site_device.device_participants
                device_site_list.append(json_ds)

            return jsonify(device_site_list)

        except InvalidRequestError:
            return '', 500

    @multi_auth.login_required
    @api.expect(post_parser)
    @api.doc(description='Create/update devices associated with a site.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify device association',
                        400: 'Badly formed JSON or missing fields(id_site or id_device) in the JSON body',
                        500: 'Internal error occured when saving device association'})
    def post(self):
        parser = post_parser

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        json_device_sites = request.json['device_site']
        if not isinstance(json_device_sites, list):
            json_device_sites = [json_device_sites]

        # Validate if we have an id
        for json_device_site in json_device_sites:
            if 'id_device' not in json_device_site or 'id_site' not in json_device_site:
                return '', 400

            # Check if current user can modify the posted device
            if json_device_site['id_site'] not in user_access.get_accessible_sites_ids(admin_only=True) or \
                    json_device_site['id_device'] not in user_access.get_accessible_devices_ids(admin_only=True):
                return gettext('Accès refusé'), 403

            # Check if already exists
            device_site = TeraDeviceSite.query_device_site_for_device_site(device_id=json_device_site['id_device'],
                                                                           site_id=json_device_site['id_site'])
            if device_site:
                json_device_site['id_device_site'] = device_site.id_device_site
            else:
                json_device_site['id_device_site'] = 0

            # Do the update!
            if json_device_site['id_device_site'] > 0:
                # Already existing
                try:
                    TeraDeviceSite.update(json_device_site['id_device_site'], json_device_site)
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500
            else:
                try:
                    new_device_site = TeraDeviceSite()
                    new_device_site.from_json(json_device_site)
                    TeraDeviceSite.insert(new_device_site)
                    # Update ID for further use
                    json_device_site['id_device_site'] = new_device_site.id_device_site
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500

        # TODO: Publish update to everyone who is subscribed to devices update...
        update_device_site = json_device_sites

        return jsonify(update_device_site)

    @multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific device-site association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete device association',
                        500: 'Device-site association not found or database error.'})
    def delete(self):
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        device_site = TeraDeviceSite.get_device_site_by_id(id_todel)
        if not device_site:
            return gettext('Non-trouvé'), 500

        if device_site.id_site not in user_access.get_accessible_sites_ids(admin_only=True) or device_site.id_device \
                not in user_access.get_accessible_devices_ids(admin_only=True):
            return gettext('Accès refusé'), 403

        # Delete participants associated with that device, since the site was changed.
        associated_participants = TeraDeviceParticipant.query_participants_for_device(device_id=device_site.id_device)
        for part in associated_participants:
            if part.device_participant_participant.participant_participant_group.participant_group_project.\
                    project_site.id_site == device_site.id_site:
                device_part = TeraDeviceParticipant.query_device_participant_for_participant_device(
                    device_id=device_site.id_device, participant_id=part.id_participant)
                if device_part:
                    TeraDeviceParticipant.delete(device_part.id_device_participant)

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraDeviceSite.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return gettext('Erreur base de données'), 500

        return '', 200
