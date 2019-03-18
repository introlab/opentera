from flask import Flask, jsonify
from flask_restful import Resource, Api
from modules.Globals import auth
from libtera.db.models.TeraUser import TeraUser


class Profile(Resource):
    @auth.login_required
    def get(self):
        return jsonify(TeraUser.get_profile_def())
