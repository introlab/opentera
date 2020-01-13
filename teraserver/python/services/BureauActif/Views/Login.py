from flask.views import MethodView
from flask import render_template


class Login(MethodView):
    # Decorators everywhere?
    # decorators = [auth.login_required]

    def __init__(self, *args, **kwargs):
        print('Index.__init__', args, kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        print(self.flaskModule)

    def get(self):
        print('get')
        hostname = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']
        return render_template('login.html', hostname=hostname, port=port)

    def post(self):
        print('post')
        pass