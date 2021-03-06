"""Prediction of users based on tweet ebmeddings."""
import numpy as np
# from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import KNeighborsClassifier
from .models import User
from .twitter import BASILICA


def predict_user(user1_name, user2_name, tweet_text):
    """Determine and return which user is more likely to say a given tweet."""
    user1 = User.query.filter(User.username == user1_name).one()
    user2 = User.query.filter(User.username == user2_name).one()
    user1_embeddings = np.array([tweet.embedding for tweet in user1.tweets])
    user2_embeddings = np.array([tweet.embedding for tweet in user2.tweets])
    # think of embeddings as X, labels as y
    embeddings = np.vstack([user1_embeddings, user2_embeddings])
    labels = np.concatenate([
        np.ones(len(user1.tweets)), np.zeros(len(user2.tweets))])
    # log_reg = LogisticRegression().fit(embeddings, labels)
    knnc = KNeighborsClassifier(
        weights='distance', metric='cosine').fit(embeddings, labels)
    tweet_embedding = BASILICA.embed_sentence(tweet_text, model='twitter')
    return knnc.predict(np.array(tweet_embedding).reshape(1, -1))
