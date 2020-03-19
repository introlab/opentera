from flask.views import MethodView
from flask import render_template, request
from services.VideoDispatch.AccessManager import AccessManager, current_client


class Index(MethodView):
    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    def get(self):
        # print('get')
        # print(request.cookies['VideoDispatchToken'])

        hostname = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']
        backend_hostname = self.flaskModule.config.backend_config['hostname']
        backend_port = self.flaskModule.config.backend_config['port']
        if 'X_EXTERNALHOST' in request.headers:
            backend_hostname = request.headers['X_EXTERNALHOST'];

        if 'X_EXTERNALPORT' in request.headers:
            backend_port = request.headers['X_EXTERNALPORT'];

        # current_client.do_get_request_to_backend('/api/user/users?user_uuid=' + current_client.user_uuid)
        # print(current_client.get_role_for_site(1))
        # print(current_client.get_role_for_project(1))

        return render_template('index.html')

    def post(self):
        if 'name' in request.form and 'email' in request.form:
            name = request.form['name']
            email = request.form['email']
            return 'Merci ' + name + '. Nous allons vous envoyer une invitation au courriel:' + email, 200
        else:
            return 'Invaild', 400
