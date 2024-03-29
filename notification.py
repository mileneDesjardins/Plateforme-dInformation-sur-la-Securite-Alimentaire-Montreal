import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yaml

from app import app
from database import Database
from download import import_csv


def extract_and_update_data():
    with app.app_context():
        db = Database.get_db()
        db.update_last_import_time()

        while True:
            print("Extraction et mise à jour des données en cours...")

            # Code pour extraire et mettre à jour les données
            import_csv()

            print("Extraction et mise à jour des données terminées.")

            # Appel à la fonction pour détecter les nouvelles contraventions
            _ = detect_new_contraventions()

            # Mettre à jour le temps de la dernière importation
            db.update_last_import_time()

            time.sleep(10)


def detect_new_contraventions():
    try:
        db = Database.get_db()
        # Obtention de l'heure de la dernière importation
        last_import_time = db.get_last_import_time()

        # Récupérer les nouvelles contraventions depuis la dernière importation
        new_contraventions = db.get_new_contraventions(last_import_time)

        # Si de nouvelles contraventions ont été détectées
        if new_contraventions:
            num_new_contraventions = len(new_contraventions)
            print(
                f"{num_new_contraventions} nouvelles contraventions détectées :")
            for contravention in new_contraventions:
                print(f"- {contravention[6]}")
            # Include a message mentioning the number of contraventions detected
            print(
                f"Nombre total de nouvelles contraventions détectées : {num_new_contraventions}")

            notify_users(new_contraventions)

        # Mettre à jour le temps de la dernière importation
        db.update_last_import_time()

        return new_contraventions
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        return []


def notify_users(new_contraventions):
    db = Database.get_db()
    users = db.get_all_users()

    # Appeler la fonction pour créer le fichier YAML
    create_yaml_config(users)

    # Lire les adresses des destinataires depuis le fichier de configuration YAML
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        # Récupérer les adresses des destinataires du fichier YAML, en gérant le cas où la clé 'destinataires' peut ne pas exister
        destinataires_config = config.get('destinataires', [])

    # Initialiser un ensemble pour stocker tous les destinataires
    destinataires = set()

    # Parcourir chaque nouvelle contravention
    for contravention in new_contraventions:
        # Récupérer les destinataires spécifiques à cette contravention
        destinataires_contravention = set()

        # Parcourir chaque utilisateur
        for user in users:
            choix_etablissements = eval(user[3])
            # Vérifier si cette contravention est surveillée par l'utilisateur
            if contravention[1] in choix_etablissements:
                # Ajouter l'utilisateur à la liste des destinataires de cette contravention
                destinataires_contravention.add(user[2])

        # Ajouter les destinataires spécifiques à cette contravention à l'ensemble global de destinataires
        destinataires.update(destinataires_contravention)

    # Ajouter les destinataires du fichier de configuration YAML, s'il y en a
    destinataires.update(destinataires_config)

    # Envoyer un courriel à tous les destinataires pour chaque contravention
    for destinataire in destinataires:
        for contravention in new_contraventions:
            # Construire le message
            message = "Nouvelle contravention à l'établissement {} - {}".format(
                contravention[6], contravention[3])
            # Envoyer l'e-mail
            send_courriel(destinataire, [message])


def send_courriel(destinataires, contraventions):
    # Lecture de l'adresse de l'expéditeur et d'autres informations depuis le fichier de configuration YAML
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        expediteur = config['expediteur']
        smtp_server = config['smtp_server']
        smtp_port = config['smtp_port']
        smtp_email = config['smtp_email']
        smtp_password = config['smtp_password']

    # Boucle sur tous les destinataires pour envoyer le courriel à chacun
    for destinataire in destinataires:
        # Construction du message
        msg = MIMEMultipart()
        msg['From'] = expediteur
        msg['To'] = destinataire
        msg['Subject'] = 'Nouvelles contraventions détectées'

        body = "\n".join(contraventions)
        msg.attach(MIMEText(body, 'plain'))

        # Envoi du message
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(smtp_email, smtp_password)
            server.send_message(msg)


def create_yaml_config(users):
    # Utiliser un ensemble pour stocker les adresses e-mail uniques
    unique_destinataires = set()

    # Parcourir les utilisateurs et ajouter les adresses e-mail uniques à l'ensemble
    for user in users:
        unique_destinataires.add(user[2])

    # Convertir l'ensemble en liste
    destinataires = list(unique_destinataires)

    # Données à stocker dans le fichier YAML
    data = {
        'destinataires': destinataires
    }

    # Chemin d'accès au fichier YAML
    yaml_file_path = r"C:\Users\Public\PycharmProjects\Projet_session\config.yaml"

    try:
        # Écriture des données dans le fichier YAML
        with open(yaml_file_path, 'w') as file:
            yaml.dump(data, file)
        print("Fichier YAML créé avec succès.")
    except Exception as e:
        print(f"Erreur lors de la création du fichier YAML : {e}")
