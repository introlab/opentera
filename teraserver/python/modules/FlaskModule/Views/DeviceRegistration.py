from flask.views import MethodView
from flask import render_template
from modules.LoginModule.LoginModule import multi_auth


class DeviceRegistration(MethodView):
    # Decorators everywhere?
    decorators = [multi_auth.login_required]

    def __init__(self, *args, **kwargs):
        # print('Index.__init__', args, kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        # print(self.flaskModule)

    @multi_auth.login_required
    def get(self):
        # print('get')
        return render_template('device_register.html')

    @multi_auth.login_required
    def post(self):
        # print('post')
        pass

