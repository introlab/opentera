from flask.views import MethodView
from flask import render_template
from modules.LoginModule.LoginModule import participant_multi_auth


class Participant(MethodView):

    def __init__(self, *args, **kwargs):
        self.flaskModule = kwargs.get('flaskModule', None)

    @participant_multi_auth.login_required
    def get(self):
        hostname = self.flaskModule.config.server_config['hostname']
        port = self.flaskModule.config.server_config['port']
        return render_template('participant.html', hostname=hostname, port=port)


