from flask import jsonify
from flask_restful import Resource, reqparse
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser


class Profile(Resource):

    def __init__(self, flaskModule=None):
        Resource.__init__(self)
        self.parser = reqparse.RequestParser()


    @auth.login_required
    def get(self):
        return jsonify(TeraUser.get_profile_def())
