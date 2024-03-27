import hashlib
import json
import sqlite3
import subprocess
import uuid
from urllib.parse import unquote

from apscheduler.triggers.cron import CronTrigger
from flask import g, request, redirect, Response, session
from flask import render_template
from flask import Flask, jsonify

from IDRessourceNonTrouve import IDRessourceNonTrouve
from database import Database, _build_contravention
from flask_json_schema import JsonValidationError, JsonSchema
import atexit
import xml.etree.ElementTree as ET

from apscheduler.schedulers.background import BackgroundScheduler

from demande_inspection import DemandeInspection
from schema import inspection_insert_schema, contrevenant_update_schema, \
    contravention_update_schema

app = Flask(__name__, static_url_path="", static_folder="static")
schema = JsonSchema(app)


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
    etablissements = Database.get_db().get_distinct_etablissements()
    script = "/js/script_accueil.js"
    return render_template('index.html', etablissements=etablissements,
                           script=script)


# A2
@app.route('/search', methods=['GET'])
def search():
    try:
        keywords = request.args.get('search')
        if keywords is None or len(keywords) == 0:
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

        if mdp_hash == user[3]:
            # Accès autorisé
            return creer_session(user)
        else:
            return render_template('connection.html',
                                   erreur="Connexion impossible, veuillez "
                                          "vérifier vos informations")


def est_incomplet():
    return render_template('connection.html',
                           erreur="Veuillez remplir tous les champs")


def nexiste_pas():
    return render_template('connection.html',
                           erreur="Utilisateur inexistant, veuillez "
                                  "vérifier vos informations")


def obtenir_mdp_hash(mdp, user):
    salt = user[3]
    mdp_hash = hashlib.sha512(str(mdp + salt).encode("utf-8")).hexdigest()
    return mdp_hash


def creer_session(user):
    id_session = uuid.uuid4().hex
    session["id"] = id_session
    session["id_user"] = user[0]
    session["prenom"] = user[1]
    session["nom"] = user[2]
    session["id_photo"] = user[7]
    return redirect('/', 302)


@app.route('/create-user', methods=['GET', 'POST'])
def create_user():
    titre = 'Creation utilisateur'
    db = Database.get_db()
    if request.method == "GET":
        etablissements = db.get_distinct_etablissements()
        return render_template("create_user.html", titre=titre,
                               etablissements=etablissements)
    else:
        nom_complet, courriel, choix_etablissements, mdp = (obtenir_infos())

    # Vérifier que les champs ne soient pas vides
    if (nom_complet == "" or courriel == "" or not
    choix_etablissements or mdp == ""):
        return render_template("create_user.html", titre=titre,
                               erreur="Tous les champs sont obligatoires.")

    # Génération d'un salt et hachage du mot de passe
    mdp_salt = uuid.uuid4().hex
    mdp_hash = hashlib.sha512(
        str(mdp + mdp_salt).encode("utf-8")).hexdigest()

    # Stockage des informations de l'utilisateur

    db.create_user(nom_complet, courriel, choix_etablissements, mdp_hash,
                   mdp_salt)

    # Redirection vers une page de confirmation
    return redirect('/confirmation_user', 302)


def obtenir_infos():
    nom_complet = request.form['nom_complet']
    courriel = request.form["courriel"]
    choix_etablissements = request.form.getlist(
        "choix_etablissements")  # récupérer les valeurs d'un champ de form
    # pour une liste de valeurs
    mdp = request.form["mdp"]
    # photo = request.files["photo"]
    # photo_data = photo.stream.read()
    return nom_complet, courriel, choix_etablissements, mdp


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
            db.update_info_contravention(id_poursuite,
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
