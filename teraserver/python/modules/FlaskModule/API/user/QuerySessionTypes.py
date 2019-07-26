from flask import jsonify, session, request
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSessionType import TeraSessionType
from libtera.db.models.TeraSession import TeraSession
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext


class QuerySessionTypes(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.module = flaskModule

    @auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = reqparse.RequestParser()
        parser.add_argument('id_session_type', type=int, help='id_session')
        parser.add_argument('list', type=bool)

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

    @auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('session_type', type=str, location='json', help='Session type to create / update',
                            required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)
        # Using request.json instead of parser, since parser messes up the json!
        if 'session_type' not in request.json:
            return '', 400

        json_session_type = request.json['session_type']

        # Validate if we have an id
        if 'id_session_type' not in json_session_type:
            return '', 400

        # Check if current user can modify the posted group
        # User can modify or add a group if it has admin access to that project
        if json_session_type['id_session_type'] not in user_access.get_accessible_session_types_ids(admin_only=True) \
                and json_session_type['id_session_type'] > 0:
            return '', 403

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

        # TODO: Publish update to everyone who is subscribed to update...
        update_session_type = TeraSessionType.get_session_type_by_id(json_session_type['id_session_type'])

        return jsonify([update_session_type.to_json()])

    @auth.login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        session_type = TeraSessionType.get_session_type_by_id(id_todel)

        # Check if we are admin of all projects of that session_type
        for proj in session_type.session_type_projects:
            if user_access.get_project_role(proj.id_project) != "admin":
                return gettext('Impossible de supprimer - pas administrateur dans tous les projets de ce type.'), 403

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
