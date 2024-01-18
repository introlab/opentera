from flask_restx import Resource

from modules.FlaskModule.FlaskModule import test_api_ns as api
import modules.Globals
import json


# Parser definition(s)
# GET
get_parser = api.parser()


class TestDBReset(Resource):

    def __init__(self, _api, *args, **kwargs):
        Resource.__init__(self, _api, *args, **kwargs)
        self.module = kwargs.get('flaskModule', None)
        self.test = kwargs.get('test', False)

    @api.doc(description='Reset database to default values',
             responses={200: 'Success'})
    @api.expect(get_parser)
    def get(self):
        modules.Globals.db_man.reset_db()
        return 200
