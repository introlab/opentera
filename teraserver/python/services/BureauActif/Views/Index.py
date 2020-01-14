from flask.views import MethodView
from flask import render_template, request
from services.BureauActif.AccessManager import AccessManager


class Index(MethodView):
    # Decorators everywhere?
    # decorators = [auth.login_required]

    def __init__(self, *args, **kwargs):
        print('Index.__init__', args, kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        print(self.flaskModule)

    @AccessManager.token_required
    def get(self):
        print('get')
        print(request.cookies['BureauActifToken'])

        hostname = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']
        return render_template('index.html', hostname=hostname, port=port)

    def post(self):
        print('post')
        pass