
from .views import api
from flask import Flask, url_for
from flask_assets import Environment, Bundle
from dotenv import load_dotenv
from flask_fontawesome import FontAwesome
import os
import h2o

# load env variables
load_dotenv(verbose=True)

# initialise assets environment to the app
assets = Environment()
fa = FontAwesome()

# create function that returns the app


def create_app():
    # initialise app
    app = Flask(__name__)

    # app secret
    SECRET_KEY = os.urandom(64)
    # load environmental variables

    load_dotenv(verbose=True)

    # import blueprint

    # register blueprint
    app.register_blueprint(api)

    # register assets
    assets.init_app(app)
    fa.init_app(app)

    # register css assets
    # css bundle
    css = Bundle('scss/main.css', output='gen/style.css')
    assets.register('css_all', css)

    # js bundle
    js = Bundle('js/main.js', output='gen/app.js')
    assets.register('js_all', js)

    # app configuration
    app.config['SECRET_KEY'] = SECRET_KEY

    return app
