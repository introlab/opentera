from flask.views import MethodView
from flask import render_template, request
from services.VideoDispatch.AccessManager import AccessManager, current_user_client


class DashboardMain(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @AccessManager.token_required
    def get(self):
        # print('get')
        # print(request.cookies['VideoDispatchToken'])

        # This could happen if a participant tries to reach that page
        # TODO: Make a specific decorator in AccessManager
        if not current_user_client:
            return 'Access Denied', 403

        hostname = self.flaskModule.config.service_config['hostname']
        port = self.flaskModule.config.service_config['port']
        backend_hostname = self.flaskModule.config.backend_config['hostname']
        backend_port = self.flaskModule.config.backend_config['port']
        if 'X_EXTERNALHOST' in request.headers:
            backend_hostname = request.headers['X_EXTERNALHOST'];

        if 'X_EXTERNALPORT' in request.headers:
            backend_port = request.headers['X_EXTERNALPORT'];

        # current_user_client.do_get_request_to_backend('/api/user/users?user_uuid=' + current_user_client.user_uuid)
        # print(current_user_client.get_role_for_site(1))
        # print(current_user_client.get_role_for_project(1))

        return render_template('main_en.html', hostname=hostname, port=port,
                               backend_hostname=backend_hostname, backend_port=backend_port)

    def post(self):
        print('post')
        pass