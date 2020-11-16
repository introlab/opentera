from flask.views import MethodView
from flask import render_template, request
from services.BureauActif.AccessManager import AccessManager, current_user_client


class Index(MethodView):
    # Decorators everywhere?
    # decorators = [auth.login_required]

    def __init__(self, *args, **kwargs):
        print('Index.__init__', args, kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        print(self.flaskModule)

    def get(self):

        return self.flaskModule.session.app.send_static_file('index.html')

    def post(self):
        print('post')
        pass