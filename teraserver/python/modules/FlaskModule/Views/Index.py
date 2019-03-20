from flask.views import MethodView
from flask import render_template
from modules.Globals import auth


class Index(MethodView):
    def __init__(self, *args, **kwargs):
        print('Index.__init__', args, kwargs)
        self.module = kwargs.get('module', None)
        print(self.module)

    @auth.login_required
    def get(self):
        print('get')
        return render_template('index.html')

    @auth.login_required
    def post(self):
        print('post')
        pass

