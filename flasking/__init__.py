import os

from flask import Flask, render_template
from flask_behind_proxy import FlaskBehindProxy
from . import database

def set_up(test_config=None):
    app = Flask(__name__)

    proxied = FlaskBehindProxy(app)
    app.config.from_mapping(SECRET_KEY='d821716fe32cfc57665bae47fc2d5dd3',
                            DATABASE=os.path.join(app.instance_path, ".sqlite"))

    if test_config is None:
        app.config.from_pyfile("config.py", silent=True)
    else:
        app.config.update(test_config)

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    @app.route("/")
    def home():
        return render_template('home.html', subtitle='Home', text='this the home page')
