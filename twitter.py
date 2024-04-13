import base64
import hashlib
import hmac
import os
import re
import time
import uuid

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

    status = "ok!"
    return update_status(status, access_token, access_token_secret)


def update_status(status, access_token, access_token_secret):
    url = 'https://api.twitter.com/1.1/statuses/update.json'
    method = 'POST'

    oauth_params = {
        "oauth_consumer_key": consumer_key,
        "oauth_nonce": generate_nonce(),
        "oauth_signature_method": "HMAC-SHA1",
        "oauth_timestamp": generate_timestamp(),
        "oauth_token": session.get("oauth_token"),
        "oauth_version": "1.0",
    }

    params = '&'.join([f'{k}={v}' for k, v in oauth_params.items()])
    signature = generate_signature(consumer_secret, access_token_secret, url,
                                   params, method)

    headers = {
        "Authorization": f'OAuth oauth_consumer_key="{consumer_key}",'
                         f' oauth_nonce="{oauth_params["oauth_nonce"]}",'
                         f' oauth_signature="{requests.utils.quote(signature, safe="")}", '
                         f'oauth_signature_method="HMAC-SHA1",'
                         f' oauth_timestamp="{oauth_params["oauth_timestamp"]}",'
                         f' oauth_token="{access_token}", oauth_version="1.0"',
    }

    payload = {
        'status': status,
    }

    response = requests.post(url, headers=headers, data=payload)
    return response.json()


def generate_nonce():
    return str(uuid.uuid4())


def generate_timestamp():
    return str(int(time.time()))


def generate_signature(consumer_secret, access_token_secret, url, params,
                       method):
    key = consumer_secret + "&" + access_token_secret
    signature_base_string = '&'.join(
        [method.upper(), requests.utils.quote(url, safe=''),
         requests.utils.quote(params, safe='')])
    hashed = hmac.new(key.encode(), signature_base_string.encode(),
                      hashlib.sha1)
    signature = base64.b64encode(hashed.digest()).decode()
    return signature
