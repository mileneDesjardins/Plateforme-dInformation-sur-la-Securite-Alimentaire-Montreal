import tweepy

from flask import (current_app)
from app import app

with app.app_context():
    consumer_key = current_app.config["API_KEY"]
    consumer_secret = current_app.config["API_SECRET"]
    access_token = current_app.config["ACCESS_TOKEN"]
    access_token_secret = current_app.config["ACCESS_TOKEN_SECRET"]


def twitter_post(etablissement_name):
    client = tweepy.Client(consumer_key=consumer_key,
                           consumer_secret=consumer_secret,
                           access_token=access_token,
                           access_token_secret=access_token_secret)

    status = ("Une nouvelle contravention a été détectée pour "
              "l'établissement suivant : ") + etablissement_name

    # Todo quoi faire si quelque chose va pas
    try:
        client.create_tweet(text=status)
    except(Exception) as e:
        print(str(e))
