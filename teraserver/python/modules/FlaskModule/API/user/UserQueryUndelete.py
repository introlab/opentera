from flask_restx import Resource
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_session', type=int, help='ID of the session to undelete')
get_parser.add_argument('id_asset', type=int, help='ID of the asset to undelete')


class UserQueryUndelete(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Undelete an item if that item can be undeleted. Only one ID is supported at once',
             responses={200: 'Success - item was undeleted',
                        400: 'Required parameter is missing',
                        401: 'Requested item not found or is undeletable',
                        403: 'Access level insufficient to access that API or the item to undelete',
                        500: 'Database error'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        """
        Undelete an item
        """
        if not current_user.user_superadmin:
            return gettext('No access to this API'), 403

        # For now, only super admins can undelete, so no need to check for access to the item to undelete
        # This should be done when / if that API is opened to site admins (for example)
        args = get_parser.parse_args()

        object_to_undelete = None
        if args['id_session']:
            from opentera.db.models.TeraSession import TeraSession
            object_to_undelete = TeraSession.get_session_by_id(ses_id=args['id_session'], with_deleted=True)

        if args['id_asset']:
            from opentera.db.models.TeraAsset import TeraAsset
            object_to_undelete = TeraAsset.get_asset_by_id(asset_id=args['id_asset'], with_deleted=True)

        if not object_to_undelete:
            return gettext('Item to undelete not found'), 401

        if not getattr(object_to_undelete, 'undelete', None):
            return gettext('Item can\'t be undeleted'), 401

        if not object_to_undelete.deleted_at:
            return gettext('Item isn\'t deleted'), 401

        # Do the actual undelete
        object_to_undelete.undelete()
        object_to_undelete.db().session.commit()

        return '', 200






