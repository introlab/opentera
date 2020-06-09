from flask import session
from flask_restx import Resource
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraAsset import TeraAsset

from sqlalchemy import exc
from modules.DatabaseModule.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_asset', type=int, help='Specific ID of asset to query information.')
get_parser.add_argument('id_device', type=int, help='ID of the device from which to request all assets')
get_parser.add_argument('id_session', type=int, help='ID of session from which to request all assets')
get_parser.add_argument('id_participant', type=int, help='ID of participant from which to request all assets')
get_parser.add_argument('service_uuid', type=str, help='Service UUID from which to request all assets')

delete_parser = api.parser()
delete_parser.add_argument('id', type=int, help='Specific asset ID to delete', required=True)


class UserQueryAssets(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get asset information. Only one of the ID parameter is supported at once',
             responses={200: 'Success - returns list of assets',
                        500: 'Required parameter is missing',
                        403: 'Logged user doesn\'t have permission to access the requested data'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = get_parser.parse_args()

        # If we have no arguments, don't do anything!
        if not any(args.values()):
            return '', 500
        elif args['id_device']:
            if args['id_device'] not in user_access.get_accessible_devices_ids():
                return '', 403
            assets = TeraAsset.get_assets_for_device(device_id=args['id_device'])
        elif args['id_session']:
            if not user_access.query_session(session_id=args['id_session']):
                return '', 403
            assets = TeraAsset.get_assets_for_session(session_id=args['id_session'])
        elif args['id_participant']:
            if args['id_participant'] not in user_access.get_accessible_participants_ids():
                return '', 403
            assets = TeraAsset.get_assets_for_participant(part_id=args['id_participant'])
        elif args['id_asset']:
            assets = [TeraAsset.get_asset_by_id(args['id_asset'])]
            if assets[0] is not None:
                if assets[0].id_device is not None and assets[0].id_device not in \
                        user_access.get_accessible_devices_ids():
                    return '', 403
                if not user_access.query_session(session_id=assets[0].id_session):
                    return '', 403
        elif args['service_uuid']:
            assets = user_access.query_assets_for_service(args['service_uuid'])

        assets_list = []
        for asset in assets:
            asset_json = asset.to_json()
            assets_list.append(asset_json)

        return assets_list

    @user_multi_auth.login_required
    @api.doc(description='Delete asset.',
             responses={200: 'Success - asset deleted',
                        500: 'Database error occurred',
                        403: 'Logged user doesn\'t have permission to delete the requested asset (must be an user of'
                             'the related project)'})
    @api.expect(delete_parser)
    def delete(self):
        from libtera.db.models.TeraSession import TeraSession
        from libtera.db.models.TeraParticipant import TeraParticipant
        parser = delete_parser
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Get data in itself to validate we can delete it
        asset = TeraAsset.get_asset_by_id(id_todel)

        # Get accessible projects list
        projects_ids = user_access.get_accessible_participants_ids()

        # Check if current user can delete
        if len(TeraAsset.query.join(TeraSession).join(TeraSession.session_participants)
                       .filter(TeraParticipant.id_project.in_(projects_ids)).all()) == 0:
            return '', 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraAsset.delete(id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200

