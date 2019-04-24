from flask import jsonify, session
from flask_restful import Resource, reqparse
from modules.Globals import auth

from libtera.db.models.TeraUser import TeraUser

from libtera.forms.TeraUserForm import TeraUserForm
from libtera.forms.TeraSiteForm import TeraSiteForm
from libtera.forms.TeraDeviceForm import TeraDeviceForm
from libtera.forms.TeraKitDeviceForm import TeraKitDeviceForm


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

        if args['type'] == 'user_profile':
            return jsonify(TeraUserForm.get_user_profile_form())

        if args['type'] == 'user':
            return jsonify(TeraUserForm.get_user_form())

        if args['type'] == 'site':
            return jsonify(TeraSiteForm.get_site_form())

        if args['type'] == 'device':
            return jsonify(TeraDeviceForm.get_device_form(current_user=current_user))

        if args['type'] == 'kit_device':
            return jsonify(TeraKitDeviceForm.get_kit_device_form(current_user=current_user))

        return 'Unknown definition type: ' + args['type'], 500
