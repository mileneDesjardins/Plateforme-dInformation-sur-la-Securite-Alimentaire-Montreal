import hashlib
import json
import subprocess
import uuid

from apscheduler.triggers.cron import CronTrigger
from flask import Flask, g, request, redirect, Response, session
from flask import render_template
from flask import Flask, jsonify
from database import Database
from flask_json_schema import JsonValidationError, JsonSchema
import atexit
import xml.etree.ElementTree as ET

from apscheduler.schedulers.background import BackgroundScheduler

from schema import inspection_insert_schema

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
    return render_template('index.html', etablissements=etablissements)


# A2
@app.route('/search', methods=['GET'])
def search():
    db = Database.get_db()
    keywords = request.args.get('search')
    results = db.search(keywords)
    return render_template('results.html', keywords=keywords, results=results)


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
    if request.method == "GET":
        return render_template("create_user.html", titre=titre)
    else:
        prenom, nom, courriel, choix_etablissements, mdp = (obtenir_infos())

    # Vérifier que les champs ne soient pas vides
    if (prenom == "" or nom == "" or courriel == "" or not
    choix_etablissements or mdp == ""):
        return render_template("create_user.html", titre=titre,
                               erreur="Tous les champs sont obligatoires.")

    # Génération d'un salt et hachage du mot de passe
    mdp_salt = uuid.uuid4().hex
    mdp_hash = hashlib.sha512(
        str(mdp + mdp_salt).encode("utf-8")).hexdigest()

    # Stockage des informations de l'utilisateur
    db = Database.get_db()
    db.create_user(prenom, nom, courriel, choix_etablissements, mdp_hash,
                   mdp_salt)

    # Redirection vers une page de confirmation
    return redirect('/confirmation_user', 302)


def obtenir_infos():
    prenom = request.form['prenom']
    nom = request.form['nom']
    courriel = request.form["courriel"]
    choix_etablissements = request.form.getlist(
        "choix_etablissements")  # récupérer les valeurs d'un champ de form
    # pour une liste de valeurs
    mdp = request.form["mdp"]
    # photo = request.files["photo"]
    # photo_data = photo.stream.read()
    return prenom, nom, courriel, choix_etablissements, mdp


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


# A4 TODO route ok ?
@app.route('/api/contrevenants/start/<date1>/end/<date2>', methods=['GET'])
def contrevenants(date1, date2):
    db = Database.get_db()
    # TODO valider dates ISO ?
    results = db.get_contraventions_between(date1, date2)
    return jsonify(results)


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
    demande = request.get_json()
    return "TODO"  # TODO


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
