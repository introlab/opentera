from flask import jsonify, session
from flask_restx import Resource, reqparse
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from modules.DatabaseModule.DBManager import DBManager
from flask_babel import gettext

from libtera.db.models.TeraUser import TeraUser

from libtera.forms.TeraUserForm import TeraUserForm
from libtera.forms.TeraSiteForm import TeraSiteForm
from libtera.forms.TeraDeviceForm import TeraDeviceForm
from libtera.forms.TeraProjectForm import TeraProjectForm
from libtera.forms.TeraParticipantGroupForm import TeraParticipantGroupForm
from libtera.forms.TeraParticipantForm import TeraParticipantForm
from libtera.forms.TeraSessionTypeForm import TeraSessionTypeForm
from libtera.forms.TeraSessionForm import TeraSessionForm
from libtera.forms.TeraDeviceSubTypeForm import TeraDeviceSubTypeForm
from libtera.forms.TeraUserGroupForm import TeraUserGroupForm
from libtera.forms.TeraServiceForm import TeraServiceForm
from libtera.forms.TeraServiceConfigForm import TeraServiceConfigForm

get_parser = api.parser()
get_parser.add_argument(name='type', type=str, help='Data type of the required form. Currently, the '
                                                    'following data types are supported: \n '
                                                    'device\n'
                                                    'device_subtype\n'
                                                    'group\n'
                                                    'participant\n'
                                                    'project\n'
                                                    'service\n'
                                                    'service_config\n'
                                                    'session\n'
                                                    'session_type\n'
                                                    'site\n'
                                                    'user\n'
                                                    'user_group\n'
                        )
get_parser.add_argument(name='id', type=int, help='Specific id of subitem to query. Used with service_config.')


class UserQueryForms(Resource):

    def __init__(self, _api, *args, **kwargs):
        self.module = kwargs.get('flaskModule', None)
        Resource.__init__(self, _api, *args, **kwargs)

    @user_multi_auth.login_required
    @api.expect(get_parser)
    @api.doc(description='Get json description of standard input form for the specified data type.',
             responses={200: 'Success',
                        400: 'Missing required parameter',
                        500: 'Unknown or unsupported data type'})
    def get(self):
        parser = get_parser
        args = parser.parse_args()
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        # if args['type'] == 'user_profile':
        #     return jsonify(TeraUserForm.get_user_profile_form())

        if args['type'] == 'user':
            return jsonify(TeraUserForm.get_user_form(user_access=user_access))

        if args['type'] == 'site':
            return jsonify(TeraSiteForm.get_site_form())

        if args['type'] == 'device':
            return jsonify(TeraDeviceForm.get_device_form(user_access=user_access))

        if args['type'] == 'project':
            return jsonify(TeraProjectForm.get_project_form(user_access=user_access))

        if args['type'] == 'group':
            return jsonify(TeraParticipantGroupForm.get_participant_group_form(user_access=user_access))

        if args['type'] == 'participant':
            return jsonify(TeraParticipantForm.get_participant_form(user_access=user_access))

        if args['type'] == 'session_type':
            return jsonify(TeraSessionTypeForm.get_session_type_form(user_access=user_access))

        if args['type'] == 'session':
            return jsonify(TeraSessionForm.get_session_form(user_access=user_access))

        if args['type'] == 'device_subtype':
            return jsonify(TeraDeviceSubTypeForm.get_device_subtype_form(user_access=user_access))

        if args['type'] == 'user_group':
            return TeraUserGroupForm.get_user_group_form(user_access=user_access)

        if args['type'] == 'service':
            return TeraServiceForm.get_service_form(user_access=user_access)

        if args['type'] == 'service_config':
            if not args['id']:
                return TeraServiceConfigForm.get_service_config_form()

            from libtera.db.models.TeraService import TeraService
            service = TeraService.get_service_by_id(args['id'])

            if not service:
                return gettext('Invalid service id'), 400

            return TeraServiceConfigForm.get_service_config_config_form(user_access=user_access,
                                                                        service_key=service.service_key)

        return gettext('Unknown form type: ') + args['type'], 500
