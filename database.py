import datetime
import sqlite3
import csv
from flask import g, json
from datetime import datetime

from IDRessourceNonTrouve import IDRessourceNonTrouve
import user
from contravention import Contravention
from demande_inspection import DemandeInspection


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
        "categorie": query_result[12]
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
        categorie=modifs_request.get('categorie')
    )
    return contrevenant


class Database:
    def __init__(self):
        self.contravention_connection = None
        self.user_connection = None
        self.demandes_inspection_connection = None

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
             statut, date_statut, categorie) = row
            contravention = Contravention(id_poursuite, id_business, date,
                                          description, adresse,
                                          date_jugement, etablissement,
                                          montant, proprietaire, ville,
                                          statut, date_statut, categorie)
            contraventions.append(contravention)
        return contraventions

    def insert_contraventions_from_csv(self, csv_file):
        with open(csv_file, 'r', encoding='utf-8') as file:
            contenu = csv.reader(file)
            cursor = self.get_contravention_connection().cursor()
            insertion = (
                "INSERT INTO Contravention(id_poursuite, id_business, date, "
                "description, adresse, date_jugement, etablissement, montant, "
                "proprietaire, ville, statut, date_statut, categorie, timestamp_csv) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

            # Ignorer la première ligne (en-tête)
            next(contenu)

            for row in contenu:
                try:
                    # Convertir la date du format YYYYMMDD en un objet datetime
                    date = datetime.strptime(row[2], '%Y%m%d').date()
                    date_jugement = datetime.strptime(row[5], '%Y%m%d').date()
                    date_statut = datetime.strptime(row[11], '%Y%m%d').date()
                except ValueError:
                    # Gérer les erreurs de format de date
                    print(f"Erreur de format de date pour la ligne: {row}")
                    continue

                try:
                    current_time = datetime.now()
                    # Insérer les données dans la base de données
                    cursor.execute(insertion, (
                        row[0], row[1], date, row[3], row[4], date_jugement,
                        row[6],
                        row[7],
                        row[8], row[9], row[10], date_statut, row[12],
                        current_time), )
                except sqlite3.IntegrityError:
                    # Gérer les erreurs d'unicité en les ignorant
                    print(
                        f"Ignorer l'insertion pour id_poursuite existant: "
                        f"{row[0]}")
                    continue
                except Exception as e:
                    # Gérer les autres erreurs
                    print(f"Erreur lors de l'insertion pour la ligne: {row}")
                    print(f"Erreur détaillée: {e}")
                    continue

            self.contravention_connection.commit()

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

    def get_info_contrevenant_by_id(self, id_business):
        connection = self.get_contravention_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM Contravention WHERE id_business = ?"
        cursor.execute(query, (id_business,))
        info_etablissement = cursor.fetchall()
        return [_build_contravention_dict(item) for item in info_etablissement]

    def validates_poursuite_exists(self, id_poursuite):
        cursor = self.get_contravention_connection().cursor()
        query = ("SELECT COUNT(*)  FROM Contravention WHERE id_poursuite=?")
        cursor.execute(query, (id_poursuite,))
        count = cursor.fetchone()

        if count[0] == 0:
            raise IDRessourceNonTrouve()

    def validates_business_exists(self, id_business):
        cursor = self.get_contravention_connection().cursor()
        query = ("SELECT COUNT(*)  FROM Contravention WHERE id_business=?")
        cursor.execute(query, (id_business,))
        count = cursor.fetchone()

        if count[0] == 0:
            raise IDRessourceNonTrouve()

    def update_date(self, id_poursuite, contrevenant):
        if contrevenant.date is not None:
            self.validates_poursuite_exists(id_poursuite)
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

    def update_contrevenant(self, id_business, modif_request):
        contrevenant = _build_contravention(modif_request)
        self.update_adresse(id_business, contrevenant)
        self.update_nom_etablissement(id_business, contrevenant)
        self.update_proprietaire(id_business, contrevenant)
        self.update_ville(id_business, contrevenant)
        self.update_statut(id_business, contrevenant)
        self.update_date_statut(id_business, contrevenant)

    def update_info_contravention(self, id_poursuite,
                                  modif_request):
        contravention = _build_contravention(modif_request)
        self.update_date(id_poursuite, contravention)
        self.update_description(id_poursuite, contravention)
        self.update_date_jugement(id_poursuite, contravention)
        self.update_montant(id_poursuite, contravention)
        self.update_categorie(id_poursuite, contravention)

    def delete_contrevenant(self, id_business):
        # TODO verifier si deja delete, si oui renvoyer false ?
        connection = self.get_contravention_connection()
        cursor = connection.cursor()
        query = ("UPDATE Contravention SET adresse = NULL,"
                 "date=NULL, description=NULL, date_jugement=NULL, "
                 "etablissement=NULL, montant=NULL, proprietaire=NULL, "
                 "ville=NULL, statut=NULL, date_statut=NULL, categorie=NULL,"
                 "deleted=1, timestamp_modif=? WHERE id_business =?")
        try:
            cursor.execute(query, (datetime.now(), id_business))
            connection.commit()
            return True
        except sqlite3.Error as e:
            connection.rollback()
            return False

    def delete_contravention(self, id_poursuite):
        connection = self.get_contravention_connection()
        cursor = connection.cursor()
        query = ("UPDATE Contravention SET adresse = NULL,"
                 "date=NULL, description=NULL, date_jugement=NULL, "
                 "etablissement=NULL, montant=NULL, proprietaire=NULL, "
                 "ville=NULL, statut=NULL, date_statut=NULL, categorie=NULL, "
                 "timestamp_modif=?, deleted=1 WHERE id_poursuite=?")
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

    # DEMANDE D'INSPECTION

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
        demande = cursor.fetchall()

        if len(demande) == 0:
            return None
        else:
            return DemandeInspection(demande[0], demande[1], demande[2],
                                     demande[3], demande[4], demande[5],
                                     demande[6], demande[7])

    def delete_demande_inspection(self, demande_inspection):
        connection = self.get_demandes_inspection_connection()
        query = "DELETE FROM Demandes_Inspection WHERE id = ?"
        connection.execute(query, (demande_inspection.id,))
        connection.commit()