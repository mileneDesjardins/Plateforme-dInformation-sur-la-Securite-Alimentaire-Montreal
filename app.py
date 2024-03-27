import hashlib
import json

import sqlite3

import os

import subprocess
import uuid

from apscheduler.triggers.cron import CronTrigger
from flask import Flask, g, request, redirect, Response, session, url_for
from flask import render_template
from flask import Flask, jsonify

from IDRessourceNonTrouve import IDRessourceNonTrouve

from flask.cli import load_dotenv

from database import Database

from flask_json_schema import JsonValidationError, JsonSchema
import atexit
import xml.etree.ElementTree as ET

from apscheduler.schedulers.background import BackgroundScheduler

from demande_inspection import DemandeInspection
from schema import inspection_insert_schema, valider_new_user_schema
from user import User

from schema import inspection_insert_schema, contrevenant_update_schema, \
    contravention_update_schema

from authorization_decorator import login_required

load_dotenv()
app = Flask(__name__, static_url_path="", static_folder="static")
schema = JsonSchema(app)
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')


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
    keywords = request.args.get('search')
    print("KEY", keywords)
    if keywords is None or len(keywords) == 0:
        error = "Une erreur est survenue, veuillez réessayer plus tard."
        return render_template('results.html',
                               error=error)
    else:
        results = Database.get_db().search(keywords)
        print("RES", results)
        return render_template('results.html', keywords=keywords,
                               results=results)


@app.route('/plainte')
def plainte():
    script = "/js/script_plainte.js"
    return render_template('plainte.html', script=script)


@app.route('/plainte-envoyee')
def plainte_envoyee():
    return render_template('confirmation_plainte.html')


@app.route('/create-user', methods=['GET', 'POST'])
def create_user():
    titre = 'Création utilisateur'
    db = Database.get_db()
    script = "/js/script_create_user.js"
    if request.method == "GET":
        etablissements = db.get_distinct_etablissements()
        return render_template("create_user.html", titre=titre,
                               etablissements=etablissements, script=script)


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


@app.route('/confirmation-new-user', methods=['GET'])
def confirmation_user():
    titre = 'Création de compte réussie'
    return render_template('confirmation_user.html', titre=titre)


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


@app.route('/disconnection')
@login_required
def disconnection():
    session.clear()  # Supprime toutes les données de la session
    return redirect("/")


def est_incomplet():
    return render_template('connection.html',
                           erreur="Veuillez remplir tous les champs")


def nexiste_pas():
    return render_template('connection.html',
                           erreur="Utilisateur inexistant, veuillez "
                                  "vérifier vos informations")


def obtenir_mdp_hash(mdp, user):
    salt = user[5]
    mdp_hash = hashlib.sha512(str(mdp + salt).encode("utf-8")).hexdigest()
    return mdp_hash


def creer_session(user):
    id_session = uuid.uuid4().hex
    session["id"] = id_session
    session["id_user"] = user[0]
    session["nom_complet"] = user[1]
    session["choix_etablissements"] = user[3]
    return redirect('/', 302)


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


@app.route('/photo/<id_photo>')
def photo(id_photo):
    photo_data = Database.get_db().get_photo(id_photo)
    if photo_data:
        return Response(photo_data, mimetype='application/octet-stream')


@app.route('/confirmation-modifs-user', methods=['GET'])
def confirmation_modifs_user():
    titre = 'Modifications enregistrées'
    return render_template('confirmation_modifs_user.html', titre=titre)


# A3
def extract_and_update_data():
    # Appeler le script de téléchargement et d'insertion des données
    subprocess.run(["python", "telechargement.py"])


scheduler = BackgroundScheduler()
scheduler.add_job(func=extract_and_update_data,
                  trigger=CronTrigger(hour=0,
                                      minute=0))  # déclenchée à minuit (0 heure, 0 minute)
scheduler.start()  # démarre le planificateur

# Shut down the scheduler when exiting the app
atexit.register(lambda: scheduler.shutdown())


@app.route('/search-by-dates/<start>/<end>', methods=['POST'])
def search_by_date(start, end):
    infos_obtenues = request.get_json()
    occurences = count_contraventions(infos_obtenues)
    return render_template('search-by-dates.html', results=occurences,
                           start=start, end=end)


@app.route('/modal-dates/<id_business>/<start>/<end>', methods=['GET'])
def modal_dates(start, end, id_business):
    contrevenant = (Database.get_db().
                    get_contraventions_business_between(start, end,
                                                        id_business))
    return render_template('modal_modifier.html', results=contrevenant)


def count_contraventions(contraventions):
    occurrences = {item['id_business']: {'count': sum(
        1 for c in contraventions if c['id_business'] == item['id_business']),
        'etablissement': item[
            'etablissement']} for item in
        contraventions}
    return occurrences


# A4 TODO rechanger route ?
@app.route('/api/contrevenants/start/<date1>/end/<date2>', methods=['GET'])
def contrevenants(date1, date2):
    db = Database.get_db()
    # TODO valider dates ISO
    results = db.get_contraventions_between(date1, date2)
    return jsonify(results)


# A6 TODO changer pour /api/contrevenant/<nom_etablissement>
@app.route('/api/info-etablissement/<etablissement>', methods=['GET'])
def info_etablissements(etablissement):
    db = Database.get_db()
    # TODO valider
    etablissement = db.get_info_contrevenant_by_name(etablissement)
    return jsonify(etablissement)


@app.route('/api/contrevenants/<id_business>', methods=['PATCH'])
@schema.validate(contrevenant_update_schema)
def modify_contrevenant(id_business):
    modifs_request = request.get_json()
    try:
        Database.get_db().update_contrevenant(id_business, modifs_request)
        modified = Database.get_db().get_info_contrevenant_by_id(id_business)
        return jsonify(modified), 200
    except IDRessourceNonTrouve as e:
        return jsonify("La ressource n'a pu être modifiée.", e.message), 404
    except Exception as e:
        return jsonify(
            "Une erreur est survenue sur le serveur. Veuillez réessayer plus tard.")


@app.route('/api/contraventions',
           methods=['PATCH'])
@schema.validate(contravention_update_schema)
def modify_contravention():
    modifs_requests = request.get_json()
    modified_objects = []
    try:
        db = Database.get_db()
        for modifs_request in modifs_requests:
            id_poursuite = modifs_request.get('id_poursuite')
            db.update_contravention(id_poursuite,
                                    modifs_request)
            modified_objects.append(
                db.get_info_poursuite(id_poursuite))
        return jsonify(modified_objects)
    except IDRessourceNonTrouve as e:
        return jsonify("La ressource n'a pu être modifée.", e.message), 404


@app.route('/api/contraventions/<id_poursuite>',
           methods=['DELETE'])
def delete_contravention(id_poursuite):
    try:
        Database.get_db().delete_contravention(id_poursuite)
        return jsonify("La contravention a bien été supprimée"), 200
    except sqlite3.Error as e:
        return jsonify("Une erreur est survenue :"), 500


@app.route('/api/contrevenant/<id_business>',
           methods=['DELETE'])
def delete_contrevenant(id_business):
    try:
        Database.get_db().delete_contrevenant(id_business)
        return jsonify("Le contrevenant bien été suppimé"), 200
    except sqlite3.Error as e:
        return jsonify("Une erreur est survenue"), 500


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
