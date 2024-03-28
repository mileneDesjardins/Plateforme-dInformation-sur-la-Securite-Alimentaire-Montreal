import atexit
import hashlib
import json
import os
import smtplib
import uuid
import xml.etree.ElementTree as ET
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import yaml
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from flask import (Flask, jsonify, g, request, redirect, Response, session,
                   url_for, render_template)
from flask.cli import load_dotenv
from flask_json_schema import JsonValidationError, JsonSchema

from authorization_decorator import login_required
# from contravention_detector import detect_new_contraventions_and_notify
from database import Database
from demande_inspection import DemandeInspection
from schema import inspection_insert_schema, valider_new_user_schema
from telechargement import download_csv
from user import User

load_dotenv()
app = Flask(__name__, static_url_path="", static_folder="static")
schema = JsonSchema(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
scheduler = BackgroundScheduler()


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
    titre = "Accueil"
    etablissements = Database.get_db().get_distinct_etablissements()
    script = "/js/script_accueil.js"
    print(script)

    if "id" in session:
        id_user = session.get("id_user")
        nom_complet = session.get('nom_complet')
    else:
        nom_complet = None
        id_user = None
    return render_template('index.html',
                           titre=titre, script=script,
                           etablissements=etablissements,
                           nom_complet=nom_complet, id_user=id_user
                           )


# A2
@app.route('/search', methods=['GET'])
def search():
    try:
        keywords = request.args.get('search')
        if keywords is None or len(keywords) == 0:
            print("nice")
        results = Database.get_db().db.search(keywords)
        return render_template('results.html', keywords=keywords,
                               results=results)
    except Exception as e:
        error = "Une erreur est survenue, veuillez réessayer plus tard."
        return render_template('results.html',
                               error=error)


@app.route('/plainte')
def plainte():
    script = "/js/script_plainte.js"
    return render_template('plainte.html', script=script)


@app.route('/plainte-envoyee')
def plainte_envoyee():
    return render_template('confirmation_plainte.html')


# E1
@app.route('/create-user', methods=['GET', 'POST'])
def create_user():
    titre = 'Création utilisateur'
    db = Database.get_db()
    script = "/js/script_create_user.js"
    if request.method == "GET":
        etablissements = db.get_distinct_etablissements()
        return render_template("create_user.html", titre=titre,
                               etablissements=etablissements, script=script)


# E1
@app.route('/api/new-user', methods=['POST'])
@schema.validate(valider_new_user_schema)
def new_user():
    try:
        data = request.get_json()
        db = Database.get_db()

        # Vérifier si le champ choix_etablissements est un tableau non vide
        choix_etablissements = data.get("choix_etablissements", [])
        if not isinstance(choix_etablissements, list) or len(
                choix_etablissements) == 0:
            return jsonify({
                "error": "Le champ choix_etablissements est requis."}), 400

        # Vérifier si les autres champs requis sont présents et non vides
        if "" in (data.get("nom_complet", ""), data.get("courriel", ""),
                  data.get("mdp", "")):
            return jsonify(
                {"error": "Tous les champs sont obligatoires."}), 400

        # Génération du sel de mot de passe
        mdp_salt = uuid.uuid4().hex

        # Récupérer le mot de passe fourni par l'utilisateur
        mdp = data["mdp"]

        # Hachage du mot de passe avec le sel
        mdp_hash = hashlib.sha512(
            str(mdp + mdp_salt).encode("utf-8")).hexdigest()

        new_user = User(data["nom_complet"],
                        data["courriel"],
                        data["choix_etablissements"],
                        mdp_hash,
                        mdp_salt)

        db.create_user(new_user)

        """
        201 Created : Ce code est renvoyé lorsqu'une nouvelle ressource a été 
        créée avec succès.
        """
        return jsonify({"message": "Création de compte réussie"}), 201

    except Exception as e:
        print(e)
        # Si une erreur se produit, renvoyer les données saisies
        return jsonify(
            error="Une erreur interne s'est produite. L'erreur a été "
                  "signalée à l'équipe de développement."), 500


# E1
@app.route('/confirmation-new-user', methods=['GET'])
def confirmation_user():
    titre = 'Création de compte réussie'
    return render_template('confirmation_user.html', titre=titre)


# E2
@app.route('/connection', methods=['GET', 'POST'])
def connection():
    titre = "Connexion"

    if request.method == "GET":
        return render_template("connection.html", titre=titre)
    else:
        courriel = request.form["courriel"]
        mdp = request.form["mdp"]

        if courriel == "" or mdp == "":
            return est_incomplet()

        db = Database.get_db()
        user = db.get_user_login_infos(courriel)
        if user is None:
            return nexiste_pas()

        mdp_hash = obtenir_mdp_hash(mdp, user)

        if mdp_hash == user[4]:
            # Accès autorisé
            return creer_session(user)
        else:
            return render_template('connection.html',
                                   erreur="Connexion impossible, veuillez "
                                          "vérifier vos informations")


# E2
@app.route('/disconnection')
@login_required
def disconnection():
    session.clear()  # Supprime toutes les données de la session
    return redirect("/")


# E2
def est_incomplet():
    return render_template('connection.html',
                           erreur="Veuillez remplir tous les champs")


# E2
def nexiste_pas():
    return render_template('connection.html',
                           erreur="Utilisateur inexistant, veuillez "
                                  "vérifier vos informations")


# E2
def obtenir_mdp_hash(mdp, user):
    salt = user[5]
    mdp_hash = hashlib.sha512(str(mdp + salt).encode("utf-8")).hexdigest()
    return mdp_hash


# E2
def creer_session(user):
    id_session = uuid.uuid4().hex
    session["id"] = id_session
    session["id_user"] = user[0]
    session["nom_complet"] = user[1]
    session["choix_etablissements"] = user[3]
    return redirect('/', 302)


# E2
@app.route('/compte', methods=['GET', 'POST'])
@login_required
def compte():
    titre = 'Compte'
    db = Database()
    id_user = session["id_user"]
    user = db.get_user_by_id(id_user)
    etablissements = db.get_distinct_etablissements()
    choix_etablissements = session.get("choix_etablissements")

    if request.method == 'GET':

        if not user:
            return render_template('404.html'), 404

        # Vérifier si la liste des établissements sélectionnés est vide
        if not choix_etablissements:
            return render_template('404.html'), 404

        # Convertir choix_etablissements en liste d'entiers
        if isinstance(choix_etablissements, str):  # Vérifier le type
            choix_etablissements = json.loads(choix_etablissements)

        return render_template('compte.html', titre=titre,
                               user=user, etablissements=etablissements,
                               choix_etablissements=choix_etablissements)


    elif request.method == 'POST':

        # Récupérer les informations soumises dans le formulaire
        new_etablissements = request.form.getlist('choix_etablissements')

        # Mettre à jour les établissements sélectionnés dans la base de données
        db.update_user_etablissements(id_user, new_etablissements)

        # Mettre à jour les établissements sélectionnés dans la session
        session["choix_etablissements"] = new_etablissements

        nouvelle_photo = request.files.get('photo')

        # Mettre à jour les établissements choisis pour l'utilisateur
        if new_etablissements:
            db.update_user_etablissements(id_user, new_etablissements)
            session["choix_etablissements"] = new_etablissements

        # Enregistrer la nouvelle photo dans la base de données et mettre à jour l'ID de la photo de l'utilisateur
        if nouvelle_photo is not None and nouvelle_photo.filename:
            photo_data = nouvelle_photo.read()
            id_photo = db.create_photo(photo_data)
            if user[6]:
                db.delete_photo(user[
                                    6])  # Supprimer l'ancienne photo de la base de données
            db.update_user_photo(id_user, id_photo)

        # Rediriger vers la page de confirmation des modifications de l'utilisateur
        return redirect(url_for('confirmation_modifs_user'))


# E2
@app.route('/photo/<id_photo>')
def photo(id_photo):
    photo_data = Database.get_db().get_photo(id_photo)
    if photo_data:
        return Response(photo_data, mimetype='application/octet-stream')


# E2
@app.route('/confirmation-modifs-user', methods=['GET'])
def confirmation_modifs_user():
    titre = 'Modifications enregistrées'
    return render_template('confirmation_modifs_user.html', titre=titre)


@app.before_request
def before_request():
    if not request.path.startswith('/static'):
        extract_and_update_data(session)
        detect_new_contraventions(session)


def extract_and_update_data(session):
    print("Extraction et mise à jour des données en cours...")

    # Code pour extraire et mettre à jour les données
    download_csv()

    print("Extraction et mise à jour des données terminées.")

    # Appel à la fonction de détection et de notification des nouvelles contraventions
    new_contraventions = detect_new_contraventions(session)
    return new_contraventions


def detect_new_contraventions(session):
    try:
        db = Database.get_db()

        # Récupérer la dernière date de vérification des nouvelles contraventions
        last_check_date = session.get("last_check_date")

        # S'il s'agit de la première vérification, utiliser une date antérieure pour obtenir toutes les contraventions
        if last_check_date is None:
            last_check_date = datetime.min

        # Récupérer toutes les contraventions ajoutées depuis la dernière vérification
        new_contraventions = db.get_contraventions_between(
            last_check_date, datetime.now())

        # Mettre à jour la dernière date de vérification
        session["last_check_date"] = datetime.now()

        # Si de nouvelles contraventions ont été détectées, appeler la fonction notify_users
        if new_contraventions:
            notify_users(new_contraventions)

        # Retourner la liste des nouvelles contraventions
        return new_contraventions
    except Exception as e:
        # Enregistrer l'erreur ou la gérer de manière appropriée
        print(f"Une erreur s'est produite : {e}")
        return []


def notify_users(new_contraventions):
    db = Database.get_db()
    users = db.get_all_users()
    # Lecture des adresses des destinataires depuis le fichier de configuration YAML
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        destinataires_config = config[
            'destinataires']  # Supposons que vous avez une clé 'destinataires' dans votre fichier de configuration

    # Initialiser un ensemble pour stocker tous les destinataires
    destinataires = set()

    # Parcourir chaque nouvelle contravention
    for contravention in new_contraventions:
        # Récupérer les destinataires spécifiques à cette contravention
        destinataires_contravention = set()

        # Parcourir chaque utilisateur
        for user in users:
            # Vérifier si cette contravention est surveillée par l'utilisateur
            if contravention in user.choix_etablissements:
                # Ajouter l'utilisateur à la liste des destinataires de cette contravention
                destinataires_contravention.add(user.courriel)

        # Ajouter les destinataires spécifiques à cette contravention à l'ensemble global de destinataires
        destinataires.update(destinataires_contravention)

    # Ajouter les destinataires du fichier de configuration YAML, s'il y en a
    if destinataires_config:
        destinataires.update(destinataires_config)

    # Envoyer un courriel à tous les destinataires pour chaque contravention
    for destinataire in destinataires:
        send_courriel(destinataire, [
            "Nouvelle contravention à l'établissement {}".format(
                contravention)])


def send_courriel(destinataires, contraventions):
    # Lecture de l'adresse de l'expéditeur et d'autres informations depuis le fichier de configuration YAML
    with open('config.yaml', 'r') as file:
        config = yaml.safe_load(file)
        expediteur = config['expediteur']
        smtp_server = config['smtp_server']
        smtp_port = config['smtp_port']
        smtp_courriel = config['smtp_courriel']
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
            server.login(smtp_courriel, smtp_password)
            server.send_message(msg)


# Ajouter les tâches planifiées au planificateur
scheduler.add_job(func=extract_and_update_data,
                  trigger=IntervalTrigger(seconds=5))
scheduler.add_job(func=detect_new_contraventions,
                  trigger=IntervalTrigger(seconds=5))

# TODO METTRE POUR MINUIT
# scheduler.add_job(func=extract_and_update_data,
#                   trigger=CronTrigger(hour=0, minute=0))
# scheduler.add_job(func=detect_new_contraventions_and_notify,
#                   trigger=CronTrigger(hour=0, minute=0))


# Démarrez le planificateur
scheduler.start()

# Enregistrez la fermeture du planificateur à la sortie
atexit.register(lambda: scheduler.shutdown())


# A4 TODO route ok ?
@app.route('/api/contrevenants/start/<date1>/end/<date2>', methods=['GET'])
def contrevenants(date1, date2):
    db = Database.get_db()
    # TODO valider dates ISO ?
    results = db.get_contraventions_between(date1, date2)
    return (results)


# A6
@app.route('/api/info-etablissement/<etablissement>', methods=['GET'])
def info_etablissements(etablissement):
    db = Database.get_db()
    # TODO valider
    etablissement = db.get_info_etablissement(etablissement)
    return jsonify(etablissement)


@app.route('/modal', methods=['POST'])
def modal_etablissements():
    """ NOTE pour documentation : Recoit JSON de l'etablissement'"""
    infos_obtenues = request.get_json()
    return render_template('modal_etablissement.html',
                           results=infos_obtenues)


@app.route('/api/demande-inspection', methods=['POST'])
@schema.validate(inspection_insert_schema)
def demande_inspection():
    try:
        demande = request.get_json()
        nouvelle_demande = DemandeInspection(None, demande["etablissement"],
                                             demande["adresse"],
                                             demande["ville"],
                                             demande["date_visite"],
                                             demande["nom_complet_client"],
                                             demande["description"])
        print(nouvelle_demande.description)
        Database.get_db().insert_demande_inspection(nouvelle_demande)
        return "Utilisateur ajouté", 201
    except Exception as e:
        return jsonify(
            error="Une erreur est survenue sur le serveur. Veuillez "
                  "réessayer plus tard"), 500


@app.route('/api/demande-inspection/<id_demande>', methods=['DELETE'])
@schema.validate(inspection_insert_schema)
def supprimer_inspection(id_demande):
    try:
        demande = Database.get_db().get_demande_inspection(id_demande)
        if demande is None:
            return jsonify(
                "Le ID " + id_demande + " ne correspond à aucune demande "
                                        "d\'inspection."), 404
        Database.get_db().delete_demande_inspection(demande)
        return jsonify("La demande a bien été supprimée."), 200
    except Exception as e:
        return jsonify(
            error="Une erreur est survenue sur le serveur. Veuillez "
                  "réessayer plus tard"), 500


# C1
@app.route('/api/etablissements', methods=['GET'])
def etablissements():
    db = Database.get_db()
    results = db.get_etablissements_et_nbr_infractions()
    if results is None:
        return "", 404  # TODO gestion cas vide
    else:
        return jsonify(results)


# C2
@app.route('/api/etablissements/xml',
           methods=['GET'])
def etablissements_xml():
    db = Database.get_db()
    results = db.get_etablissements_et_nbr_infractions()
    if results is None:
        return "", 404  # TODO gestion cas vide
    else:
        # Créer l'élément racine du XML
        root = ET.Element("etablissements")

        # Parcourir les résultats et les ajouter au XML
        for result in results:
            etablissement = ET.SubElement(root, "etablissement")
            nom = ET.SubElement(etablissement, "nom")
            nom.text = result[0]  # Insérer le nom de l'établissement
            nbr_infractions = ET.SubElement(etablissement, "nbr_infractions")
            nbr_infractions.text = str(
                result[1])  # Insérer le nombre d'infractions

        # Créer un objet Response contenant le XML
        xml_response = ET.tostring(root, encoding="utf-8")
        return Response(xml_response, content_type="application/xml")


# C3
@app.route('/api/etablissements/csv', methods=['GET'])
def etablissements_csv():
    db = Database.get_db()
    results = db.get_etablissements_et_nbr_infractions()
    if results is None:
        return "", 404  # TODO gestion cas vide
    else:
        # Créer une liste de dictionnaires pour les résultats
        data = []
        for result in results:
            data.append({
                'Etablissement': result[0],
                'Nbr_infractions': result[1]
            })

        # Créer une réponse CSV à partir des données
        csv_data = ', '.join(data[0].keys()) + '\n'  # Écrire les noms de
        # colonnes
        for entry in data:
            csv_data += ', '.join(map(str, entry.values())) + '\n'  # Écrire
            # les valeurs de chaque entrée

        # Créer un objet Response contenant le CSV
        return Response(csv_data, content_type="text/csv")


@app.route('/doc')
def doc():
    return render_template('doc.html')


if __name__ == '__main__':
    app.run()
