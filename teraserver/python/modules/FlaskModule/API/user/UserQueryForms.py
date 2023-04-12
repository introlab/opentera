from flask import jsonify, session
from flask_restx import Resource, reqparse
from modules.LoginModule.LoginModule import user_multi_auth, current_user
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.DatabaseModule.DBManager import DBManager
from flask_babel import gettext

from opentera.db.models.TeraSessionType import TeraSessionType
from opentera.db.models.TeraParticipantGroup import TeraParticipantGroup
from opentera.db.models.TeraParticipant import TeraParticipant

from opentera.forms.TeraUserForm import TeraUserForm
from opentera.forms.TeraSiteForm import TeraSiteForm
from opentera.forms.TeraDeviceForm import TeraDeviceForm
from opentera.forms.TeraProjectForm import TeraProjectForm
from opentera.forms.TeraParticipantGroupForm import TeraParticipantGroupForm
from opentera.forms.TeraParticipantForm import TeraParticipantForm
from opentera.forms.TeraSessionTypeForm import TeraSessionTypeForm
from opentera.forms.TeraSessionForm import TeraSessionForm
from opentera.forms.TeraDeviceTypeForm import TeraDeviceTypeForm
from opentera.forms.TeraDeviceSubTypeForm import TeraDeviceSubTypeForm
from opentera.forms.TeraUserGroupForm import TeraUserGroupForm
from opentera.forms.TeraServiceForm import TeraServiceForm
from opentera.forms.TeraServiceConfigForm import TeraServiceConfigForm
from opentera.forms.TeraVersionsForm import TeraVersionsForm
from opentera.forms.TeraSessionTypeConfigForm import TeraSessionTypeConfigForm
from opentera.forms.TeraTestTypeForm import TeraTestTypeForm

from opentera.redis.RedisRPCClient import RedisRPCClient
import json

get_parser = api.parser()
get_parser.add_argument(name='type', type=str, help='Data type of the required form. Currently, the '
                                                    'following data types are supported: \n '
                                                    'device\n'
                                                    'device_type\n'
                                                    'device_subtype\n'
                                                    'group\n'
                                                    'participant\n'
                                                    'project\n'
                                                    'service\n'
                                                    'service_config\n'
                                                    'session\n'
                                                    'session_type\n'
                                                    'session_type_config\n'
                                                    'site\n'
                                                    'test_type\n'
                                                    'user\n'
                                                    'user_group\n'
                                                    'versions\n'
                        )
get_parser.add_argument(name='id', type=int, help='Specific id of subitem to query. Used to provide context to the '
                                                  'returned form.')
get_parser.add_argument(name='id_project', type=int, help='Specific id_project used to limit arrays list in some forms')
get_parser.add_argument(name='id_site', type=int, help='Specific id_site used to limit arrays list in some forms')
get_parser.add_argument(name='key', type=str, help='Specific key of subitem to query. Used with service_config.')


class UserQueryForms(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Get json description of standard input form for the specified data type.',
             responses={200: 'Success',
                        400: 'Missing required parameter',
                        500: 'Unknown or unsupported data type'},
             params={'token': 'Secret token'})
    @api.expect(get_parser)
    @user_multi_auth.login_required
    def get(self):
        args = get_parser.parse_args()
        user_access = DBManager.userAccess(current_user)

        # if args['type'] == 'user_profile':
        #     return jsonify(TeraUserForm.get_user_profile_form())
        # If we have no arguments, return error

        if 'type' not in args:
            return gettext('Missing type'), 400

        if not any(args.values()):
            return gettext('Missing arguments'), 400

        if args['type'] == 'user':
            return TeraUserForm.get_user_form()

        if args['type'] == 'site':
            return TeraSiteForm.get_site_form()

        if args['type'] == 'device':
            return TeraDeviceForm.get_device_form()

        if args['type'] == 'project':
            return TeraProjectForm.get_project_form(accessible_sites=user_access.get_accessible_sites())

        if args['type'] == 'group':
            projects = []
            if args['id_site']:
                # Specific project id specified
                projects = user_access.query_projects_for_site(site_id=args['id_site'])
            elif not args['id'] or args['id'] not in user_access.get_accessible_groups_ids():
                # No specific group id specified
                projects = user_access.get_accessible_projects()
            else:
                # Specific group id specified
                group = TeraParticipantGroup.get_participant_group_by_id(args['id'])
                if group:
                    projects = user_access.query_projects_for_site(group.participant_group_project.id_site)

            return TeraParticipantGroupForm.get_participant_group_form(projects=projects)

        if args['type'] == 'participant':
            project_id = args['id_project']
            specific_participant_id = args['id']
            groups = []
            if project_id and project_id in user_access.get_accessible_projects_ids():
                groups = TeraParticipantGroup.get_participant_group_for_project(project_id=project_id)
            elif not specific_participant_id or \
                    specific_participant_id not in user_access.get_accessible_participants_ids():
                groups = user_access.get_accessible_groups()
            else:
                participant = TeraParticipant.get_participant_by_id(specific_participant_id)
                if participant:
                    groups = TeraParticipantGroup.get_participant_group_for_project(
                        participant.participant_project.id_project)

            return TeraParticipantForm.get_participant_form(groups=groups)

        if args['type'] == 'session_type':
            return TeraSessionTypeForm.get_session_type_form(services=user_access.get_accessible_services())

        if args['type'] == 'session_type_config':
            if not args['id']:
                return gettext('Missing session type id'), 400
            session_type: TeraSessionType = TeraSessionType.get_session_type_by_id(args['id'])
            if session_type:
                if session_type.session_type_category == TeraSessionType.SessionCategoryEnum.SERVICE.value and \
                        not session_type.session_type_service.service_system:
                    # External service - must query RPC call to get config form
                    rpc = RedisRPCClient(self.module.config.redis_config, timeout=5)
                    answer = rpc.call_service(session_type.session_type_service.service_key, 'session_type_config',
                                              json.dumps({'id_session_type': session_type.id_session_type}))
                    if answer:
                        return answer
                    else:
                        return gettext('No reply from service while querying session type config'), 408

                return TeraSessionTypeConfigForm.get_session_type_config_form(session_type)

        if args['type'] == 'session':
            return TeraSessionForm.get_session_form(user_access=user_access, specific_session_id=args['id'],
                                                    project_id=args['id_project'])

        if args['type'] == 'device_type':
            return TeraDeviceTypeForm.get_device_type_form()

        if args['type'] == 'device_subtype':
            return TeraDeviceSubTypeForm.get_device_subtype_form()

        if args['type'] == 'user_group':
            return TeraUserGroupForm.get_user_group_form()

        if args['type'] == 'service':
            return TeraServiceForm.get_service_form()

        if args['type'] == 'service_config':
            if not args['id'] and not args['key']:
                return TeraServiceConfigForm.get_service_config_form()

            service = None
            if args['id']:
                from opentera.db.models.TeraService import TeraService
                service = TeraService.get_service_by_id(args['id'])

            if args['key']:
                from opentera.db.models.TeraService import TeraService
                service = TeraService.get_service_by_key(args['key'])

            if not service:
                return gettext('Invalid service specified'), 400

            return TeraServiceConfigForm.get_service_config_config_form(service_key=service.service_key)

        if args['type'] == 'versions':
            return TeraVersionsForm.get_versions_form()

        if args['type'] == 'test_type':
            return TeraTestTypeForm.get_test_type_form(services=user_access.get_accessible_services())

        self.module.logger.log_error(self.module.module_name,
                                     UserQueryForms.__name__,
                                     'get', 400, 'Unknown form type: ' + args['type'])
        return gettext('Unknown form type: ') + args['type'], 400
