import os
import h2o
import pandas as pd
from dotenv import load_dotenv
from flask_pymongo import MongoClient
from functools import wraps
from .controllers import recommend
from bcrypt import hashpw, gensalt
from flask import Blueprint, redirect, render_template, jsonify, flash, request, session, url_for

import datetime

# create a blueprint
api = Blueprint('api', __name__)
h2o.init()

model = h2o.load_model(
    '/home/lostvane/Projects/school-project/CreditScore/app/ml_model/model/GBM_model_python_1565074809758_307')

loans = pd.read_csv(
    '/home/lostvane/Projects/school-project/CreditScore/app/ml_model/loans.csv')

# mongo set up
# mongodb setup
uri = os.getenv('MONGO_URI')
client = MongoClient(uri, connectTimeoutMS=30000, connect=False)
db = client.creditdb

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
            return redirect(url_for('api.login'))
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
            print(login_user['_id'])
            if hashpw(pass_candidate.encode('utf-8'), login_user['Password']) == login_user['Password']:
                # create a session for the user
                session['logged_in'] = True
                session['username'] = login_user['Username']
                session['email'] = login_user['Email']
                session['name'] = login_user['Name']
                # session['id'] = login_user['_id']

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


@api.route('/score', methods=["POST", "GET"])
@is_logged_in
def score():
    if request.method == "POST":
        # get form data
        loan_amount = int(request.form.get("loanamount"))
        funded_amnt = int(request.form.get("funded"))
        installment = int(request.form.get("installment"))
        int_rate = float(request.form.get("interest"))
        # to be a select with 2 options
        term = int(request.form.get("term"))
        # select with 10 options
        emp_length = int(request.form.get("employment"))
        # select with 3 options
        home_ownership = request.form.get("home")
        annual_inc = int(request.form.get("income"))
        # select with 4 options
        purpose = request.form.get("purpose")

        # put then into a list
        formlist = [loan_amount, funded_amnt, installment, int_rate,
                    term, emp_length, home_ownership, annual_inc, purpose]

        # change the list to a dataframe
        new_form_list = pd.DataFrame(
            [formlist],
            columns=['loan_amnt', 'funded_amnt', 'installment', 'int_rate',
                     'term', 'emp_length', 'home_ownership', 'annual_inc', 'purpose'],
        )
        # change the dataframe to a h2o framw
        h2o_formlist = h2o.H2OFrame(new_form_list)
        print(h2o_formlist)

        # use the model to predict based on given data
        prediction = model.predict(h2o_formlist)

        # get the score
        score = round(prediction[0, 1] * 100)

        # get probability of being good
        good_prediction = prediction[0, 1]

        # call our function on the prediction as the score
        recom = recommend(good_prediction, loans)

        # get recommendations from the dataframe
        # banks
        banks = [i for i in recom.BANKS[:2]]
        # loan
        loan = [i for i in recom.LOANS[:2]]
        # interest
        interest = [i for i in recom.RATES[:2]]
        # maximum amount
        max_amount = [i for i in recom.MAX_AMOUNT[:2]]

        # connect to db and store the scores
        scores = db.scores

        # create an object
        new_score = {
            'User_id': session['username'],
            'Score': score,
            'Loan_amount': loan_amount,
            'Funded_amount': funded_amnt,
            'Loan_interest': int_rate,
            'Annual_income': annual_inc,
            'Purpose': purpose,
            'Created': datetime.datetime.now()

        }
        # try to save it to db
        try:
            scores.insert_one(new_score)
            print('your score has been saved')
        except Exception as error:
            print('something went wrong: ', error)

        return render_template('result.html', score=score, proba=good_prediction, bank=banks, loan=loan, interest=interest, maxamount=max_amount)
    return render_template('score.html')


@api.route('/account', methods=['GET'])
@is_logged_in
def account():
    #
    # connect to db
    scores = db.scores
    # initialise empty list
    result = scores.find({'User_id': session['username']})
    for score in result:
        if score:
            output = {
                'user_id': score['User_id'],
                'score': score['Score'],
                'loan': score['Loan_amount'],
                'funded': score['Funded_amount'],
                'interest': score['Loan_interest'],
                'income': score['Annual_income'],
                'Purpose': score['Purpose'],
            }

    return render_template('account.html', output=output)


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
