from flask import jsonify, session
from flask_restplus import Resource, reqparse
from modules.LoginModule.LoginModule import user_multi_auth
from modules.FlaskModule.FlaskModule import user_api_ns as api
from libtera.db.DBManager import DBManager

from libtera.db.models.TeraUser import TeraUser

from libtera.forms.TeraUserForm import TeraUserForm
from libtera.forms.TeraSiteForm import TeraSiteForm
from libtera.forms.TeraDeviceForm import TeraDeviceForm
from libtera.forms.TeraProjectForm import TeraProjectForm
from libtera.forms.TeraParticipantGroupForm import TeraParticipantGroupForm
from libtera.forms.TeraParticipantForm import TeraParticipantForm
from libtera.forms.TeraSessionTypeForm import TeraSessionTypeForm
from libtera.forms.TeraSessionForm import TeraSessionForm


class QueryForms(Resource):

    def __init__(self, _api, *args, **kwargs):
        self.module = kwargs.get('flaskModule', None)
        Resource.__init__(self, _api, *args, **kwargs)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('type', type=str, help='Definition type required', required=True)

    @user_multi_auth.login_required
    @api.doc(description='Get json description of standard input form for the specified data type.',
             responses={200: 'Success',
                        500: 'Unknown or unsupported data type'})
    @api.param(name='type', type='string', description='Data type of the required form. Currently, the following data '
                                                       'types are supported: \n user_profile\nuser\nsite\ndevice\n'
                                                       'project\ngroup\nparticipant\nsession_type\nsession')
    def get(self):
        args = self.parser.parse_args(strict=True)
        current_user = TeraUser.get_user_by_uuid(session['_user_id'])
        user_access = DBManager.userAccess(current_user)

        if args['type'] == 'user_profile':
            return jsonify(TeraUserForm.get_user_profile_form())

        if args['type'] == 'user':
            return jsonify(TeraUserForm.get_user_form())

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

        return 'Unknown definition type: ' + args['type'], 500
