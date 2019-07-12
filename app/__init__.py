
from flask import Flask, url_for
from flask_assets import Environment, Bundle
from dotenv import load_dotenv
from flask_pymongo import MongoClient
import os

# mongodb setup
uri = 'mongodb+srv://creditor:creditor123@creditscore-fs5ta.gcp.mongodb.net/test?retryWrites=true&w=majority'
client = MongoClient(uri, connectTimeoutMS=30000, connect=False)
db = client.creditdb

# initialise assets environment to the app
assets = Environment()

# create function that returns the app


def create_app():
    # initialise app
    app = Flask(__name__)

    # app secret
    SECRET_KEY = os.urandom(64)
    app.config['SECRET_KEY'] = SECRET_KEY
    # load environmental variables
    load_dotenv(verbose=True)

    # import blueprint
    from .views import api

    # register blueprint
    app.register_blueprint(api)

    # register assets
    assets.init_app(app)

    # register css assets
    # css bundle
    css = Bundle('scss/main.css', output='gen/style.css')
    assets.register('css_all', css)

    # js bundle
    js = Bundle('js/main.js', output='gen/app.js')
    assets.register('js_all', js)

    return app
