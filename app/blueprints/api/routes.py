import json
from . import api
from .auth import basic_auth, token_auth
from flask import jsonify, request   # request is a proxy for the latest request, like current_user for flask-login
from app.models import User, Word, Prompt, Daily, Answer, Comment, Likes

@api.route('/token')
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    token = user.get_token()
    return jsonify({'token': token})


@api.route('/users', methods=["POST"])
def create_user():
    if not request.is_json:
        return jsonify({'error': 'Your request content-type must be application/json'}), 400
    data = request.json
    for field in ['email', 'first_name', 'last_name', 'username', 'password']:
        if field not in data:
            return jsonify({'error': f'{field} must be in request body'}), 400
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    username = data.get('username')
    password = data.get('password')
    existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
    if existing_user:
        return jsonify({'error': "User with that username and/or email already exists."}), 400
    new_user = User(email=email, first_name=first_name, last_name=last_name, username=username, password=password)
    return jsonify(new_user.to_dict()), 201

@api.route('/create_answer', methods=["POST"])
@token_auth.login_required
def create_answer():
    if not request.is_json:
        return jsonify({'error': 'Your request content-type must be application/json'}), 400
    data = request.json
    url = data.get('url')
    line1 = data.get('line1')
    line2 = data.get('line2')
    line3 = data.get('line3')
    line4 = data.get('line4')
    line5 = data.get('line5')
    line6 = data.get('line6')
    prompt_id = data.get('prompt_id')
    daily_id = data.get('daily_id')
    user_id = token_auth.current_user().id
    new_answer = Answer(url=url, line1=line1, line2=line2, line3=line3, line4=line4, line5=line5, line6=line6, prompt_id=prompt_id, daily_id=daily_id, user_id=user_id)
    return jsonify(new_answer.to_dict()), 201

@api.route('/answers/<int:answer_id>')
@token_auth.login_required
def get_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    return jsonify(answer.to_dict())
    
@api.route('/users/<int:user_id>')   # this also returns all answers associated with the current user
@token_auth.login_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())

@api.route('/answers_by_prompt/<prompt_id>')
@token_auth.login_required
def get_answers_by_prompt(prompt_id): 
    answers = Answer.query.filter_by(prompt_id=prompt_id)
    return jsonify([a.to_dict() for a in answers]) 

@api.route('/answers_by_daily/<daily_id>')
@token_auth.login_required
def get_answers_by_daily(daily_id): 
    answers = Answer.query.filter_by(daily_id=daily_id)
    return jsonify([a.to_dict() for a in answers]) 

