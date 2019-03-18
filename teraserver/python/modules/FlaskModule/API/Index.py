from flask import Flask, render_template
from flask_restful import Resource, Api
from modules.Globals import auth


class Index(Resource):
    @auth.login_required
    def get(self):
        return render_template('index.html')
