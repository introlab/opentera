from flask import request
from flask_restx import Resource, reqparse, inputs
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraProject import TeraProject
from modules.DatabaseModule.DBManager import DBManager
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc, inspect
from flask_babel import gettext

# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_project', type=int, help='Project ID to query associated session types from')
get_parser.add_argument('id_session_type', type=int, help='Session type ID to query associated projects from')

get_parser.add_argument('with_projects', type=inputs.boolean, help='Used with id_session_type. Also return projects '
                                                                   'that don\'t have any association with that type')
get_parser.add_argument('with_session_type', type=inputs.boolean, help='Used with id_project. Also return types that '
                                                                       'don\'t have any association with that project')
get_parser.add_argument('with_sites', type=inputs.boolean, help='Used with id_session_type. Also return site '
                                                                'information of the returned projects.')

get_parser.add_argument('list', type=inputs.boolean, help='Flag that limits the returned data to minimal information '
                                                          '(ids only)')

post_parser = api.parser()
post_schema = api.schema_model('user_session_type_project', {'properties': TeraSessionTypeProject.get_json_schema(),
                                                             'type': 'object',
                                                             'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific device-type - project association ID to delete. '
                                                'Be careful: this is not the session-type or project ID, but the ID'
                                                ' of the association itself!', required=True)


class UserQuerySessionTypeProjects(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get devices types that are associated with a project. Only one "ID" parameter required and '
                         'supported at once.',
             responses={200: 'Success - returns list of devices-types - projects association',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error when getting association'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        user_access = DBManager.userAccess(current_user)
        args = get_parser.parse_args()

        session_type_projects = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        if args['id_project']:
            if args['id_project'] in user_access.get_accessible_projects_ids():
                session_type_projects = user_access.query_session_types_for_project(project_id=args['id_project'],
                                                                                    include_other_session_types=
                                                                                    args['with_session_type'])
        elif args['id_session_type']:
            if args['id_session_type'] in user_access.get_accessible_session_types_ids():
                session_type_projects = user_access.query_projects_for_session_type(session_type_id=
                                                                                    args['id_session_type'],
                                                                                    include_other_projects=
                                                                                    args['with_projects'])
        try:
            stp_list = []
            for stp in session_type_projects:
                json_stp = stp.to_json()
                if args['list'] is None:
                    obj_type = inspect(stp)
                    if not obj_type.transient:
                        json_stp['session_type_name'] = stp.session_type_project_session_type.session_type_name
                        json_stp['project_name'] = stp.session_type_project_project.project_name
                        if args['with_sites']:
                            json_stp['id_site'] = stp.session_type_project_project.id_site
                            json_stp['site_name'] = stp.session_type_project_project.project_site.site_name
                    else:
                        # Temporary object, a not-committed object, result of listing projects not associated to a
                        # session type.
                        if stp.id_session_type:
                            st: TeraSessionType = TeraSessionType.get_session_type_by_id(stp.id_session_type)
                            json_stp['session_type_name'] = st.session_type_name
                        else:
                            json_stp['session_type_name'] = None
                        if stp.id_project:
                            proj = TeraProject.get_project_by_id(stp.id_project)
                            json_stp['project_name'] = proj.project_name
                            if args['with_sites']:
                                json_stp['id_site'] = proj.id_site
                                json_stp['site_name'] = proj.project_site.site_name
                        else:
                            json_stp['project_name'] = None
                stp_list.append(json_stp)

            return stp_list

        except InvalidRequestError as e:
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySessionTypeProjects.__name__,
                                         'get', 500, 'InvalidRequestError', e)
            return '', 500

    @api.doc(description='Create/update session-type - project association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t modify association (session type must be accessible from project '
                             'access)',
                        400: 'Badly formed JSON or missing fields(id_project or id_session_type) in the JSON body',
                        500: 'Internal error occurred when saving association'},
             params={'token': 'Secret token'})
    @api.expect(post_schema)
    @user_multi_auth.login_required
    def post(self):
        user_access = DBManager.userAccess(current_user)

        accessible_projects_ids = user_access.get_accessible_projects_ids(admin_only=True)
        if 'session_type' in request.json:
            # We have a session_type. Get list of items
            if 'id_session_type' not in request.json['session_type']:
                return gettext('Missing id_session_type'), 400
            if 'projects' not in request.json['session_type']:
                return gettext('Missing projects'), 400
            id_session_type = request.json['session_type']['id_session_type']

            if id_session_type not in user_access.get_accessible_session_types_ids(admin_only=True):
                return gettext("Access denied"), 403

            # Get all current association for session type
            current_projects = TeraSessionTypeProject.get_projects_for_session_type(session_type_id=id_session_type)
            current_projects_ids = [proj.id_project for proj in current_projects]
            received_proj_ids = [proj['id_project'] for proj in request.json['session_type']['projects']]
            # Difference - we must delete sites not anymore in the list
            todel_ids = set(current_projects_ids).difference(received_proj_ids)
            # Also filter projects already there
            received_proj_ids = set(received_proj_ids).difference(current_projects_ids)
            for proj_id in todel_ids:
                if proj_id in accessible_projects_ids:  # Don't remove from the list if not admin for that project!
                    TeraSessionTypeProject.delete_with_ids(session_type_id=id_session_type, project_id=proj_id)
            # Build projects association to add
            json_stp = [{'id_session_type': id_session_type, 'id_project': proj_id} for proj_id in received_proj_ids]
        elif 'project' in request.json:
            # We have a project. Get list of items
            if 'id_project' not in request.json['project']:
                return gettext('Missing project ID'), 400
            if 'sessiontypes' not in request.json['project']:
                return gettext('Missing session types'), 400
            id_project = request.json['project']['id_project']

            # Check if admin for that project
            if user_access.get_project_role(project_id=id_project) != 'admin':
                return gettext('Access denied'), 403

            # Get all current association for site
            current_session_types = TeraSessionTypeProject.get_sessions_types_for_project(project_id=id_project)
            current_session_types_ids = [st.id_session_type for st in current_session_types]
            received_st_ids = [st['id_session_type'] for st in request.json['project']['sessiontypes']]
            # Difference - we must delete types not anymore in the list
            todel_ids = set(current_session_types_ids).difference(received_st_ids)
            # Also filter session types already there
            received_st_ids = set(received_st_ids).difference(current_session_types_ids)
            for st_id in todel_ids:
                TeraSessionTypeProject.delete_with_ids(session_type_id=st_id, project_id=id_project)
            # Build associations to add
            json_stp = [{'id_session_type': st_id, 'id_project': id_project} for st_id in received_st_ids]
        elif 'session_type_project' in request.json:
            json_stp = request.json['session_type_project']
            if not isinstance(json_stp, list):
                json_stp = [json_stp]
        else:
            return gettext('Unknown format'), 400

        # Validate if we have an id and access
        for json_st in json_stp:
            if 'id_session_type' not in json_st or 'id_project' not in json_st:
                return gettext('Badly formatted request'), 400

            if json_st['id_project'] not in accessible_projects_ids:
                return gettext('Forbidden'), 403

            proj = TeraProject.get_project_by_id(json_st['id_project'])
            site_access = TeraSessionTypeSite.get_session_type_site_for_session_type_and_site(site_id=proj.id_site,
                                                                                              session_type_id=
                                                                                              json_st['id_session_type']
                                                                                              )
            if not site_access:
                return gettext('At least one session type is not associated to the site of its project'), 403

        for json_st in json_stp:
            if 'id_session_type_project' not in json_st:
                # Check if already exists
                st = TeraSessionTypeProject.\
                    get_session_type_project_for_session_type_project(project_id=int(json_st['id_project']),
                                                                      session_type_id=int(json_st['id_session_type']))
                if st:
                    json_st['id_session_type_project'] = st.id_session_type_project
                else:
                    json_st['id_session_type_project'] = 0

            # Do the update!
            if int(json_st['id_session_type_project']) > 0:
                # Already existing
                # try:
                #     TeraSessionTypeProject.update(int(json_st['id_session_type_project']), json_st)
                # except exc.SQLAlchemyError as e:
                #     import sys
                #     print(sys.exc_info())
                #     self.module.logger.log_error(self.module.module_name,
                #                                  UserQuerySessionTypeProjects.__name__,
                #                                  'post', 500, 'Database error', str(e))
                #     return gettext('Database error'), 500
                pass
            else:
                try:
                    new_stp = TeraSessionTypeProject()
                    new_stp.from_json(json_st)
                    new_stp = TeraSessionTypeProject.insert(new_stp)
                    # Update ID for further use
                    json_st['id_session_type_project'] = new_stp.id_session_type_project
                except exc.SQLAlchemyError as e:
                    import sys
                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 UserQuerySessionTypeProjects.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500

        return json_stp

    @api.doc(description='Delete a specific session-type - project association.',
             responses={200: 'Success',
                        403: 'Logged user can\'t delete association (no access to session-type or project)',
                        400: 'Association not found (invalid id?)'},
             params={'token': 'Secret token'})
    @api.expect(delete_parser)
    @user_multi_auth.login_required
    def delete(self):
        user_access = DBManager.userAccess(current_user)
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if current user can delete
        stp = TeraSessionTypeProject.get_session_type_project_by_id(id_todel)
        if not stp:
            return gettext('Not found'), 400

        if stp.id_session_type not in user_access.get_accessible_session_types_ids(admin_only=True):
            return gettext('Access denied'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraSessionTypeProject.delete(id_todel=id_todel)
        except exc.IntegrityError as e:
            # Causes that could make an integrity error when deleting:
            # - Associated project still have sessions of that type
            self.module.logger.log_warning(self.module.module_name, UserQuerySessionTypeProjects.__name__, 'delete',
                                           500, 'Integrity error', str(e))
            return gettext('Can\'t delete session type from project: please delete all sessions of that type in the '
                           'project before deleting.'), 500
        except exc.SQLAlchemyError as e:
            import sys
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         UserQuerySessionTypeProjects.__name__,
                                         'delete', 500, 'Database error', e)
            return gettext('Database error'), 500

        return '', 200
