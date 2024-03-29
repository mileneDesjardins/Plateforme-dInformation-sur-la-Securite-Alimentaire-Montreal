from flask import Flask
import os

app = Flask(__name__, static_url_path="", static_folder="static")
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
