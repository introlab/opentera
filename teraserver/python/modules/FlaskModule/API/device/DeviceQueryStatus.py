from flask_restx import Resource, reqparse
from modules.LoginModule.LoginModule import LoginModule
from flask_babel import gettext
from modules.FlaskModule.FlaskModule import device_api_ns as api
from opentera.db.models.TeraDevice import TeraDevice


# Parser definition(s)
get_parser = api.parser()
post_parser = api.parser()


class DeviceQueryStatus(Resource):

    def __init__(self, _api, flaskModule=None):
        Resource.__init__(self, _api)
        self.module = flaskModule

    @LoginModule.device_token_or_certificate_required
    @api.expect(post_parser)
    @api.doc(description='Login device with Token.',
             responses={200: 'Success',
                        500: 'Required parameter is missing',
                        501: 'Not implemented',
                        403: 'Logged device doesn\'t have permission to access the requested data'})
    def post(self):
        return '', 501
