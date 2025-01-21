import sys
from flask import request
from flask_restx import Resource, reqparse, inputs

from sqlalchemy.exc import InvalidRequestError
from sqlalchemy import exc, inspect
from flask_babel import gettext

from modules.LoginModule.LoginModule import current_service, LoginModule
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.DatabaseModule.DBManager import DBManager
from modules.DatabaseModule.DBManagerTeraServiceAccess import DBManagerTeraServiceAccess
from opentera.db.models.TeraSessionTypeProject import TeraSessionTypeProject
from opentera.db.models.TeraSessionTypeSite import TeraSessionTypeSite
from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraProject import TeraProject



# Parser definition(s)
get_parser = api.parser()
get_parser.add_argument('id_project', type=int, help='Project ID to query associated session types from')
get_parser.add_argument('id_session_type', type=int, help='Session type ID to query associated projects from')

get_parser.add_argument('with_sites', type=inputs.boolean, help='Used with id_session_type. Also return site '
                                                                'information of the returned projects.')

post_parser = api.parser()
post_schema = api.schema_model('service_session_type_project', {'properties': TeraSessionTypeProject.get_json_schema(),
                                                             'type': 'object',
                                                             'location': 'json'})

delete_parser = reqparse.RequestParser()
delete_parser.add_argument('id', type=int, help='Specific session type - project association ID to delete. '
                                                'Be careful: this is not the session type or project ID, but the ID'
                                                ' of the association itself!', required=True)


class ServiceQuerySessionTypeProjects(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get session types that are associated with a project. Only one "ID" parameter required and '
                         'supported at once.',
             responses={200: 'Success - returns list of session types - projects association for this service',
                        400: 'Required parameter is missing (must have at least one id)',
                        500: 'Error when getting association'},
             params={'token': 'Access token'})
    @api.expect(get_parser)
    @LoginModule.service_token_or_certificate_required
    def get(self):
        """
        Get session types associated with a project
        """
        service_access : DBManagerTeraServiceAccess = DBManager.serviceAccess(current_service)
        args = get_parser.parse_args()

        session_type_projects : list[TeraSessionTypeProject] = []
        # If we have no arguments, return error
        if not any(args.values()):
            return gettext('Missing arguments'), 400

        if args['id_project']:
            if args['id_project'] in service_access.get_accessible_projects_ids():
                session_type_projects = TeraSessionTypeProject.get_sessions_types_for_project(args['id_project'])
        elif args['id_session_type']:
            if args['id_session_type'] in service_access.get_accessible_sessions_types_ids():
                session_type_projects = TeraSessionTypeProject.get_projects_for_session_type(args['id_session_type'])
        try:
            stp_list = []
            for stp in session_type_projects:
                json_stp = stp.to_json()
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
                                         ServiceQuerySessionTypeProjects.__name__,
                                         'get', 500, 'InvalidRequestError', e)
            return '', 500

    @api.doc(description='Create/update session-type - project association.',
             responses={200: 'Success',
                        403: 'Logged service can\'t modify association (not associated to project or session type)',
                        400: 'Badly formed JSON or missing fields in the JSON body',
                        500: 'Internal error occurred when saving association'},
             params={'token': 'Access token'})
    @api.expect(post_schema)
    @LoginModule.service_token_or_certificate_required
    def post(self):
        """
        Create / update session types -> project association
        """
        service_access : DBManagerTeraServiceAccess = DBManager.serviceAccess(current_service)

        accessible_projects_ids = service_access.get_accessible_projects_ids(admin_only=True)
        if 'session_type' in request.json:
            # We have a session_type. Get list of items
            if 'id_session_type' not in request.json['session_type']:
                return gettext('Missing id_session_type'), 400
            if 'projects' not in request.json['session_type']:
                return gettext('Missing projects'), 400
            id_session_type = request.json['session_type']['id_session_type']

            if id_session_type not in service_access.get_accessible_sessions_types_ids():
                return gettext("Forbidden"), 403

            # Get all current association for session type
            current_projects = TeraSessionTypeProject.get_projects_for_session_type(session_type_id=id_session_type)
            current_projects_ids = [proj.id_project for proj in current_projects]

            for proj_id in current_projects_ids:
                if proj_id not in accessible_projects_ids:
                    return gettext('Access denied to at least one project'), 403

            received_proj_ids = [proj['id_project'] for proj in request.json['session_type']['projects']]
            # Difference - we must delete sites not anymore in the list
            todel_ids = set(current_projects_ids).difference(received_proj_ids)
            # Also filter projects already there
            received_proj_ids = set(received_proj_ids).difference(current_projects_ids)
            try:
                for proj_id in todel_ids:
                    if proj_id in accessible_projects_ids:  # Don't remove from the list if not admin for that project!
                        TeraSessionTypeProject.delete_with_ids(session_type_id=id_session_type, project_id=proj_id,
                                                            autocommit=False)
                TeraSessionTypeProject.commit()
            except exc.IntegrityError as e:
                self.module.logger.log_warning(self.module.module_name, ServiceQuerySessionTypeProjects.__name__, 'delete',
                                               500, 'Integrity error', str(e))
                return gettext('Can\'t delete session type from project: please delete all sessions of that type in the '
                               'project before deleting.'), 500
            # Build projects association to add
            json_stp = [{'id_session_type': id_session_type, 'id_project': proj_id} for proj_id in received_proj_ids]
        elif 'project' in request.json:
            # We have a project. Get list of items
            if 'id_project' not in request.json['project']:
                return gettext('Missing project ID'), 400
            if 'sessions_types' not in request.json['project']:
                return gettext('Missing sessions_types'), 400
            id_project = request.json['project']['id_project']

            # Check if accessibles
            if id_project not in accessible_projects_ids:
                return gettext('Forbidden'), 403

            # Get all current association
            current_sessions_types = TeraSessionTypeProject.get_sessions_types_for_project(project_id=id_project)
            current_sessions_types_ids = [st.id_session_type for st in current_sessions_types]
            received_st_ids = [st['id_session_type'] for st in request.json['project']['sessions_types']]
            # Difference - we must delete types not anymore in the list
            todel_ids = set(current_sessions_types_ids).difference(received_st_ids)
            # Also filter types already there
            received_st_ids = set(received_st_ids).difference(current_sessions_types_ids)
            try:
                for st_id in todel_ids:
                    TeraSessionTypeProject.delete_with_ids(session_type_id=st_id, project_id=id_project, autocommit=False)
                TeraSessionTypeProject.commit()
            except exc.IntegrityError as e:
                self.module.logger.log_warning(self.module.module_name, ServiceQuerySessionTypeProjects.__name__, 'delete',
                                               500, 'Integrity error', str(e))
                return gettext('Can\'t delete session type from project: please delete all sessions of that type in the '
                               'project before deleting.'), 500
            # Build associations to add
            json_stp = [{'id_session_type': st_id, 'id_project': id_project} for st_id in received_st_ids]
        elif 'sessions_types_projects' in request.json:
            json_stp = request.json['sessions_types_projects']
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
                # At service level, if we have access to the project, we automatically associate the session type to its
                # site, since we know we are allowed to (prevent a call to another API)
                tsts: TeraSessionTypeSite = TeraSessionTypeSite()
                tsts.id_session_type = json_st['id_session_type']
                tsts.id_site = proj.id_site
                TeraSessionTypeSite.insert(tsts)

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
            if int(json_st['id_session_type_project']) == 0:
                try:
                    new_stp = TeraSessionTypeProject()
                    new_stp.from_json(json_st)
                    new_stp = TeraSessionTypeProject.insert(new_stp)
                    # Update ID for further use
                    json_st['id_session_type_project'] = new_stp.id_session_type_project
                except exc.SQLAlchemyError as e:

                    print(sys.exc_info())
                    self.module.logger.log_error(self.module.module_name,
                                                 ServiceQuerySessionTypeProjects.__name__,
                                                 'post', 500, 'Database error', str(e))
                    return gettext('Database error'), 500

        return json_stp

    @api.doc(description='Delete a specific session-type - project association.',
             responses={200: 'Success',
                        403: 'Logged service can\'t delete association (no access to session-type or project)',
                        400: 'Association not found (invalid id?)'},
             params={'token': 'Access token'})
    @api.expect(delete_parser)
    @LoginModule.service_token_or_certificate_required
    def delete(self):
        """
        Delete a specific session type -> project association
        """
        service_access = DBManager.serviceAccess(current_service)
        args = delete_parser.parse_args()
        id_todel = args['id']

        # Check if current service can delete
        stp : TeraSessionTypeProject = TeraSessionTypeProject.get_session_type_project_by_id(id_todel)
        if not stp:
            return gettext('Not found'), 400

        if stp.id_project not in service_access.get_accessible_projects_ids() or stp.id_session_type \
                not in service_access.get_accessible_sessions_types_ids():
            return gettext('Forbidden'), 403

        # If we are here, we are allowed to delete. Do so.
        try:
            TeraSessionTypeProject.delete(id_todel=id_todel)
        except exc.IntegrityError as e:
            # Causes that could make an integrity error when deleting:
            # - Associated project still have sessions with sessions of that type
            self.module.logger.log_warning(self.module.module_name, ServiceQuerySessionTypeProjects.__name__, 'delete',
                                           500, 'Integrity error', str(e))
            return gettext('Can\'t delete session type from project: please delete all sessions of that type in the project '
                           'before deleting.'), 500
        except exc.SQLAlchemyError as e:
            print(sys.exc_info())
            self.module.logger.log_error(self.module.module_name,
                                         ServiceQuerySessionTypeProjects.__name__,
                                         'delete', 500, 'Database error', e)
            return gettext('Database error'), 500

        return '', 200
