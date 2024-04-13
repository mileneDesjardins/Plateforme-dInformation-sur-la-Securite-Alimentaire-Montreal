import csv
import datetime
import sqlite3
import uuid
from datetime import datetime
from enum import Enum

from flask import g, json

from IDRessourceNonTrouve import IDRessourceNonTrouve
from contravention import Contravention
from demande_inspection import DemandeInspection
from validations import validates_format_iso


class Cols(Enum):
    """
    Enumérations représentant les colonnes du schéma de la
    table SQL Contravention.
    """
    ID_POURSUITE = 0
    ID_BUSINESS = 1
    DATE = 2
    DESCRIP = 3
    ADRESSE = 4
    DATE_JUG = 5
    ETAB = 6
    MONTANT = 7
    PROPRIO = 8
    VILLE = 9
    STATUT = 10
    DATE_STA = 11
    CAT = 12
    DATE_IMPORTATION = 13
    TSP_CSV = 14
    TSP_MOD = 15
    DELETED = 16


def _build_contravention_dict(query_result):
    contravention = {
        "id_poursuite": query_result[0],
        "id_business": query_result[1],
        "date": query_result[2],
        "description": query_result[3],
        "adresse": query_result[4],
        "date_jugement": query_result[5],
        "etablissement": query_result[6],
        "montant": query_result[7],
        "proprietaire": query_result[8],
        "ville": query_result[9],
        "statut": query_result[10],
        "date_statut": query_result[11],
        "categorie": query_result[12],
        "date_importation": query_result[13]
    }
    return contravention


def _build_contravention(modifs_request):
    """NOTE : permet de retourner NONE si l'element nest pas dans la requete """
    contrevenant = Contravention(
        id_poursuite=modifs_request.get("id_poursuite"),
        id_business=modifs_request.get('id_business'),
        date=modifs_request.get('date'),
        description=modifs_request.get('description'),
        adresse=modifs_request.get('adresse'),
        date_jugement=modifs_request.get('date_jugement'),
        etablissement=modifs_request.get('etablissement'),
        montant=modifs_request.get('montant'),
        proprietaire=modifs_request.get('proprietaire'),
        ville=modifs_request.get('ville'),
        statut=modifs_request.get('statut'),
        date_statut=modifs_request.get('date_statut'),
        categorie=modifs_request.get('categorie'),
        date_importation=modifs_request.get('date_importation')
    )
    return contrevenant


def can_be_update(timestamp_modif, timestamp_csv):
    if timestamp_modif is None:
        return True
    if isinstance(timestamp_modif, str):
        timestamp_modif = datetime.strptime(timestamp_modif,
                                            '%Y-%m-%d %H:%M:%S.%f')
    if isinstance(timestamp_csv, str):
        timestamp_csv = datetime.strptime(timestamp_csv,
                                          '%Y-%m-%d %H:%M:%S.%f')
    return timestamp_csv > timestamp_modif


def update_record(cursor, date, date_jugement, date_statut,
                  existing_data, row):
    if can_be_update(existing_data[Cols.TSP_MOD.value],
                     existing_data[Cols.TSP_CSV.value]):
        current_time = datetime.now()
        query = (
            "UPDATE Contravention SET date=?, description=?, adresse=?, "
            "date_jugement=?, etablissement=?, montant=?, proprietaire=?, "
            "ville=?, statut=?, date_statut=?, categorie=?, "
            "date_importation=?, timestamp_csv=?, deleted=0 "
            "WHERE id_poursuite=? AND id_business=?")
        params = (date, row[Cols.DESCRIP.value], row[Cols.ADRESSE.value],
                  date_jugement, row[Cols.ETAB.value],
                  row[Cols.MONTANT.value], row[Cols.PROPRIO.value],
                  row[Cols.VILLE.value], row[Cols.STATUT.value],
                  date_statut, row[Cols.CAT.value], current_time,
                  row[Cols.ID_POURSUITE.value], row[Cols.ID_BUSINESS.value])
        cursor.execute(query, params)


def insert_new_record(cursor, date, date_jugement,
                      date_statut, row):
    current_time = datetime.now()
    query = ("INSERT INTO Contravention(id_poursuite, id_business, date, "
             "description, adresse, date_jugement, etablissement, montant, "
             "proprietaire, ville, statut, date_statut, categorie, "
             "date_importation, "
             "timestamp_csv, deleted) "
             "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 0)",)
    params = (
        row[Cols.ID_POURSUITE.value], row[Cols.ID_BUSINESS.value],
        date, row[Cols.DESCRIP.value], row[Cols.ADRESSE.value],
        date_jugement, row[Cols.ETAB.value], row[Cols.MONTANT.value],
        row[Cols.PROPRIO.value], row[Cols.VILLE.value],
        row[Cols.STATUT.value], date_statut, row[Cols.CAT.value],
        row[Cols.DATE_IMPORTATION.value],
        current_time.value)
    cursor.execute(query, params)


class Database:
    def __init__(self):
        self.contravention_connection = None
        self.user_connection = None
        self.demandes_inspection_connection = None
        self.last_import_time = None
        self.photo_connection = None
        self.token_connection = None

    @staticmethod
    def get_db():
        if not hasattr(g, '_database'):
            g._database = Database()
        return g._database

    def disconnect(self):  # TODO je pense quil manque des disconnect?
        if self.contravention_connection is not None:
            self.contravention_connection.close()
        if self.user_connection is not None:
            self.user_connection.close()
        if self.demandes_inspection_connection is not None:
            self.demandes_inspection_connection.close()
        if self.last_import_time is not None:
            self.last_import_time.close()
        if self.photo_connection is not None:
            self.photo_connection.close()
        if self.token_connection is not None:
            self.token_connection.close()

    # CONTRAVENTION
    def get_contravention_connection(self):
        if self.contravention_connection is None:
            self.contravention_connection = sqlite3.connect(
                'db/contravention.db')
        return self.contravention_connection

    def get_contraventions(self):
        connection = self.get_contravention_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Contravention")

        contraventions = []
        for row in cursor.fetchall():
            (id_poursuite, id_business, date, description, adresse,
             date_jugement, etablissement, montant, proprietaire, ville,
             statut, date_statut, categorie, date_importation) = row
            contravention = Contravention(id_poursuite, id_business, date,
                                          description, adresse,
                                          date_jugement, etablissement,
                                          montant, proprietaire, ville,
                                          statut, date_statut, categorie,
                                          date_importation)
            contraventions.append(contravention)
        return contraventions

    def insert_contraventions_from_csv(self, csv_file):
        new_data_inserted = False  # Variable pour suivre si de nouvelles données ont été insérées
        with open(csv_file, 'r', encoding='utf-8') as file:
            contenu = csv.reader(file)
            cursor = self.get_contravention_connection().cursor()
            insertion = (
                "INSERT INTO Contravention(id_poursuite, id_business, date, "
                "description, adresse, date_jugement, etablissement, montant, "
                "proprietaire, ville, statut, date_statut, categorie, "
                "date_importation, timestamp_csv, deleted) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

            # Ignorer la première ligne (en-tête)
            next(contenu)

            for row in contenu:
                try:
                    # Convertir la date du format YYYYMMDD en un objet datetime
                    date = datetime.strptime(row[2], '%Y%m%d').date()
                    date_jugement = datetime.strptime(row[5], '%Y%m%d').date()
                    date_statut = datetime.strptime(row[11], '%Y%m%d').date()
                    date_importation = datetime.now()
                    timestamp_csv = datetime.now()
                    deleted = 0
                except ValueError:
                    # Gérer les erreurs de format de date
                    print(f"Erreur de format de date pour la ligne: {row}")
                    continue

                try:
                    # verifier si deja dans base de donnnes  si oui, update
                    cursor.execute(
                        "SELECT * FROM Contravention WHERE id_poursuite=? AND id_business=?",
                        (row[0], row[1])
                    )
                    existing_data = cursor.fetchone()

                    if existing_data is not None:

                        if self.can_be_update(existing_data[14],
                                              existing_data[14]):
                            # Mettre à jour les données existantes dans la base de données
                            cursor.execute(
                                "UPDATE Contravention SET date=?, description=?, adresse=?, "
                                "date_jugement=?, etablissement=?, montant=?, proprietaire=?, "
                                "ville=?, statut=?, date_statut=?, categorie=?, timestamp_csv=?, deleted=0 "
                                "WHERE id_poursuite=? AND id_business=?",
                                (date, row[3], row[4], date_jugement, row[6],
                                 row[7], row[8], row[9],
                                 row[10], date_statut, row[12], timestamp_csv,
                                 row[0], row[1])
                            )
                    else:

                    #Insérer les données dans la base de données
                        cursor.execute(insertion, (
                            row[0], row[1], date, row[3], row[4], date_jugement,
                            row[6],
                            row[7],
                            row[8], row[9], row[10], date_statut, row[12],
                            date_importation, timestamp_csv, deleted))
                        new_data_inserted = True  # Marquer qu'une nouvelle donnée a été insérée
                except sqlite3.IntegrityError:
                    # Gérer les erreurs d'unicité en les ignorant
                    # print(
                    #     f"Ignorer l'insertion pour id_poursuite existant: "
                    #     f"{row[0]}")
                    continue
                except Exception as e:
                    # Gérer les autres erreurs
                    print(f"Erreur lors de l'insertion pour la ligne: {row}")
                    print(f"Erreur détaillée: {e}")
                    continue

            self.contravention_connection.commit()

        if new_data_inserted:
            print("Nouvelles données insérées avec succès.")
        else:
            print("Aucune nouvelle donnée insérée.")

    def can_be_update(self, timestamp_modif, timestamp_csv):
        if timestamp_modif is None:
            return True
        if isinstance(timestamp_modif, str):
            timestamp_modif = datetime.strptime(timestamp_modif,
                                                '%Y-%m-%d %H:%M:%S.%f')
        if isinstance(timestamp_csv, str):
            timestamp_csv = datetime.strptime(timestamp_csv,
                                              '%Y-%m-%d %H:%M:%S.%f')

        return timestamp_csv > timestamp_modif

    def get_new_contraventions(self, last_import_time):
        # Obtention de la connexion à la base de données des contraventions
        connection = self.get_contravention_connection()
        # connection.set_trace_callback(print)
        cursor = connection.cursor()

        # Utiliser l'heure actuelle comme new_import_time
        new_import_time = datetime.now()

        print("last", last_import_time)
        print("new", new_import_time)

        # Requête pour récupérer les contraventions entre la dernière importation et l'heure actuelle
        query = "SELECT * FROM Contravention WHERE date_importation > ? AND date_importation <= ?"

        # Exécution de la requête avec les paramètres
        cursor.execute(query, (last_import_time, new_import_time))

        # Récupération de toutes les lignes retournées par la requête
        rows = cursor.fetchall()

        return rows

    def update_last_import_time(self):
        self.last_import_time = datetime.now()

    def get_last_import_time(self):
        return self.last_import_time

    def search(self, keywords):
        cursor = self.get_contravention_connection().cursor()
        query = ("SELECT * FROM Contravention WHERE etablissement LIKE ? OR "
                 "adresse LIKE ? OR proprietaire LIKE ?")
        param = ('%' + keywords + '%')
        cursor.execute(query, (param, param, param))
        all_data = cursor.fetchall()
        return [_build_contravention_dict(item) for item in all_data]

    def get_contraventions_between(self, date1, date2):
        cursor = self.get_contravention_connection().cursor()
        query = "SELECT * FROM Contravention WHERE date >= ? AND date <= ?"
        param = (date1, date2)
        cursor.execute(query, param)
        all_data = cursor.fetchall()
        return [_build_contravention_dict(item) for item in all_data]

    def get_contraventions_business_between(self, date1, date2, id_business):
        cursor = self.get_contravention_connection().cursor()
        query = ("SELECT * FROM Contravention WHERE date >= ? AND date <= ? "
                 "AND id_business=?")
        param = (date1, date2, id_business)
        cursor.execute(query, param)
        all_data = cursor.fetchall()
        return [_build_contravention_dict(item) for item in all_data]

    def get_etablissements_et_nbr_infractions(self):
        connection = self.get_contravention_connection()
        cursor = connection.cursor()

        query = """
        SELECT etablissement, COUNT(*) as nbr_infractions
        FROM Contravention
        GROUP BY etablissement
        ORDER BY nbr_infractions DESC
        """

        cursor.execute(query)
        results = cursor.fetchall()

        return results

    def get_distinct_etablissements(self):
        connection = self.get_contravention_connection()
        cursor = connection.cursor()
        query = (
            "SELECT DISTINCT id_business, etablissement, adresse FROM "
            "Contravention "
            "ORDER BY etablissement")
        cursor.execute(query)
        results = cursor.fetchall()
        return results

    def get_info_contrevenant_by_name(self, etablissement):
        connection = self.get_contravention_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM Contravention WHERE etablissement = ?"
        cursor.execute(query, (etablissement,))
        contraventions = cursor.fetchall()
        return [_build_contravention_dict(item) for item in contraventions]

    def get_info_poursuite(self, id_poursuite):
        cursor = self.get_contravention_connection().cursor()
        query = "SELECT * FROM Contravention WHERE id_poursuite=?"
        cursor.execute(query, (id_poursuite,))
        info_poursuite = cursor.fetchone()
        if len(info_poursuite) == 0:
            return None
        return _build_contravention_dict(info_poursuite)

    def get_info_contrevenant(self, id_business):
        self.validates_business_exists(id_business)
        connection = self.get_contravention_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM Contravention WHERE id_business = ?"
        cursor.execute(query, (id_business,))
        info_etablissement = cursor.fetchall()
        return [_build_contravention_dict(item) for item in info_etablissement]

    def validates_poursuite_exists(self, id_poursuite):
        cursor = self.get_contravention_connection().cursor()
        query = ("SELECT COUNT(*)  FROM Contravention WHERE id_poursuite=? "
                 "AND deleted=0")
        cursor.execute(query, (id_poursuite,))
        count = cursor.fetchone()

        if count[0] == 0:
            raise IDRessourceNonTrouve(
                "Le id_poursuite `" + str(id_poursuite) +
                "` ne correspond à aucune ressource dans la base de données.")

    def validates_business_exists(self, id_business):
        cursor = self.get_contravention_connection().cursor()
        query = ("SELECT COUNT(*)  FROM Contravention WHERE id_business=? "
                 "AND deleted=0")
        cursor.execute(query, (id_business,))
        count = cursor.fetchone()

        if count[0] == 0:
            raise IDRessourceNonTrouve(
                "Le id_business `" + id_business +
                "` ne correspond à aucune ressource dans la base de données.")

    def update_date(self, id_poursuite, contrevenant):
        if contrevenant.date is not None:
            self.validates_poursuite_exists(id_poursuite)
            validates_format_iso(contrevenant.date)
            connection = self.get_contravention_connection()
            cursor = connection.cursor()
            query = ("UPDATE Contravention SET date = ?, "
                     "timestamp_modif=? WHERE id_poursuite=? ")
            cursor.execute(query, (
                contrevenant.date, datetime.now(),
                id_poursuite))
            connection.commit()

    def update_description(self, id_poursuite, contrevenant):
        if contrevenant.description is not None:
            self.validates_poursuite_exists(id_poursuite)
            connection = self.get_contravention_connection()
            cursor = connection.cursor()
            query = ("UPDATE Contravention SET description = ?, "
                     "timestamp_modif=? WHERE id_poursuite=? ")
            cursor.execute(query, (contrevenant.description, datetime.now(),
                                   id_poursuite))
            connection.commit()

    def update_adresse(self, id_business, contrevenant):
        if contrevenant.adresse is not None:
            self.validates_business_exists(id_business)
            connection = self.get_contravention_connection()
            cursor = connection.cursor()
            query = ("UPDATE Contravention SET adresse = ?, "
                     "timestamp_modif=? WHERE id_business = ? ")
            cursor.execute(query, (contrevenant.adresse, datetime.now(),
                                   id_business))
            connection.commit()

    def update_date_jugement(self, id_poursuite, contrevenant):
        if contrevenant.date_jugement is not None:
            self.validates_poursuite_exists(id_poursuite)
            connection = self.get_contravention_connection()
            cursor = connection.cursor()
            query = ("UPDATE Contravention SET date_jugement = ?, "
                     "timestamp_modif=? WHERE id_poursuite=? ")
            cursor.execute(query, (contrevenant.date_jugement, datetime.now(),
                                   id_poursuite))
            connection.commit()

    def update_nom_etablissement(self, id_business, contrevenant):
        if contrevenant.etablissement is not None:
            self.validates_business_exists(id_business)
            connection = self.get_contravention_connection()
            cursor = connection.cursor()
            query = ("UPDATE Contravention SET etablissement = ?, "
                     "timestamp_modif=? WHERE id_business = ? ")
            cursor.execute(query, (contrevenant.etablissement, datetime.now(),
                                   id_business))
            connection.commit()

    def update_montant(self, id_poursuite, contravention):
        if contravention.montant is not None:
            self.validates_poursuite_exists(id_poursuite)
            connection = self.get_contravention_connection()
            cursor = connection.cursor()
            query = ("UPDATE Contravention SET montant = ?, "
                     "timestamp_modif=? WHERE id_poursuite=? ")
            cursor.execute(query, (contravention.montant, datetime.now(),
                                   id_poursuite))
            connection.commit()

    def update_proprietaire(self, id_business, contravention):
        if contravention.proprietaire is not None:
            self.validates_business_exists(id_business)
            connection = self.get_contravention_connection()
            cursor = connection.cursor()
            query = ("UPDATE Contravention SET proprietaire = ?, "
                     "timestamp_modif=? WHERE id_business = ? ")
            cursor.execute(query, (contravention.proprietaire, datetime.now(),
                                   id_business))
            connection.commit()

    def update_ville(self, id_business, contravention):
        if contravention.ville is not None:
            self.validates_business_exists(id_business)
            connection = self.get_contravention_connection()
            cursor = connection.cursor()
            query = ("UPDATE Contravention SET ville = ?, "
                     "timestamp_modif=? WHERE id_business = ? ")
            cursor.execute(query, (contravention.ville, datetime.now(),
                                   id_business))
            connection.commit()

    def update_statut(self, id_business, contravention):
        if contravention.statut is not None:
            self.validates_business_exists(id_business)
            connection = self.get_contravention_connection()
            cursor = connection.cursor()
            query = ("UPDATE Contravention SET statut = ?, "
                     "timestamp_modif=? WHERE id_business = ? ")
            cursor.execute(query, (contravention.statut, datetime.now(),
                                   id_business))
            connection.commit()

    def update_date_statut(self, id_business, contravention):
        if contravention.date_statut is not None:
            self.validates_business_exists(id_business)
            connection = self.get_contravention_connection()
            cursor = connection.cursor()
            query = ("UPDATE Contravention SET date_statut = ?, "
                     "timestamp_modif=? WHERE id_business = ? ")
            cursor.execute(query, (contravention.date_statut, datetime.now(),
                                   id_business))
            connection.commit()

    def update_categorie(self, id_poursuite, contravention):
        if contravention.categorie is not None:
            self.validates_poursuite_exists(id_poursuite)
            connection = self.get_contravention_connection()
            cursor = connection.cursor()
            query = ("UPDATE Contravention SET categorie = ?, "
                     "timestamp_modif=? WHERE id_poursuite=? ")
            cursor.execute(query, (contravention.categorie, datetime.now(),
                                   id_poursuite))
            connection.commit()

    # TODO si delete, retourner true ?
    def update_contrevenant(self, id_business, modif_request):
        contrevenant = _build_contravention(modif_request)
        self.update_adresse(id_business, contrevenant)
        self.update_nom_etablissement(id_business, contrevenant)
        self.update_proprietaire(id_business, contrevenant)
        self.update_statut(id_business, contrevenant)
        self.update_date_statut(id_business, contrevenant)

    # TODO si delete, retourner true ?
    def update_contravention(self, id_poursuite,
                             modif_request):
        contravention = _build_contravention(modif_request)
        self.update_date(id_poursuite, contravention)
        self.update_description(id_poursuite, contravention)
        self.update_date_jugement(id_poursuite, contravention)
        self.update_montant(id_poursuite, contravention)
        self.update_categorie(id_poursuite, contravention)

    def delete_contrevenant(self, id_business):
        self.validates_business_exists(id_business)
        connection = self.get_contravention_connection()
        cursor = connection.cursor()
        query = ("UPDATE Contravention SET timestamp_modif=?, "
                 "deleted=1 WHERE id_business =?")
        try:
            cursor.execute(query, (datetime.now(), id_business))
            connection.commit()
            return True
        except sqlite3.Error as e:
            connection.rollback()
            return False

    def delete_contravention(self, id_poursuite):
        self.validates_poursuite_exists(id_poursuite)
        connection = self.get_contravention_connection()
        cursor = connection.cursor()
        query = ("UPDATE Contravention SET timestamp_modif=?, "
                 "deleted=1 WHERE id_poursuite=?")
        try:
            cursor.execute(query, (datetime.now(), id_poursuite))
            connection.commit()
            return True
        except sqlite3.Error as e:
            connection.rollback()
            return False

    # USER
    def get_user_connection(self):
        if self.user_connection is None:
            self.user_connection = sqlite3.connect('db/user.db')
        return self.user_connection

    def create_user(self, user):
        connection = self.get_user_connection()
        cursor = connection.cursor()
        choix_etablissements_json = json.dumps(user.choix_etablissements)
        cursor.execute(
            "INSERT INTO User (nom_complet, courriel, "
            "choix_etablissements, mdp_hash, mdp_salt)"
            "VALUES (?, ?, ?, ?, ?)",
            (user.nom_complet, user.courriel, choix_etablissements_json,
             user.mdp_hash,
             user.mdp_salt)
        )
        connection.commit()

    def get_user_login_infos(self, courriel):
        cursor = self.get_user_connection().cursor()
        cursor.execute((
            "SELECT * FROM user "
            "WHERE courriel=?"),
            (courriel,))
        return cursor.fetchone()

    def get_user_by_email(self, email):
        cursor = self.get_user_connection().cursor()
        cursor.execute(
            "SELECT * FROM User WHERE courriel = ?",
            (email,)
        )
        return cursor.fetchone()

    def get_user_by_id(self, id_user):
        connection = self.get_user_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM User WHERE id_user = ?",
            (id_user,)
        )
        return cursor.fetchone()

    def get_all_users(self):
        connection = self.get_user_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM User")
        return cursor.fetchall()

        # Méthode pour mettre à jour les établissements choisis pour un utilisateur

    # Méthode pour mettre à jour les établissements choisis pour un utilisateur
    def update_user_etablissements(self, id_user, new_etablissements):
        connection = self.get_user_connection()
        cursor = connection.cursor()

        # Convertir la nouvelle liste d'établissements en format JSON
        new_etablissements_json = json.dumps(new_etablissements)

        try:
            # Mettre à jour la ligne de l'utilisateur dans la base de données
            cursor.execute(
                "UPDATE User SET choix_etablissements = ? WHERE id_user = ?",
                (new_etablissements_json, id_user)
            )
            connection.commit()
            print(
                "Liste des établissements mise à jour avec succès pour l'utilisateur",
                id_user)
        except Exception as e:
            # Gérer les erreurs éventuelles
            print(
                "Erreur lors de la mise à jour des établissements pour l'utilisateur",
                id_user)
            print("Erreur détaillée:", e)

    def delete_user_choix_etablissements(self, email, id_business):
        # Convertir id_business en entier pour s'assurer de la compatibilité de type
        id_business = int(
            id_business)  # Assurez-vous que cette ligne est placée ici
        connection = self.get_user_connection()
        cursor = connection.cursor()
        try:
            # Sélectionner les choix d'établissements de l'utilisateur
            cursor.execute(
                "SELECT choix_etablissements FROM User WHERE courriel = ?",
                (email,)
            )
            user_data = cursor.fetchone()

            if user_data:
                choix_etablissements = json.loads(user_data[0])

                # Vérifier si l'établissement est dans la liste de l'utilisateur et le supprimer
                if id_business in choix_etablissements:
                    choix_etablissements.remove(id_business)
                    cursor.execute(
                        "UPDATE User SET choix_etablissements = ? WHERE "
                        "courriel = ?",
                        (json.dumps(choix_etablissements), email)
                    )
                    connection.commit()
                    return True
        except Exception as e:
            print(
                f"Erreur lors de la suppression de l'établissement {id_business} pour l'utilisateur {email}: {e}")
            return False
        finally:
            cursor.close()  # Assurez-vous de fermer le curseur
            connection.close()  # Et de fermer la connexion

    def get_demandes_inspection_connection(self):
        if self.demandes_inspection_connection is None:
            self.demandes_inspection_connection = sqlite3.connect(
                'db/demandes_inspection.db')
        return self.demandes_inspection_connection

    def disconnect_demandes_inspection(self):
        if self.demandes_inspection_connection is not None:
            self.demandes_inspection_connection.close()

    def insert_demande_inspection(self, demande_inspection):
        cursor = self.get_demandes_inspection_connection().cursor()
        query = (
            "INSERT INTO Demandes_Inspection (etablissement, adresse, ville, "
            "date_visite, nom_complet_client, description ) "
            "VALUES (?,?,?,?,?,?)")
        params = (
            demande_inspection.etablissement, demande_inspection.adresse,
            demande_inspection.ville,
            demande_inspection.date_visite,
            demande_inspection.nom_complet_client,
            demande_inspection.description)
        cursor.execute(query, params)
        self.demandes_inspection_connection.commit()

    def get_demande_inspection(self, id_demande):
        cursor = self.get_demandes_inspection_connection().cursor()
        query = "SELECT * FROM Demandes_Inspection WHERE id = ?"
        cursor.execute(query, (id_demande,))
        demande = cursor.fetchone()

        if demande is None:
            return None
        else:
            return DemandeInspection(demande[0], demande[1], demande[2],
                                     demande[3], demande[4], demande[5],
                                     demande[6])

    def delete_demande_inspection(self, id_demande):
        connection = self.get_demandes_inspection_connection()
        query = "DELETE FROM Demandes_Inspection WHERE id = ?"
        connection.execute(query, (id_demande,))
        connection.commit()

    # PHOTO
    def get_photo_connection(self):
        if self.photo_connection is None:
            self.photo_connection = sqlite3.connect('db/photo.db')
        return self.photo_connection

    def get_photo(self, id_photo):
        connection = self.get_photo_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT data FROM Photo WHERE id_photo=?",
                       (id_photo,))
        photo_data = cursor.fetchone()
        if photo_data:
            return photo_data[0]
        else:
            return None

    def create_photo(self, photo_data):
        id_photo = str(uuid.uuid4())
        connection = self.get_photo_connection()
        connection.execute("insert into Photo(id_photo, data) values(?, ?)",
                           [id_photo, sqlite3.Binary(photo_data)])
        connection.commit()
        return id_photo

    def update_user_photo(self, id_user, nouveau_id_photo):
        connection = self.get_user_connection()
        connection.execute(
            "UPDATE User SET id_photo=? WHERE id_user=?",
            (nouveau_id_photo, id_user)
        )
        connection.commit()

    def delete_photo(self, id_photo):
        connection = self.get_photo_connection()
        connection.execute("DELETE FROM Photo WHERE id_photo = ?",
                           (id_photo,))
        connection.commit()
