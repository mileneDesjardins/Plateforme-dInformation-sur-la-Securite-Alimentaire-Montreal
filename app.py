import subprocess

from apscheduler.triggers.cron import CronTrigger
from flask import Flask, g, request, redirect
from flask import render_template
from flask import Flask, jsonify
from database import Database
from flask_json_schema import JsonValidationError, JsonSchema
import atexit

from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__, static_url_path="", static_folder="static")


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()

@app.errorhandler(JsonValidationError)
def validation_error(e):
    errors = [validation_error.message for validation_error in e.errors]
    return jsonify({'error': e.message, 'errors': errors}), 400


@app.route('/')
def index():
    return render_template('index.html')

#A2
@app.route('/search', methods=['GET'])
def search():
    db = Database.get_db()
    keywords = request.args.get('search')
    results = db.search(keywords)
    return render_template('/results.html', keywords=keywords, results=results)

#A3
def extract_and_update_data():
    # Appeler le script de téléchargement et d'insertion des données
    subprocess.run(["python", "telechargement.py"])


scheduler = BackgroundScheduler()
scheduler.add_job(func=extract_and_update_data,
                  trigger=CronTrigger(hour=0,
                                      minute=0))  # déclenchée à minuit (0 heure, 0 minute)
scheduler.start()  # démarre le planificateur

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())

#A4
@app.route('/api/contrevenants', methods=['GET'])
def contrevenants():
    db = Database.get_db()
    date_from = request.args.get('du')
    date_to = request.args.get('au')
    results = db.get_contraventions_between(date_from, date_to)
    if results is None:  # TODO gestion cas vide
        return "", 404
    else:
        return jsonify(results)

@app.route('/api/etablissements', methods=['GET'])
def etablissements():
    db = Database.get_db()
    results = db.get_etablissements_et_nbr_infractions()
    if results is None:
        return "", 404 # TODO gestion cas vide
    else:
        return jsonify(results)


@app.route('/doc')
def doc():
    return render_template('doc.html')


if __name__ == '__main__':
    app.run()
