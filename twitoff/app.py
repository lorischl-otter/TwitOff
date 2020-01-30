from decouple import config
# from dotenv import load_dotenv
from flask import Flask, render_template, request
from .models import DB, User
from .twitter import add_user
# from .predict import predict_user

# load_dotenv()


def create_app():
    """Create and configure an instances of the Flask application."""
    app = Flask(__name__)
    app.config['SQLALCHEMY_DATABASE_URI'] = config('DATABASE_URL')
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    DB.init_app(app)

    @app.route('/')
    def root():
        users = User.query.all()
        return render_template(
            'base.html', title='TwitOff', users=users)

    @app.route('/user', methods=['POST'])
    @app.route('/user/<name>', methods=['GET'])
    def user(name=None, message=''):
        name = name or request.values['username']
        # followers = request.values['followers']
        try:
            if request.method == 'POST':
                add_user(name)
                message = "User {} successfully added.".format(name)
            # else:
            #     message = "{} followers".format(followers)
            tweets = User.query.filter(User.username == name).one().tweets
        # Trigger an error message
        except Exception as e:
            message = 'Error adding {}: {}'.format(name, e)
            tweets = []
        return render_template(
            'user.html', title=name, tweets=tweets, message=message)

    # @app.route('/compare', methods=['POST'])
    # def compare(user1=, user2, fake_tweet):
    #     try:
    #         predict_user()
    #     return render_template('compare.html', message=message)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='Reset database complete.')

    return app
