from flask.views import MethodView
from flask import render_template
from modules.Globals import auth


class Index(MethodView):
    # Decorators everywhere?
    decorators = [auth.login_required]

    def __init__(self, *args, **kwargs):
        print('Index.__init__', args, kwargs)
        self.flaskModule = kwargs.get('flaskModule', None)
        print(self.flaskModule)

    @auth.login_required
    def get(self):
        print('get')
        return render_template('index.html')

    @auth.login_required
    def post(self):
        print('post')
        pass

