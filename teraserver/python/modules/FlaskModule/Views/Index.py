from flask.views import MethodView
from flask import render_template
from modules.LoginModule.LoginModule import user_multi_auth


class Index(MethodView):

    def __init__(self, *args, **kwargs):
        print('Index.__init__', args, kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        print(self.flaskModule)

    @user_multi_auth.login_required
    def get(self):
        print('get')
        hostname = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']
        return render_template('index.html', hostname=hostname, port=port)

    @user_multi_auth.login_required
    def post(self):
        print('post')
        pass

