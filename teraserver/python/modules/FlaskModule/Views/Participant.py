from flask.views import MethodView
from modules.LoginModule.LoginModule import LoginModule, current_participant

from flask import render_template, request, redirect, flash


class Participant(MethodView):
    def __init__(self, *args, **kwargs):
        print('Participant.__init__', args, kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        print(self.flaskModule)

    @LoginModule.token_required
    def get(self):

        print('current participant', current_participant)
        return render_template('participant.html', token=current_participant.participant_token)
        # return 'Participant GET ' + current_participant.participant_name


