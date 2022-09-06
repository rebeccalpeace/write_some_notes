from . import api
from flask import jsonify, request   # request is a proxy for the latest request, like current_user for flask-login
from app.models import User

@api.route('/')
def index():
    names = ['Rebecca', 'Rachel', 'Xaq']
    return jsonify(names)

