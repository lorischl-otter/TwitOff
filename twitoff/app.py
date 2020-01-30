from decouple import config
# from dotenv import load_dotenv
from flask import Flask, render_template, request
from .models import DB, User
from .twitter import add_user, update_users
from .predict import predict_user

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

    @app.route('/compare', methods=['POST'])
    def compare(message=''):
        user1 = request.values['user1']
        user2 = request.values['user2']
        fake_tweet = request.values['tweet_text']
        try:
            if user1 == user2:
                message = "It's not very interesting to compare a user to themselves!"
            else:
                prediction = predict_user(user1, user2, fake_tweet)
                message = "'{}' is more likely to be said by {} than {}.".format(
                    fake_tweet, user1 if prediction else user2, 
                    user2 if prediction else user1
                    )
        except Exception as e:
            message = 'Error comparing {} and {}: {}'.format(user1, user2, e)
        return render_template('compare.html', title='Prediction', message=message)

    @app.route('/reset')
    def reset():
        DB.drop_all()
        DB.create_all()
        return render_template('base.html', title='Reset database complete.')

    @app.route('/update')
    def update():
        update_all_users()
        return render_template('base.html', users=User.query.all(), title="Tweets updated!")

    return app
