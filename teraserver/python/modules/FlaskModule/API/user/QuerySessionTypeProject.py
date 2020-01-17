from flask import jsonify, session, request
from flask_restplus import Resource, reqparse
from modules.LoginModule.LoginModule import multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.models.TeraUser import TeraUser
from libtera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from libtera.db.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc
from flask_babel import gettext


class QuerySessionTypeProject(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)

    @multi_auth.login_required
    def get(self):
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        parser = reqparse.RequestParser()
        parser.add_argument('id_project', type=int)
        parser.add_argument('id_session_type', type=int)
        parser.add_argument('list', type=bool)

        args = parser.parse_args()

        session_type_projects = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Arguments manquants'), 400

        if args['id_project']:
            session_type_projects = user_access.query_session_types_for_project(project_id=args['id_project'])
        else:
            if args['id_session_type']:
                if args['id_session_type'] in user_access.get_accessible_session_types_ids():
                    session_type_projects = TeraSessionTypeProject.query_projects_for_session_type(
                        args['id_session_type'])
        try:
            stp_list = []
            for stp in session_type_projects:
                json_stp = stp.to_json()
                if args['list'] is None:
                    json_stp['session_type_name'] = stp.session_type_project_session_type.session_type_name
                    json_stp['project_name'] = stp.session_type_project_project.project_name
                stp_list.append(json_stp)

            return jsonify(stp_list)

        except InvalidRequestError:
            return '', 400

    @multi_auth.login_required
    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('session_type_project', type=str, location='json',
                            help='Session type project to create / update', required=True)

        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        # Using request.json instead of parser, since parser messes up the json!
        json_stps = request.json['session_type_project']
        if not isinstance(json_stps, list):
            json_stdts = [json_stps]

        # Validate if we have an id
        for json_stp in json_stps:
            if 'id_session_type' not in json_stp or 'id_project' not in json_stp:
                return '', 400

            # Check if current user can modify the posted information
            if json_stp['id_session_type'] not in user_access.get_accessible_session_types_ids(admin_only=True):
                return gettext('Acces refuse'), 403

            # Check if already exists
            stp = TeraSessionTypeProject.query_session_type_project_for_session_type_project(
                project_id=json_stp['id_project'], session_type_id=json_stp['id_session_type'])

            if stp:
                json_stp['id_session_type_project'] = stp.id_session_type_project
            else:
                json_stp['id_session_type_project'] = 0

            # Do the update!
            if json_stp['id_session_type_project'] > 0:
                # Already existing
                try:
                    TeraSessionTypeProject.update(json_stp['id_session_type_project'], json_stp)
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500
            else:
                try:
                    new_stp = TeraSessionTypeProject()
                    new_stp.from_json(json_stp)
                    TeraSessionTypeProject.insert(new_stp)
                    # Update ID for further use
                    json_stp['id_session_type_project'] = new_stp.id_session_type_project
                except exc.SQLAlchemyError:
                    import sys
                    print(sys.exc_info())
                    return '', 500

        # TODO: Publish update to everyone who is subscribed to devices update...
        update_stp = json_stps

        return jsonify(update_stp)

    @multi_auth.login_required
    def delete(self):
        parser = reqparse.RequestParser()
        parser.add_argument('id', type=int, help='ID to delete', required=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
        user_access = DBManager.userAccess(current_user)

        args = parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        stp = TeraSessionTypeProject.get_session_type_project_by_id(id_todel)
        if not stp:
            return gettext('Non-trouvé'), 500

        if stp.id_session_type not in user_access.get_accessible_session_types_ids(admin_only=True):
            return gettext('Accès refusé'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraSessionTypeProject.delete(id_todel=id_todel)
        except exc.SQLAlchemyError:
            import sys
            print(sys.exc_info())
            return gettext('Erreur base de données'), 500

        return '', 200
