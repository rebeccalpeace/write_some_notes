from app import app
from flask import render_template, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from app.forms import SignUpForm, LoginForm, WordForm
from app.models import User, Word

@app.route('/', methods=['GET', 'POST'])
def index():
    form = WordForm()
    if form.validate_on_submit():
        word = form.word.data
        word_length = len(form.word.data)
        new_word = Word(word=word, word_length=word_length)
        flash(f"{new_word.word} {new_word.word_length} has been added to the Word table",'primary')
        return redirect(url_for('index'))
    return render_template('index.html', form=form)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = SignUpForm()
    if form.validate_on_submit():
        print('Form has been validated!')
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        username = form.username.data
        password = form.password.data
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            flash('A user with that username or email already exists.', 'danger')
            return redirect(url_for('signup'))
        new_user = User(email=email, first_name=first_name, last_name=last_name, username=username, password=password)
        flash(f"{new_user.username} has been created.", 'success')
        return redirect(url_for('index'))
    return render_template('signup.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.query.filter_by(username=username).first()
        if user is not None and user.check_password(password):
            login_user(user)
            flash(f"Welcome back {user.username}!", 'success')
            return redirect(url_for('login'))
        else:
            flash('Incorrect username and/or password. Please try again.', 'danger')
            return redirect(url_for('login'))
    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You have successfully logged out.', 'primary')
    return redirect(url_for('index'))



