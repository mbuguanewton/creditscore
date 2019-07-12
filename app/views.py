from . import db
from dotenv import load_dotenv
from functools import wraps
from bcrypt import hashpw, gensalt
from flask import Blueprint, redirect, render_template, jsonify, flash, request, session, url_for

# create a blueprint
api = Blueprint('api', __name__)

# load environmental variables
load_dotenv(verbose=True)

# routes
@api.route('/')
def index():
    return render_template('index.html')


# check for is logged in
def is_logged_in(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if 'logged_in' in session:
            return f(*args, **kwargs)
        else:
            flash('Unauthoried, Please login', 'danger')
            return redirect(url_for('api.login'))
    return wrap


@api.route('/register', methods=['POST', 'GET'])
def register():
    # get the method
    if request.method == 'POST':
        # access the database
        try:
            users = db.users
            print('connected to db successfully')

            # get the form values
            name = request.form['name']
            email = request.form['email']
            username = request.form['username']

            if not name and not email and not username:
                flash('Please fill the form', 'danger')
                return render_template('register.html')

            # encrypt the password
            password = hashpw(
                request.form['password'].encode('utf-8'), gensalt())

            # create an dictionary that will be passed to the db
            user = {
                'Name': name,
                'Email': email,
                'Username': username,
                'Password': password
            }

            # insert the user to the db
            users.insert_one(user)

            # show message of success insertion
            flash('Your account has been successfully added', 'success')

            # redirect url to login page
            return redirect(url_for('login'))
        except Exception as error:
            print('we have a problem', error)

    return render_template('register.html')


@api.route('/login', methods=['POST', 'GET'])
def login():
    # get method
    if request.method == 'POST':
        # get password candidate
        pass_candidate = request.form['password']

        # connect to the database
        users = db.users

        # find the user by the passed in username
        username = request.form['username']

        login_user = users.find_one({'Username': username})

        # check if login user is available
        if login_user:
            # check if passwords match
            if hashpw(pass_candidate.encode('utf-8'), login_user['Password']) == login_user['Password']:
                # create a session for the user
                session['logged_in'] = True
                session['username'] = login_user['Username']
                session['email'] = login_user['Email']
                session['name'] = login_user['Name']

                # show succesful login message
                flash('You have successfully logged in', 'success')

                # redirect to check score page
                return redirect(url_for('api.score'))
            else:
                error = 'invalid login, check username or password'
                flash('invalid login, check username or password', 'danger')
                return render_template('login.html', error=error)
        else:
            error = 'username not found'
            flash('username not found', 'danger')
            return render_template('login.html', error=error)
    return render_template('login.html')

# users accounts page


@api.route('/account')
@is_logged_in
def account():
    return render_template('account.html')


@api.route('/score')
@is_logged_in
def score():
    return render_template('score.html')


@api.route('/information')
@is_logged_in
def info():
    return render_template('info.html')


# logout route
@api.route('/logout')
@is_logged_in
def logout():
    if session['username']:
        # delete the username in session
        del session['username']
        # turn session logged in to false
        session['logged_in'] = False

        # redirect to home page
        return redirect(url_for('api.index'))
    return render_template('index.html')
