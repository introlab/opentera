from flask_login import logout_user
from flask_restful import Resource, reqparse


class Logout(Resource):
    def __init__(self, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self)
        self.parser = reqparse.RequestParser()

    def get(self):
        print('logout user')
        logout_user()
        return "User logged out."
