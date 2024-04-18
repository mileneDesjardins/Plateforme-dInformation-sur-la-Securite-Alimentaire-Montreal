import csv
import os
import tempfile
import urllib.request
from flask import Flask
from database import Database

app = Flask(__name__)

def import_csv():
    with app.app_context():  # This creates a Flask application context
        db = Database.get_db()
        url = 'https://data.montreal.ca/dataset/05a9e718-6810-4e73-8bb9-5955efeb91a0/resource/7f939a08-be8a-45e1-b208-d8744dca8fc6/download/violations.csv'
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        response = urllib.request.urlopen(req)

        # Create a temporary file to store the CSV content
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(response.read())

        # Read the content of the CSV file
        with open(temp_file.name, 'r', encoding='utf-8') as csv_file:
            contenu = csv.reader(csv_file)
            db.insert_contraventions_from_csv(csv_file.name)

        # Clean up the temporary file
        os.unlink(temp_file.name)

if __name__ == "__main__":
    import_csv()
