import csv
import time

from database import Database


def import_csv():
    # Création de l'objet Database
    db = Database()
    # Spécifiez le chemin d'accès à votre fichier CSV
    file_path = r"/mnt/c/Users/Public/violations.csv"

    try:
        # Ouverture du fichier CSV
        with open(file_path, 'r', encoding='utf-8') as csv_file:
            contenu = csv.reader(csv_file)

            # Appel de la fonction pour insérer les contraventions depuis le CSV
            db.insert_contraventions_from_csv(csv_file.name)

        print("Importation des données CSV réussie.")
    except Exception as e:
        print(
            f"Une erreur s'est produite lors de l'importation du fichier CSV : {e}")



