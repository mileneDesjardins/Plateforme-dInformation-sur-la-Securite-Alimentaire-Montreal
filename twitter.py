import base64
import hashlib
import os
import re
import requests
import tweepy

from requests_oauthlib import OAuth1Session
from flask import (Flask, request, redirect, session, url_for, render_template,
                   current_app, jsonify)
from app import app

with app.app_context():
    client_id = current_app.config["CLIENT_ID"]
    client_secret = current_app.config["CLIENT_SECRET"]
    consumer_key = current_app.config["API_KEY"]
    consumer_secret = current_app.config["API_SECRET"]

authorize_url = "https://twitter.com/oauth/authorize"
request_token_url = "https://api.twitter.com/oauth/request_token"
access_token_url = 'https://api.twitter.com/oauth/access_token'
callback_url = "http://127.0.0.1:5000/oauth/callback"


def twitter_request_token():
    twitter = OAuth1Session(consumer_key, client_secret=consumer_secret)

    # REQUEST TOKEN
    fetch_response = twitter.fetch_request_token(request_token_url)
    session["oauth_token"] = fetch_response.get("oauth_token")
    session["oauth_token_secret"] = fetch_response.get(
        "oauth_token_secret")

    # AUTHORIZE
    auth_url = twitter.authorization_url(authorize_url,
                                         oauth_token=session["oauth_token"])
    return redirect(auth_url)


def request_token(twitter):
    fetch_response = twitter.fetch_request_token(request_token_url)
    session["oauth_token"] = fetch_response.get("oauth_token")
    session["oauth_token_secret"] = fetch_response.get(
        "oauth_token_secret")


def callback():
    # CALLBACK RECOIT OAUTH
    oauth_verifier = request.args.get('oauth_verifier')
    oauth_token = session.get('oauth_token')
    oauth_token_secret = session.get('oauth_token_secret')

    twitter = OAuth1Session(
        consumer_key,
        client_secret=consumer_secret,
        resource_owner_key=oauth_token,
        resource_owner_secret=oauth_token_secret,
        verifier=oauth_verifier
    )

    access_token_dict = twitter.fetch_access_token(access_token_url)
    access_token = access_token_dict.get('oauth_token')
    access_token_secret = access_token_dict.get('oauth_token_secret')

    payload = upload_media()
    response = post_tweet(payload, access_token, access_token_secret).json()

    return response


def post_tweet(payload, access_token, secret_token):
    # Créer l'en-tête d'autorisation OAuth1
    auth_header = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    # Ajouter le token secret dans l'en-tête
    oauth_params = {
        "oauth_consumer_key": "YOUR_CONSUMER_KEY",
        "oauth_nonce": "",
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": "",  # Remplir avec le timestamp UNIX actuel
        "oauth_token": access_token,
        "oauth_version": "1.0",
    }

    # Générer la signature OAuth1
    # Ceci est un exemple basique, vous devrez utiliser une bibliothèque pour générer la signature correcte
    # La signature est basée sur les paramètres OAuth et votre clé secrète de consommateur et votre secret de token
    # oauth_signature = generate_oauth_signature(oauth_params, "YOUR_CONSUMER_SECRET", access_token_secret)

    # Ajouter la signature à l'en-tête d'autorisation
    # auth_header["Authorization"] += f', oauth_signature="{oauth_signature}"'

    # Envoyer la requête POST avec l'en-tête d'autorisation
    response = requests.post(
        "https://api.twitter.com/2/tweets",
        json=payload,
        headers=auth_header,
    )

    return response


def upload_media():
    test = {"text": "hevxcvxvcbcvbccllo"}
    payload = test
    return payload
