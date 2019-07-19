from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth
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

    def __init__(self, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self)
        self.parser = reqparse.RequestParser()
        self.parser.add_argument('type', type=str, help='Definition type required', required=True)

    @auth.login_required
    def get(self):
        args = self.parser.parse_args(strict=True)
        current_user = TeraUser.get_user_by_uuid(session['user_id'])
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
