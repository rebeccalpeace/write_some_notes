import json
from datetime import date
import random
from . import api
from .auth import basic_auth, token_auth
from flask import jsonify, request   # request is a proxy for the latest request, like current_user for flask-login
from app.models import User, Word, Prompt, Daily, Answer, Comment, Likes

@api.route('/token')
@basic_auth.login_required
def get_token():
    user = basic_auth.current_user()
    token = user.get_token()
    return jsonify({'token': token, 'token_expiration': user.token_expiration})


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


@api.route('/users/<int:user_id>')   # this also returns all answers associated with the current user
@token_auth.login_required
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(user.to_dict())


@api.route('/answers/<int:answer_id>')
@token_auth.login_required
def get_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    return jsonify(answer.to_dict())

@api.route('/answers_by_user')
@token_auth.login_required
def get_answers_by_user():
    user_id = token_auth.current_user().id
    answers = Answer.query.filter_by(user_id=user_id).all()
    return jsonify([a.to_dict() for a in answers])
    

@api.route('/answers_by_prompt/<int:prompt_id>')
@token_auth.login_required
def get_answers_by_prompt(prompt_id): 
    answers = Answer.query.filter_by(prompt_id=prompt_id).all()
    return jsonify([a.to_dict() for a in answers]) 


@api.route('/answers_by_daily/<int:daily_id>')
@token_auth.login_required
def get_answers_by_daily(daily_id): 
    answers = Answer.query.filter_by(daily_id=daily_id).all()
    return jsonify([a.to_dict() for a in answers]) 


@api.route('/delete_answer/<int:answer_id>', methods=["DELETE"])
@token_auth.login_required
def delete_answer(answer_id):
    answer = Answer.query.get_or_404(answer_id)
    user = token_auth.current_user()
    if user.id != answer.user_id:
        return jsonify({'error': 'You are not allowed to delete this answer.'}), 403
    answer.delete()
    return jsonify({'success': 'This answer has been deleted.'})


@api.route('/delete_user/<int:user_id>', methods=["DELETE"])
@token_auth.login_required
def delete_user(user_id):
    current_user = token_auth.current_user()
    if current_user.id != user_id:
        return jsonify({'error': 'You do not have access to delete this user.'}), 403
    user_to_delete = User.query.get_or_404(user_id)
    answers_to_delete = Answer.query.filter_by(user_id=user_id)
    [a.delete() for a in answers_to_delete]
    user_to_delete.delete()
    return jsonify({'success': f'{user_to_delete.username} has been deleted.'})


@api.route('/update/<int:user_id>', methods=["PUT"])
@token_auth.login_required
def update_user(user_id):
    current_user = token_auth.current_user()
    if current_user.id != user_id:
        return jsonify({'error': 'You do not have access to upate this user.'}), 403
    user = User.query.get_or_404(user_id)
    data = request.json
    email = data.get('email')
    first_name = data.get('first_name')
    last_name = data.get('last_name')
    username = data.get('username')
    password = data.get('password')
    existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
    if existing_user.id != user_id:
        return jsonify({'error': "User with that username and/or email already exists."}), 400
    user.update(data)
    return jsonify(user.to_dict())

@api.route('/random_by_id/<int:id>')
@token_auth.login_required
def get_random(id):
    random = Prompt.query.get_or_404(id)
    return jsonify(random.to_dict())

@api.route('/daily_by_id/<int:id>')
@token_auth.login_required
def get_daily(id):
    daily = Daily.query.get_or_404(id)
    return jsonify(daily.to_dict())

@api.route('/daily')
@token_auth.login_required
def deal_daily():
    # determine how many prompts are in the Daily table
    days = Daily.query.count()
    # determine which id to display for the day by using toordinal(), add 1 to start range at 1 instead of 0
    prompt_id = ((date.today().toordinal()) % days) + 1
    daily = Daily.query.get_or_404(prompt_id)
    return jsonify(daily.to_dict())


@api.route('/prompt')
@token_auth.login_required
def deal_prompt():
    # user = User.query.get_or_404(user_id)
    user_id = token_auth.current_user().id
    prompts = Prompt.query.count()
    seen = Answer.query.filter_by(user_id=user_id).all()
    seen_prompts = []
    if len(seen) == 0:
        # return a random prompt to them in range of length of table
        prompt = random.randint(1, prompts)
        deal_to_player = Prompt.query.get_or_404(prompt)
        return jsonify(deal_to_player.to_dict())
    elif len(seen) == prompts:
        return jsonify({'error': 'User has answered all of the prompts!'})
    else:
        # append the prompt_ids for all answers in users history
        for i in seen:
            seen_prompts.append(i.prompt_id)
        # get a random prompt
        prompt = random.randint(1, prompts)
        # check to see if user has already answered the random prompt
        while prompt in seen_prompts:
            prompt = random.randint(1, prompts)
        # send random prompt back to front end
        deal_to_player = Prompt.query.get_or_404(prompt)
        return jsonify(deal_to_player.to_dict())


@api.route('/words')
@token_auth.login_required
def deal_words():
    # sends 50 words to front end
    # query all words
    words = Word.query.all()
    # copy all words and ids into a list
    words_list = []
    for word in words:
        words_list.append([word.id, word.word])
    words_to_player = []
    for i in range(60):
        x = random.randint(0, len(words_list)-1)
        popped = words_list.pop(x)
        words_to_player.append({"id":popped[0], "word":popped[1], "category": "toPlay"})
    return jsonify(words_to_player)


# need route that changes a like in like database with the current user id(turns flower to orange or black)
@api.route('/likes', methods=["PUT"])
@token_auth.login_required
def post_likes():
    # front end will submit the answer id, the liker id, the creator id
    data = request.json
    answer = data.get('answer_id')
    creator = data.get('creator_id')
    liker_id = token_auth.current_user().id
    # check if liker id is in database with this certain answer id
    # query the database for liker id, add to list
    user_likes = Likes.query.filter_by(liker_id=liker_id, answer_id=answer).all()
    # if answer_id in list, change boolean to opposite
    if len(user_likes) == 0:
        new_like = Likes(like=True, answer_id=answer, creator_id=creator, liker_id=liker_id)
        return jsonify(new_like.to_dict()), 201
    else:
        user_likes[0].update({"like": not user_likes[0].like})
        return jsonify(user_likes[0].to_dict()), 200

# need route that gets the number of likes for an answer (queries like database and returns number of how many likes an answer has)

@api.route('/likes/<int:answer_id>', methods=["GET"])
@token_auth.login_required
def answer_likes(answer_id):
    likes = Likes.query.filter_by(answer_id=answer_id, like=True).all()
    if len(likes) == 0:
        return jsonify(0), 200
    return jsonify(len(likes))

# need route that checks if user has liked that answer (returns true or false to turn flower orange or black)

@api.route('/user_like/<int:answer_id>', methods=["GET"])
@token_auth.login_required
def user_like(answer_id):
    # front end will submit the answer_id
    # check to see if user has liked this answer
    # if in database return like.like
    # else return false (if user has not liked this answer)
    answer = answer_id
    liker_id = token_auth.current_user().id
    user_likes = Likes.query.filter_by(liker_id=liker_id, answer_id=answer).all()
    if len(user_likes) == 0:
        return jsonify({}), 200
    else:
        return jsonify(user_likes[0].to_dict()), 200
      
                





    







    









