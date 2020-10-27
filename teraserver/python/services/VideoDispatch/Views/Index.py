from flask.views import MethodView
from flask import render_template, request
from services.shared.ServiceOpenTera import ServiceOpenTera
import services.VideoDispatch.Globals as Globals


class Index(MethodView):
    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    def get(self):
        # print('get')
        # print(request.cookies['VideoDispatchToken'])

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

        return render_template('index_en.html')

    def post(self):

        backend_hostname = self.flaskModule.config.backend_config['hostname']
        backend_port = self.flaskModule.config.backend_config['port']

        if 'user-test-form' in request.form:
            # Survey results, TODO: process data if required
            survey_ok = True
            return render_template('index_en.html', survey_ok=survey_ok)

        if 'user-infos-form' in request.form:
            if 'name' in request.form and 'email' in request.form:
                name = request.form['name']
                email = request.form['email']

                # Call OpenTera server to create a participant
                # This is a synchronous call
                # url = "http://" + backend_hostname + ':' + str(backend_port) + '/api/service/participants'
                # request_headers = {'Authorization': 'OpenTera ' + self.service_token}

                participant_info = {'participant': {'id_participant': 0,  # Will create a new participant
                                                    'id_project': 1,  # Hard coded for now
                                                    'participant_name': request.form['name'],
                                                    'participant_email': request.form['email']}}

                # response = post(url=url, verify=False, headers=request_headers, json=participant_info)
                response = Globals.service.post_to_opentera(api_url='/api/service/participants',
                                                            json_data=participant_info)
                if response.status_code == 200:
                    # TODO SEND EMAIL!
                    server_participant_info = response.json()

                    # default values
                    hostname = self.flaskModule.config.service_config['hostname']
                    port = self.flaskModule.config.service_config['port']
                    scheme = 'https'
                    path = '/login'

                    if 'X-Externalhost' in request.headers:
                        hostname = request.headers['X-Externalhost']

                    if 'X-Externalport' in request.headers:
                        port = request.headers['X-Externalport']

                    if 'X-Scheme' in request.headers:
                        scheme = request.headers['X-Scheme']

                    if 'X-Script-Name' in request.headers:
                        path = request.headers['X-Script-Name'] + path

                    url = scheme + '://' + hostname + ':' + port + path + '?participant_token=' + \
                          server_participant_info['participant_token']

                    # Render template with participant information and link
                    return render_template('index_participant_info_en.html', info=server_participant_info, participant_url=url)
                else:
                    return 'Invalid', 500

        else:
            return 'Invalid', 400
