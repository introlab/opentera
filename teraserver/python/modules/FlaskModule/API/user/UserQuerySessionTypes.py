from flask import jsonify, session, request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSessionType import TeraSessionType
from libtera.db.models.TeraSession import TeraSession
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_session_type', type=int, help='ID of the session type to query')
get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information')

# post_parser = reqparse.RequestParser()
# post_parser.add_argument('session_type', type=str, location='json', help='Session type to create / update',
#                          required=True)

post_schema = api.schema_model('user_session_type', {'properties': TeraSessionType.get_json_schema(),
                                                     'type': 'object',
                                                     'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Session type ID to delete', required=True)


class UserQuerySessionTypes(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get session type information. If no id_session_type specified, returns all available '
                         'session types',
             responses={200: 'Success - returns list of session types',
                        500: 'Database error'})
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = get_parser

        args = parser.parse_args()

        session_types = []

        if args['id_session_type']:
            session_types = [user_access.query_session_type_by_id(args['id_session_type'])]
        else:
            session_types = user_access.get_accessible_session_types()

        try:
            sessions_types_list = []
            for st in session_types:
                if args['list'] is None:
                    st_json = st.to_json()
                    sessions_types_list.append(st_json)
                else:
                    st_json = st.to_json(minimal=True)
                    sessions_types_list.append(st_json)

            return jsonify(sessions_types_list)

        except InvalidRequestError:
            return '', 500

    @user_multi_auth.login_required
    @api.expect(post_schema)
    @api.doc(description='Create / update session type. id_session_type must be set to "0" to create a new '
                         'type. A session type can be created/modified if the user has access to a related session type'
                         'project.',
             responses={200: 'Success',
                        403: 'Logged user can\'t create/update the specified session type',
                        400: 'Badly formed JSON or missing field(id_session_type) in the JSON body',
                        500: 'Internal error when saving session type'})
    def post(self):
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        if 'session_type' not in request.json:
            return gettext('Missing session_type'), 400

        json_session_type = request.json['session_type']

        # Validate if we have an id
        if 'id_session_type' not in json_session_type:
            return gettext('Missing id_session_type'), 400

        # Check if current user can modify the posted type
        if json_session_type['id_session_type'] > 0:
            if json_session_type['id_session_type'] not in \
                    user_access.get_accessible_session_types_ids(admin_only=True):
                return gettext('Forbidden'), 403
        else:
            # Allows session type creation if the user is at least admin in one project
            if len(user_access.get_accessible_projects(admin_only=True)) == 0:
                return gettext('User must be admin in at least one site to create new type'), 403

        # Check if we have a session type of type "service" and, if there's changes in the id_service, it won't break
        # any project association
        session_type_category = None
        if 'session_type_category' in json_session_type:
            session_type_category = TeraSessionType.SessionCategoryEnum(int(json_session_type['session_type_category']))

        session_type = None
        if json_session_type['id_session_type'] > 0 and not session_type_category:
            session_type = TeraSessionType.get_session_type_by_id(json_session_type['id_session_type'])
            session_type_category = session_type.session_type_category

        if session_type_category == TeraSessionType.SessionCategoryEnum.SERVICE:
            # Check if we have a service id associated
            current_service_id = None
            if 'id_service' in json_session_type:
                # Get service id directly from the request
                current_service_id = json_session_type['id_service']
            else:
                # Get service id from the exiting session type
                if session_type:
                    current_service_id = session_type.id_service
            if not current_service_id:
                return gettext('Missing id_service for session type of type service'), 400

        st_projects_ids = []
        update_st_projects = False
        if 'session_type_projects' in json_session_type:
            if json_session_type['id_session_type'] > 0:
                return gettext('Session type projects may be specified with that API only on a new session type. Use '
                               '"sessiontypeproject" instead'), 400
            session_type_projects = json_session_type.pop('session_type_projects')
            # Check if the current user is project admin in all of those projects
            st_projects_ids = [project['id_project'] for project in session_type_projects]

            for project_id in st_projects_ids:
                if user_access.get_project_role(project_id) != 'admin':
                    return gettext('No project admin access for at a least one project in the list'), 403
            update_st_projects = True

        # Do the update!
        if json_session_type['id_session_type'] > 0:
            # Already existing
            try:
                TeraSessionType.update(json_session_type['id_session_type'], json_session_type)
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500
        else:
            # New
            try:
                new_st = TeraSessionType()
                new_st.from_json(json_session_type)
                TeraSessionType.insert(new_st)
                # Update ID for further use
                json_session_type['id_session_type'] = new_st.id_session_type
            except exc.SQLAlchemyError:
                import sys
                print(sys.exc_info())
                return '', 500

        update_session_type = TeraSessionType.get_session_type_by_id(json_session_type['id_session_type'])

        # Update session type projects, if needed
        if update_st_projects:
            from libtera.db.models.TeraProject import TeraProject
            update_session_type.session_type_projects = [TeraProject.get_project_by_id(project_id)
                                                         for project_id in st_projects_ids]
            update_session_type.commit()

        return [update_session_type.to_json()]

    @user_multi_auth.login_required
    @api.expect(delete_parser)
    @api.doc(description='Delete a specific session type',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete session type (no admin access to project related to that type '
                             'or sessions of that type exists in the system somewhere)',
                        500: 'Database error.'})
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        session_type = TeraSessionType.get_session_type_by_id(id_todel)

        # Check if we are admin of all projects of that session_type
        if len(session_type.session_type_projects) > 0:
            for proj in session_type.session_type_projects:
                if user_access.get_project_role(proj.id_project) != "admin":
                    return gettext('Impossible de supprimer - pas administrateur dans tous les projets de ce type.'), \
                           403
        else:
            # No project right now for that session type - must at least project admin somewhere to delete
            if len(user_access.get_accessible_projects(admin_only=True)) == 0:
                return gettext('Unable to delete - not admin in at least one project'), 403

        # Check if there's some sessions that are using that session type. If so, we must not delete!
        if len(TeraSession.get_sessions_for_type(id_todel)) > 0:
            return gettext('Impossible de supprimer - des seances de ce type existent.'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraSessionType.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return 'Database error', 500

        return '', 200
