from flask_login import logout_user
from flask_restful import Resource, reqparse
from flask import session

class Logout(Resource):
    def __init__(self, flaskModule=None):
        self.module = flaskModule
        Resource.__init__(self)
        self.parser = reqparse.RequestParser()

    def get(self):
        print('logout user')
        logout_user()
        session.clear()
        return "User logged out."
