from flask import Flask
import os

app = Flask(__name__, static_url_path="", static_folder="static")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['SITE_USER'] = os.getenv('SITE_USER')
app.config['SITE_PASS'] = os.getenv('SITE_PASS')
app.config['CLIENT_ID'] = os.getenv('CLIENT_ID')
app.config['CLIENT_SECRET'] = os.getenv('CLIENT_SECRET')
app.config['API_KEY'] = os.getenv('API_KEY')
app.config['API_SECRET'] = os.getenv('API_SECRET')
app.config['ACCESS_TOKEN'] = os.getenv('ACCESS_TOKEN')
app.config['ACCESS_TOKEN_SECRET'] = os.getenv('ACCESS_TOKEN_SECRET')
app.config['REDIRECT_URI'] = os.getenv('REDIRECT_URI')
app.secret_key = os.urandom(50)

