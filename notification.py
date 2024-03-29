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

            notify(new_contraventions)

        # Mettre à jour le temps de la dernière importation
        db.update_last_import_time()

        return new_contraventions
    except Exception as e:
        print(f"Une erreur s'est produite : {e}")
        return []


def notify(new_contraventions):

    # db = Database.get_db()
    # users = db.get_all_users()
    # destinataires_users = set()

    if new_contraventions is None:
        print("Aucune nouvelle contravention à notifier.")
        return

    try:
        with open('config.yaml', 'r') as file:
            config_data = yaml.safe_load(file)
            sender_email = config_data['sender_email']
            receiver_email = config_data['receiver_email']
            print(config_data)
    except Exception as e:
        print(
            f"Une erreur s'est produite lors de la lecture du fichier YAML : {e}")


    send_courriel(sender_email, receiver_email, new_contraventions)

    # # Parcourir chaque nouvelle contravention
    # for contravention in new_contraventions:
    #     # Parcourir chaque utilisateur
    #     for user in users:
    #         choix_etablissements = eval(user[3])
    #         # Vérifier si cette contravention est surveillée par l'utilisateur
    #         if contravention[1] in choix_etablissements:
    #             # Ajouter l'utilisateur à la liste des destinataires supplémentaires
    #             destinataires_users.add((user[2], choix_etablissements))  #
    #             # courriel,
    #             # choix_etablissements
    #
    #     # Vérifier si des destinataires ont été ajoutés
    #     if destinataires_users:
    #         try:
    #             # Envoyer un courriel à l'adresse spécifiée dans le fichier YAML et aux utilisateurs concernés
    #             send_courriel(sender_email, receiver_email,
    #                           destinataires_users, new_contraventions)
    #         except Exception as e:
    #             print(f"Erreur lors de l'envoi de l'e-mail : {e}")


def send_courriel(sender_email, receiver_email, new_contraventions):
    port = 1025
    smtp_server = 'localhost'

    try:
        with (smtplib.SMTP(smtp_server, port) as server):

            # Envoyer un courriel au courriel dans le fichier YAML
            message_body_all = "<h3>Nouvelles contraventions!</h3>"
            for contravention in new_contraventions:
                message_body_all += f"<p>Établissement: {contravention[6]}</p>"
                message_body_all += "<ul>"
                message_body_all += f"<li>Date: {contravention[2]}</li>"
                message_body_all += f"<li>Description: {contravention[3]}</li>"
                message_body_all += "</ul>"

            msg_all = MIMEMultipart()
            msg_all['Subject'] = 'Nouvelles contraventions - Ville de Montréal'
            msg_all['From'] = sender_email
            msg_all['To'] = receiver_email
            msg_all.attach(MIMEText(message_body_all, 'html'))
            server.sendmail(sender_email, [receiver_email],
                            msg_all.as_string())

            # Envoyer un courriel à chaque destinataire user avec les
            # contraventions qu'ils surveillent
            # for destinataire in destinataires_users:
            #     email_destinataire = destinataire[0]
            #     message_body = ("<h3>Nouvelles contraventions!</h3>")
            #     contraventions_destinataire = [contravention for contravention
            #                                    in new_contraventions if
            #                                    contravention[1] in
            #                                    destinataire[1]]
            #
            #     for contravention in contraventions_destinataire:
            #         etablissement = contravention[6]
            #         message_body += f"<p>Établissement: {etablissement}</p>"
            #         message_body += "<ul>"
            #         message_body += f"<li>Date: {contravention[2]}</li>"
            #         message_body += f"<li>Description: {contravention[3]}</li>"
            #         message_body += "</ul>"
            #
            #     msg = MIMEMultipart()
            #     msg['Subject'] = 'Nouvelles contraventions - Ville de Montréal'
            #     msg['From'] = sender_email
            #     msg['To'] = email_destinataire
            #
            #     # Attach the message body
            #     msg.attach(MIMEText(message_body, 'html'))
            #
            #     server.sendmail(sender_email,
            #                     [email_destinataire],
            #                     msg.as_string())

    except Exception as e:
        print(f"Erreur lors de l'envoi de l'e-mail : {e}")
