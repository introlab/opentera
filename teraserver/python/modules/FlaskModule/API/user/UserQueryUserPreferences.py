from flask import session, request
from flask_restx import Resource, reqparse, inputs
from flask_babel import gettext
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraUserPreference import TeraUserPreference
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from modules.DatabaseModule.DBManager import DBManager

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_user', type=int, help='ID of the user to get preference for')
get_parser.add_argument('app_tag', type=str, help='Tag of the application for which to get preferences')

post_schema = api.schema_model('user_preference', {'properties': TeraUserPreference.get_json_schema(),
                                                   'type': 'object',
                                                   'location': 'json'})


class UserQueryUserPreferences(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get user preferences. If no id_user field specified, returns preferences for current user.',
             responses={200: 'Success - returns list of user preferences',
                        400: 'Missing parameter or bad app_tag',
                        403: 'Forbidden access to that user.',
                        500: 'Database error'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()

        if not args['id_user']:
            # No id_user specified - query for current user!
            args['id_user'] = current_user.id_user
        else:
            if args['id_user'] not in user_access.get_accessible_users_ids():
                return gettext('Forbidden'), 403

        user_prefs = []
        if args['app_tag']:
            user_prefs = [TeraUserPreference.get_user_preferences_for_user_and_app(args['id_user'], args['app_tag'])]
        else:
            user_prefs = TeraUserPreference.get_user_preferences_for_user(args['id_user'])

        try:
            user_prefs_list = []
            for pref in user_prefs:
                if pref:
                    pref_json = pref.to_json()
                    user_prefs_list.append(pref_json)
            return user_prefs_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryUserPreferences.__name__,
                                         'get', 500, 'InvalidRequestError', str(e))
            return gettext('Invalid request'), 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create / update user preferences. Only one preference is allowed for a specific app_tag. '
                         'Preference will be overwritten if app_tag already exists for the user, and will be deleted '
                         'if empty or null. If id_user isn\'t set, will update current user preferences',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the user linked to that preference',
                        400: 'Badly formed JSON or missing fields(app_tag) in the JSON body',
                        500: 'Internal error occured when saving user preference'})
    def post(self):

        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        json_user_pref = request.json['user_preference']

        # Validate if we have all fields
        if 'id_user' not in json_user_pref:
            json_user_pref['id_user'] = current_user.id_user

        if 'user_preference_app_tag' not in json_user_pref:
            return gettext('Missing app tag'), 400

        if 'user_preference_preference' not in json_user_pref:
            json_user_pref['user_preference_preference'] = None

        # Check if current user can modify the posted preferences
        if json_user_pref['id_user'] not in user_access.get_accessible_users_ids(admin_only=True):
            return gettext('Forbidden'), 403

        # Do the update!
        try:
            TeraUserPreference.insert_or_update_or_delete_user_preference(user_id=json_user_pref['id_user'],
                                                                          app_tag=
                                                                          json_user_pref['user_preference_app_tag'],
                                                                          prefs=
                                                                          json_user_pref['user_preference_preference'])
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQueryUserPreferences.__name__,
                                         'post', 500, 'Database error', str(e))
            return gettext('Database error'), 500
        except ValueError as e:
            return str(e), 400

        updated_pref = TeraUserPreference.get_user_preferences_for_user_and_app(user_id=json_user_pref['id_user'],
                                                                                app_tag=
                                                                                json_user_pref[
                                                                                    'user_preference_app_tag'])
        if updated_pref:
            json_user_pref['id_user_preference'] = updated_pref.id_user_preference
            return updated_pref.to_json()

        # In case all was deleted
        return None
