import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yaml

from TokenManager import TokenManager
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

            # TODO detect_modifications()

            # Mettre à jour le temps de la dernière importation
            db.update_last_import_time()

            time.sleep(5)


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

            notify(new_contraventions)

        # Mettre à jour le temps de la dernière importation
        db.update_last_import_time()

        return new_contraventions
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        return []


def notify(new_contraventions):
    db = Database.get_db()
    users = db.get_all_users()
    destinataires_users = dict()
    link_tokens = {}  # Dictionnaire pour stocker les tokens par utilisateur

    if new_contraventions is None:
        print("Aucune nouvelle contravention à notifier.")
        return

    else:
        try:
            with open('config.yaml', 'r') as file:
                config_data = yaml.safe_load(file)
                sender_email = config_data['sender_email']
                receiver_email = config_data['receiver_email']

        except Exception as e:
            print(
                f"Une erreur s'est produite lors de la lecture du fichier YAML : {e}")

        # Parcourir chaque utilisateur
        token_manager = TokenManager()
        for user in users:
            courriel = user[2]
            choix_etablissements = eval(user[3])

            # Initialiser les contraventions surveillées par cet utilisateur
            contraventions_surveillees = set()

            # Parcourir chaque nouvelle contravention
            for contravention in new_contraventions:
                id_business = contravention[1]
                etablissement = contravention[6]

                # Vérifier si cette contravention est surveillée par l'utilisateur
                if id_business in choix_etablissements:
                    contraventions_surveillees.add(contravention)

                    # Générer le token pour cet utilisateur
                    token = token_manager.generate_token(id_business,
                                                         courriel,
                                                         etablissement)
                    link_tokens[(courriel, id_business)] = (
                        f"http://localhost:5000/unsubscribe-page/{token}")

            if contraventions_surveillees:
                # Ajouter l'utilisateur et ses contraventions surveillées à la liste
                destinataires_users[courriel] = contraventions_surveillees

        # Envoyer l'e-mail à chaque utilisateur
        send_courriel(sender_email, receiver_email, new_contraventions,
                      destinataires_users, link_tokens)


def send_courriel(sender_email, receiver_email, new_contraventions,
                  destinataires_users, link_tokens):
    port = 1025
    smtp_server = 'localhost'

    try:
        with (smtplib.SMTP(smtp_server, port) as server):

            # Envoyer un courriel au courriel dans le fichier YAML
            message_body = prepare_email_body(new_contraventions, False)
            message_content = prepare_message_content(message_body,
                                                      sender_email,
                                                      receiver_email)
            server.sendmail(sender_email, [receiver_email],
                            message_content.as_string())

            # Envoyer un courriel à chaque destinataire utilisateur pour ses contraventions
            for email_destinataire, contraventions in destinataires_users.items():
                # Initialiser un message global pour cet utilisateur
                global_message_body = ""
                for contravention in contraventions:
                    id_business = contravention[
                        1]
                    # Générer le corps du message pour chaque contravention, incluant le lien de désinscription
                    individual_message_body = prepare_email_body(
                        [contravention], unsubscribe_link=True,
                        link_token=link_tokens.get(
                            (email_destinataire, id_business)))
                    global_message_body += individual_message_body

                # Préparer et envoyer le message global à l'utilisateur
                message_content = prepare_message_content(global_message_body,
                                                          sender_email,
                                                          email_destinataire)
                server.sendmail(sender_email, email_destinataire,
                                message_content.as_string())

    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {e}")


def prepare_email_body(contraventions, unsubscribe_link=True,
                       link_token=None):
    message_body = "<h3>Nouvelles contraventions!</h3>"
    for contravention in contraventions:
        etablissement = contravention[6]
        date = contravention[2]
        description = contravention[3]

        message_body += f"<p>Établissement: {etablissement}</p>"
        message_body += "<ul>"
        message_body += f"<li>Date: {date}</li>"
        message_body += f"<li>Description: {description}</li>"
        message_body += "</ul>"

        if unsubscribe_link and link_token is not None:
            message_body += (f"<p>Pour vous désabonner de cet établissement, "
                             f"veuillez "
                             f"cliquer "
                             f"sur le lien suivant : <a href='"
                             f"{link_token}'>Se désabonner</a></p>")
            print(message_body)

    return message_body


def prepare_message_content(message_body, sender_email, receiver_email):
    # Créer le message MIME multipart
    msg_content = MIMEMultipart()
    msg_content['Subject'] = 'Nouvelles contraventions - Ville de Montréal'
    msg_content['From'] = sender_email
    msg_content['To'] = receiver_email
    msg_content.attach(MIMEText(message_body, 'html'))
    return msg_content
