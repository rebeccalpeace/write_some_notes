import json
from . import api
from .auth import basic_auth, token_auth
from flask import jsonify, request   # request is a proxy for the latest request, like current_user for flask-login
from app.models import User

@api.route('/token')
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    token = user.get_token()
    return jsonify({'token': token})

