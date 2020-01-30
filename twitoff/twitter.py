# Imports
import basilica
import tweepy
from decouple import config
from .models import DB, Tweet, User

# TWITTER_USERS = [insert twitter users to have in default app if wanted]

TWITTER_AUTH = tweepy.OAuthHandler(
    config('TWITTER_CONSUMER_API_KEY'), config('TWITTER_CONSUMER_API_SECRET'))
TWITTER_AUTH.set_access_token(
    config('TWITTER_ACCESS_TOKEN'), config('TWITTER_ACCESS_TOKEN_SECRET'))
TWITTER = tweepy.API(TWITTER_AUTH)
BASILICA = basilica.Connection(config('BASILICA_KEY'))


def add_user(username):
    """
    Add or update a user and their Tweets.
    Throw an error if user doesn't exist or is private.
    """
    try:
        # Get user info from tweepy API
        twitter_user = TWITTER.get_user(username)

        # Add user infor to User table in database
        db_user = (User.query.get(twitter_user.id) or
                   User(id=twitter_user.id, username=username,
                   followers=twitter_user.followers_count))
        DB.session.add(db_user)

        # Add as many recent tweets as possible
        tweets = twitter_user.timeline(
            count=200, exclude_replies=True,
            include_rts=False, tweet_mode='extended',
            since_id=db_user.newest_tweet_id)

        if tweets:
            db_user.newest_tweet_id = tweets[0].id
        # Loop over each tweet
        for tweet in tweets:
            # Get Basilica embedding
            embedding = BASILICA.embed_sentence(
                tweet.full_text, model='twitter')
            # Add tweet info to Tweets table in database
            db_tweet = Tweet(
                id=tweet.id, text=tweet.full_text[:500], embedding=embedding)
            db_user.tweets.append(db_tweet)
            DB.session.add(db_tweet)
    except Exception as e:
        print('Error processing {}: {}'.format(username, e))
        raise e
    else:
        DB.session.commit()


# Depricated code:

        # db_user = User(
        #     id=twitter_user.id,
        #     username=twitter_user.screen_name,
        #     followers=twitter_user.followers_count,
        #     newest_tweet_id=newest_tweet_id)  # add what you want
        # DB.session.add(db_user)

# import pdb; pdb.set_trace()
