from flask import Flask, g

from database import Database

app = Flask(__name__)

import telechargement


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
