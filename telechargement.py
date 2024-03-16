import csv
import urllib.request
import tempfile
import os

from flask import Flask

from database import Database
from app import app # TODO Jai essaye ca au lieu de app name, tu me diras ce que tu en penses


# Création de l'objet cursor
with app.app_context():
    db = Database.get_db()

    url = 'https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv'

    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)

    # Créer un fichier temporaire pour stocker le contenu CSV
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(response.read())

    # Lecture du contenu du fichier CSV
    with open(temp_file.name, 'r', encoding='utf-8') as csv_file:
        contenu = csv.reader(csv_file)

        # Appel de la fonction pour insérer les contraventions depuis le CSV
        db.insert_contraventions_from_csv(csv_file.name)

    # Nettoyer le fichier temporaire
    os.unlink(temp_file.name)
