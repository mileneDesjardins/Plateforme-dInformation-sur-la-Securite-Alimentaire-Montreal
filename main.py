import hashlib
import json
import os
import sqlite3
import threading
import uuid
import xml.etree.ElementTree as ET

from flask import (jsonify, g, request, redirect, Response, session,
                   url_for, render_template)
from flask.cli import load_dotenv
from flask_json_schema import JsonValidationError, JsonSchema

import IDRessourceNonTrouve
from token_manager import TokenManager
from app import app
from authorization_decorator import login_required
from basic_auth_decorator import basic_auth_required
from database import Database
from demande_inspection import DemandeInspection
from notification import extract_and_update_data
from schema import inspection_insert_schema, valider_new_user_schema, \
    contrevenant_update_schema, contravention_update_schema
from user import User
from validations import validates_is_integer, is_incomplete, doesnt_exist, \
    validates_dates, is_empty

load_dotenv()
schema = JsonSchema(app)

if os.environ.get('WERKZEUG_RUN_MAIN') != 'true':
    update_thread = threading.Thread(target=extract_and_update_data)
    update_thread.start()

if __name__ == '__main__':
    app.secret_key = "AUTH_KWESI_SECRET"
    app.run()


@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.disconnect()
    # Enregistrez la fermeture du planificateur à la sortie
    # update_thread.join()


@app.errorhandler(JsonValidationError)
def validation_error(e):
    errors = [validation_error.message for validation_error in e.errors]
    return jsonify({'error': e.message, 'errors': errors}), 400


@app.route('/')
def index():
    titre = "Accueil"
    etablissements = Database.get_db().get_distinct_etablissements()
    script = "/js/script_accueil.js"
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
    if keywords is None or len(keywords) == 0:
        error = "Une erreur est survenue, veuillez réessayer plus tard."
        return render_template('results.html',
                               error=error)
    else:
        results = Database.get_db().search(keywords)
        return render_template('results.html', keywords=keywords,
                               results=results)


@app.route('/plainte')
def plainte():
    script = "/js/script_plainte.js"
    return render_template('plainte.html', script=script, titre="Plainte")


@app.route('/plainte-envoyee')
def plainte_envoyee():
    return render_template('confirmation_plainte.html', titre="Plainte")


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
            return is_incomplete()

        db = Database.get_db()
        user = db.get_user_login_infos(courriel)
        if user is None:
            return doesnt_exist()

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

        # Convertir les valeurs en entiers
        new_etablissements = [int(etablissement) for etablissement in
                              new_etablissements]

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
    db = Database()
    photo_data = db.get_photo(id_photo)
    if photo_data:
        return Response(photo_data, mimetype='application/octet-stream')


# E2
@app.route('/confirmation-modifs-user', methods=['GET'])
def confirmation_modifs_user():
    titre = 'Modifications enregistrées'
    return render_template('confirmation_modifs_user.html', titre=titre)


@app.route('/unsubscribe-page/<token>', methods=['GET'])
def unsubscribe(token):
    titre = 'Désabonnement'
    script = "/js/script_unsubscribeUser.js"
    message = None  # Variable pour stocker le message à afficher sur la page

    # Récupérez les informations de l'utilisateur à partir du token
    token_manager = TokenManager()
    if token_manager.is_token_expired(token):
        message = "Ce lien de désabonnement a expiré."
        return render_template('unsubscribe.html', titre=titre, script=script,
                               message=message)
    else:
        # Vérifier si le token est valide et récupérer les données associées
        token_data = token_manager.get_token_data(token)
        if token_data:
            # Mettre à jour l'expiration du token ici, si nécessaire
            token_manager.update_token_expiration(token)

            email = token_data[0]
            id_business = token_data[1]
            etablissement = token_data[2]
            adresse = token_data[3]

            return render_template('unsubscribe.html', titre=titre,
                                   script=script, id_business=id_business,
                                   email=email, token=token,
                                   message=message,
                                   etablissement=etablissement,
                                   adresse=adresse)
        else:
            message = "Vous êtes déjà désabonné de cet établissement."
            return render_template('unsubscribe.html', titre=titre,
                                   script=script, message=message)


# E4
@app.route('/api/unsubscribe', methods=['POST'])
def unsubscribe_user():
    # Obtenir le token, l'id de l'établissement et l'email de l'utilisateur à partir du corps de la requête POST
    token = request.json.get('token')
    id_business = request.json.get('id_business')
    email = request.json.get('email')

    # Instance de TokenManager pour gérer les opérations liées aux tokens
    token_manager = TokenManager()

    # Supprimer l'établissement surveillé par l'utilisateur de la base de données
    db = Database.get_db()
    user = db.get_user_by_email(email)
    if user:
        success = db.delete_user_choix_etablissements(email, id_business)
        if success:
            token_manager.delete_token(token)
            # Retourner une réponse JSON indiquant le succès
            return jsonify(
                {"success": True, "message": "Désabonnement réussi."}), 200
        else:
            return jsonify({"success": False,
                            "message": "L'établissement n'est pas surveillé par cet utilisateur."}), 400
    else:
        return jsonify(
            {"success": False, "message": "Utilisateur non trouvé."}), 404


# E4
@app.route('/confirmation-unsubscribed-user', methods=['GET'])
def confirmation_unsubscribed_user():
    titre = 'Désabonnement confirmé'
    return render_template('confirmation_unsubscribe_user.html',
                           titre=titre)


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


@app.route('/modal', methods=['POST'])
def modal_etablissements():
    """ NOTE pour documentation : Recoit JSON de l'etablissement'"""
    infos_obtenues = request.get_json()
    return render_template('modal_etablissement.html',
                           results=infos_obtenues)


def count_contraventions(contraventions):
    occurrences = {item['id_business']: {'count': sum(
        1 for c in contraventions if c['id_business'] == item['id_business']),
        'etablissement': item[
            'etablissement']} for item in
        contraventions}
    return occurrences


# A4
@app.route('/api/contrevenants', methods=['GET'])
def contrevenants():
    date1 = request.args.get('start-date')
    date2 = request.args.get('end-date')
    db = Database.get_db()
    try:
        validates_dates(date1, date2)
        results = db.get_contraventions_between(date1, date2)
        if is_empty(results):
            return jsonify(results), 404
        return jsonify(results), 200
    except ValueError as e:
        error_msg = {"error": str(e)}
        return json.dumps(error_msg), 400
    except Exception as e:
        return jsonify(
            "Une erreur est survenue sur le serveur. "
            "Veuillez réessayer plus tard.")


# A6
@app.route('/api/contrevenant/<id_business>', methods=['GET'])
def info_etablissements(id_business):
    try:
        validates_is_integer(id_business, "Le id_business")
        etablissement = Database.get_db().get_info_contrevenant(id_business)
        return jsonify(etablissement)
    except ValueError as e:
        error_msg = {"error": str(e)}
        return json.dumps(error_msg), 400
    except IDRessourceNonTrouve as e:
        return jsonify(e.message), 404
    except Exception as e:
        return jsonify("Une erreur est survenue sur le serveur. "
                       "Veuillez réessayer plus tard.")


@app.route('/api/contrevenant/<id_business>', methods=['PATCH'])
@basic_auth_required
@schema.validate(contrevenant_update_schema)
def modify_contrevenant(id_business):
    modifs_request = request.get_json()
    try:
        return update_contrevenant(id_business, modifs_request)
    except ValueError as e:
        error_msg = {"error": str(e)}
        return json.dumps(error_msg), 400
    except IDRessourceNonTrouve as e:
        return jsonify("La ressource n'a pu être modifiée.", e.message), 404
    except Exception as e:
        return jsonify(
            "Une erreur est survenue sur le serveur. "
            "Veuillez réessayer plus tard.")


# TODO deplacer?
def update_contrevenant(id_business, modifs_request):
    validates_is_integer(id_business, "Le id_business")
    Database.get_db().update_contrevenant(id_business, modifs_request)
    modified = Database.get_db().get_info_contrevenant(id_business)
    return jsonify(modified), 200


@app.route('/api/contrevenant/<id_business>',
           methods=['DELETE'])
@basic_auth_required
def delete_contrevenant(id_business):
    try:
        validates_is_integer(id_business, "Le id_business")
        Database.get_db().delete_contrevenant(id_business)
        return jsonify("Le contrevenant bien été supprimé"), 200
    except ValueError as e:
        error_msg = {"error": str(e)}
        return json.dumps(error_msg), 400
    except IDRessourceNonTrouve as e:
        return jsonify(e.message), 404
    except sqlite3.Error as e:
        return jsonify("Une erreur est survenue", e), 500




@app.route('/dropdown_etablissement', methods=['GET'])
def update_dropdown_etablissement():
    try:
        etablissements = Database.get_db().get_distinct_etablissements()
        return jsonify(etablissements)
    except Exception as e:
        return jsonify({"error": "Une erreur est survenue, "
                                 "veuillez réessayer plus tard."}, 500)


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
        id_demande = Database.get_db().insert_demande_inspection(nouvelle_demande)
        demande_creee = Database.get_db().get_demande_inspection(id_demande)
        test = demande_creee.dictionnaire()
        response = {
            "message": "Utilisateur ajouté",
            "demande_creee": test
        }
        return jsonify(response), 201
    except Exception as e:
        print(e)
        return jsonify(
            error="Une erreur est survenue sur le serveur. Veuillez "
                  "réessayer plus tard"), 500


@app.route('/api/demande-inspection/<id_demande>', methods=['DELETE'])
@schema.validate(inspection_insert_schema)
def supprimer_inspection(id_demande):
    try:
        return delete_demande_inspection(id_demande)
    except ValueError as e:
        error_msg = {"error": str(e)}
        return json.dumps(error_msg), 400
    except Exception as e:
        return jsonify(
            error="Une erreur est survenue sur le serveur. Veuillez "
                  "réessayer plus tard"), 500


# TODO deplacer
def delete_demande_inspection(id_demande):
    validates_is_integer(id_demande, "Le id_demande")
    demande = Database.get_db().get_demande_inspection(id_demande)
    if demande is None:
        return jsonify(
            "Le ID " + id_demande + " ne correspond à aucune demande "
                                    "d\'inspection."), 404
    Database.get_db().delete_demande_inspection(id_demande)
    return jsonify("La demande a bien été supprimée."), 200


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
