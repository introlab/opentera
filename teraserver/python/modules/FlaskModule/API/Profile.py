from flask import Flask, jsonify
from flask_restful import Resource, Api
from modules.Globals import auth


class Profile(Resource):
    @auth.login_required
    def get(self):
        print('profile')
        profile = {'profile': 'empty'}
        return jsonify(profile)
