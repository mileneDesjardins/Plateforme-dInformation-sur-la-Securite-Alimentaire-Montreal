import yaml
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


# def notify_users_about_new_contraventions(new_contraventions):
#     users = db.get_all_users()  # Récupérer tous les utilisateurs depuis la base de données
#     for user in users:
#         for choice in user.choix_etablissements:
#             if choice in new_contraventions:
#                 send_courriel(user.courriel, ["Nouvelle contravention à l'établissement {}".format(choice)])
#                 break  # Une fois qu'une correspondance est trouvée pour un utilisateur, pas besoin de continuer à chercher
#
# # Exemple de récupération de nouvelles contraventions (vous devrez adapter cette partie selon votre logique)
# new_contraventions = [6119, 9150]
#
# # Notifier les utilisateurs sur les nouvelles contraventions
# notify_users_about_new_contraventions(new_contraventions)
#
#
# def send_courriel(destinataire, contraventions):
#     # Lecture de l'adresse du destinataire depuis le fichier de configuration YAML
#     with open('config.yaml', 'r') as file:
#         config = yaml.safe_load(file)
#         expediteur = config['expediteur']
#         smtp_server = config['smtp_server']
#         smtp_port = config['smtp_port']
#         smtp_courriel = config['smtp_courriel']
#         smtp_password = config['smtp_password']
#
#     # Construction du message
#     msg = MIMEMultipart()
#     msg['From'] = expediteur
#     msg['To'] = destinataire
#     msg['Subject'] = 'Nouvelles contraventions detectees'
#
#     body = "\n".join(contraventions)
#     msg.attach(MIMEText(body, 'plain'))
#
#     # Envoi du message
#     with smtplib.SMTP(smtp_server, smtp_port) as server:
#         server.starttls()
#         server.login(smtp_courriel, smtp_password)
#         server.send_message(msg)
