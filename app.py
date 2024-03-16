import telechargement
from flask import Flask, g, request, redirect
from flask import render_template
from flask import Flask, jsonify
from database import Database

app = Flask(__name__, static_url_path="", static_folder="static")


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        g._database = Database()
    return g._database


def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()


if __name__ == '__main__':
    app.run()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/search', methods=['GET'])
def search():
    keywords = request.args.get('search')
    results = get_db().search(keywords)
    return render_template('/results.html', keywords=keywords, results=results)


@app.route('/api/contrevenants', methods=['GET'])
def contrevenants():
    date_from = request.args.get('du')
    date_to = request.args.get('au')
    results = get_db().get_contraventions_between(date_from, date_to)
    if results is None:  # TODO ou juste 200 avec json vide ?
        return "", 404
    else:
        return jsonify(results)


@app.route('/doc')
def doc():
    return render_template('doc.html')
