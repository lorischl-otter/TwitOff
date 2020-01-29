from decouple import config
from dotenv import load_dotenv
from flask import Flask, render_template, request
from .models import DB, User

load_dotenv()


def create_app():
    """Create and configure an instances of the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template(
            'base.html', title='TwitOff', users=User.query.all())

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        name = name or request.values['user_name']
        try:
            if request.method == 'POST':
                add_user(name)
                message = "User {} successfully added.".format(name)
            tweets = User.query.filter(User.username=name).one().tweets
        except Exception as e:
            message = 'Error adding {}: {}'.format(name, e)
            tweets = []
        return render_template(
            'user.html', title=name, tweets=tweets, message=message)

    return app
