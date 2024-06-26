"""
Module database : Fournit des fonctions pour valider, ajouter, et mettre
a jour les donnes d'une base de donnees.
"""

import csv
import datetime
import sqlite3
import uuid
from datetime import datetime
from enum import Enum

from flask import g, json

from IDResourceNotFoundError import IDResourceNotFoundError
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
    """
      Construit un dictionnaire représentant une contravention à
      partir du résultat d'une requête SQL.
      """
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
    """NOTE : permet de retourner NONE si l'element nest pas
    dans la requete """
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
    """
    Vérifie si une entrée de la base de données peut être mise à jour
    en fonction des horodatages.
    """
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
    """
    Met à jour un enregistrement dans la table Contravention si
     cela est possible.
    """
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
    """
    Insère un nouvel enregistrement dans la table Contravention.
    """
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
        self.demande_inspection_connection = None
        self.last_import_time = None
        self.photo_connection = None
        self.token_connection = None
        self.date_importation_connection = None

    @staticmethod
    def get_db():
        """
        Récupère ou crée une connexion à la base de données.
        """
        if not hasattr(g, '_database'):
            g._database = Database()
        return g._database

    def disconnect(self):
        """
        Ferme toutes les connexions aux différentes tables de la
        base de données.
        """
        if self.contravention_connection is not None:
            self.contravention_connection.close()
        if self.user_connection is not None:
            self.user_connection.close()
        if self.demande_inspection_connection is not None:
            self.demande_inspection_connection.close()
        if self.photo_connection is not None:
            self.photo_connection.close()
        if self.token_connection is not None:
            self.token_connection.close()
        if self.date_importation_connection is not None:
            self.date_importation_connection.close()

    # CONTRAVENTION
    def get_contravention_connection(self):
        """
        Récupère la connexion à la table Contravention dans la base de
        données. Si la connexion n'existe pas, elle est créée.
        """
        if self.contravention_connection is None:
            self.contravention_connection = sqlite3.connect(
                'db/contravention.db')
        return self.contravention_connection

    def get_contraventions(self):
        """
        Récupère toutes les contraventions à partir de la base de données.
        """
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
        """
        Insère des contraventions à partir d'un fichier
        CSV dans la base de données.
        """
        new_data_inserted = False  # Variable pour suivre si de nouvelles
        # données ont été insérées
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
                    # Insérer les données dans la base de données
                    cursor.execute(insertion, (
                        row[0], row[1], date, row[3], row[4],
                        date_jugement,
                        row[6],
                        row[7],
                        row[8], row[9], row[10], date_statut, row[12],
                        date_importation, timestamp_csv, deleted))
                    new_data_inserted = True  # Marquer qu'une nouvelle
                    # donnée a été insérée
                except sqlite3.IntegrityError:
                    # Essaie de mettre a jour la base de donnees
                    if (self.can_be_updated(row[Cols.ID_POURSUITE.value],
                                            row[Cols.ID_BUSINESS.value],
                                            cursor)):
                        self.sync_row(cursor, date, date_jugement, date_statut,
                                      row, timestamp_csv)

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

    def sync_row(self, cursor, date, date_jugement, date_statut,
                 row, timestamp_csv):
        """
        Met à jour une ligne existante dans la table Contravention avec
        les données fournies.
        """

        # Mettre à jour les données existantes dans la base de données
        cursor.execute(
            "UPDATE Contravention SET date=?, description=?, adresse=?, "
            "date_jugement=?, etablissement=?, montant=?, proprietaire=?, "
            "ville=?, statut=?, date_statut=?, categorie=?, timestamp_csv=?, "
            "deleted=0 "
            "WHERE id_poursuite=? AND id_business=?",
            (date, row[3], row[4], date_jugement, row[6],
             row[7], row[8], row[9],
             row[10], date_statut, row[12], timestamp_csv,
             row[0], row[1])
        )

    def can_be_updated(self, id_poursuite, id_business, cursor):
        """
        Vérifie si une contravention peut être mise à jour dans la
        base de données.
        """
        params = (id_poursuite, id_business)
        cursor.execute(
            "SELECT * FROM Contravention WHERE id_poursuite=? "
            "AND id_business=?", params)
        contravention = cursor.fetchone()
        if contravention is not None:
            return (contravention[Cols.TSP_MOD.value] is None and
                    contravention[Cols.DELETED.value] == 0)
        return False

    def get_new_contraventions(self, last_import_time):
        """
        Récupère les nouvelles contraventions importées depuis le dernier
        import.
        """
        connection = self.get_contravention_connection()
        cursor = connection.cursor()
        new_import_time = datetime.now()

        print("Last import time for query:", last_import_time)
        print("New import time for query:", new_import_time)

        last_import_time_str = last_import_time.strftime(
            '%Y-%m-%d %H:%M:%S.%f')
        new_import_time_str = new_import_time.strftime('%Y-%m-%d %H:%M:%S.%f')

        query = ("SELECT * FROM Contravention WHERE date_importation > ? AND "
                 "date_importation <= ?")
        cursor.execute(query, (last_import_time_str, new_import_time_str))
        rows = cursor.fetchall()

        print(f"Number of new contraventions fetched: {len(rows)}")

        return rows

    def get_date_importation_connection(self):
        """
        Récupère la connexion à la table date_importation dans la base
        de données. Si la connexion n'existe pas, elle est créée.
        """
        if self.date_importation_connection is None:
            self.date_importation_connection = sqlite3.connect(
                'db/date_importation.db')
        return self.date_importation_connection

    def get_last_import_time(self):
        """
         Récupère la date et l'heure du dernier import depuis la
         table DATE_IMPORTATION dans la base de données.
         """
        conn = self.get_date_importation_connection()
        cur = conn.cursor()
        cur.execute("SELECT date FROM DATE_IMPORTATION")
        result = cur.fetchone()
        if result is not None:
            # Extraire la date du tuple et la convertir en objet datetime
            last_import_date = datetime.strptime(result[0],
                                                 '%Y-%m-%d %H:%M:%S.%f')
            return last_import_date

    def is_first_import(self):
        """
        Vérifie si c'est le premier import en vérifiant s'il y a des
        données dans la table DATE_IMPORTATION.
        """
        conn = self.get_date_importation_connection()
        cur = conn.cursor()
        cur.execute("SELECT COUNT(*) FROM DATE_IMPORTATION")
        count = cur.fetchone()[0]
        return count == 0

    def create_first_importation_date(self):
        """
        Crée une date d'importation initiale dans la table
        DATE_IMPORTATION si c'est le premier import.
        """
        conn = self.get_date_importation_connection()
        cur = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        cur.execute("INSERT INTO DATE_IMPORTATION (date) VALUES (?)", (now,))
        conn.commit()
        print("First importation date created:", now)

    def update_importation_date(self):
        """
        Met à jour la date d'importation dans la table DATE_IMPORTATION
        avec la date actuelle.
        """
        conn = self.get_date_importation_connection()
        cur = conn.cursor()
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
        cur.execute(
            "UPDATE DATE_IMPORTATION SET date = ?",
            (now,))
        conn.commit()
        print("Importation date updated:", now)

    def search(self, keywords):
        """
        Recherche des contraventions correspondant aux mots-clés fournis
        dans le nom de l'établissement, l'adresse ou le propriétaire.
        """
        cursor = self.get_contravention_connection().cursor()
        query = ("SELECT * FROM Contravention WHERE deleted=0 AND "
                 "etablissement LIKE ? OR "
                 "adresse LIKE ? OR proprietaire LIKE ? ")
        param = ('%' + keywords + '%')
        cursor.execute(query, (param, param, param))
        all_data = cursor.fetchall()
        return [_build_contravention_dict(item) for item in all_data]

    def get_contraventions_between(self, date1, date2):
        """
        Récupère les contraventions dont la date est comprise
        entre deux dates spécifiées.
        """
        cursor = self.get_contravention_connection().cursor()
        query = ("SELECT * FROM Contravention WHERE date >= ? AND date <= ? "
                 "AND deleted=0")
        param = (date1, date2)
        cursor.execute(query, param)
        all_data = cursor.fetchall()
        return [_build_contravention_dict(item) for item in all_data]

    def get_contraventions_business_between(self, date1, date2, id_business):
        """
        Récupère les contraventions dont la date est comprise entre deux
        dates spécifiées et associées à un identifiant d'entreprise donné.
        """
        cursor = self.get_contravention_connection().cursor()
        query = ("SELECT * FROM Contravention WHERE date >= ? AND date <= ? "
                 "AND id_business=? AND deleted=0")
        param = (date1, date2, id_business)
        cursor.execute(query, param)
        all_data = cursor.fetchall()
        return [_build_contravention_dict(item) for item in all_data]

    def get_etablissements_et_nbr_infractions(self):
        """
        Récupère le nombre d'infractions par établissement.
        """
        connection = self.get_contravention_connection()
        cursor = connection.cursor()

        query = """
        SELECT etablissement, COUNT(*) as nbr_infractions
        FROM Contravention
        WHERE deleted=0
        GROUP BY etablissement
        ORDER BY nbr_infractions DESC
        """

        cursor.execute(query)
        results = cursor.fetchall()

        return results

    def get_distinct_etablissements(self):
        """
        Récupère les établissements distincts avec leurs identifiants
        d'entreprise et adresses associées.
        """
        connection = self.get_contravention_connection()
        cursor = connection.cursor()
        query = (
            "SELECT DISTINCT id_business, etablissement, adresse FROM "
            "Contravention WHERE deleted=0 "
            "ORDER BY etablissement ")
        cursor.execute(query)
        results = cursor.fetchall()
        return results

    def get_info_contrevenant_by_name(self, etablissement):
        """
         Récupère les informations sur les contrevenants associés à
         un établissement donné.
         """
        connection = self.get_contravention_connection()
        cursor = connection.cursor()
        query = ("SELECT * FROM Contravention WHERE etablissement = ?"
                 " AND deleted=0")
        cursor.execute(query, (etablissement,))
        contraventions = cursor.fetchall()
        return [_build_contravention_dict(item) for item in contraventions]

    def get_info_poursuite(self, id_poursuite):
        """
        Récupère les informations sur une poursuite donnée à partir
        de son identifiant.
        """
        cursor = self.get_contravention_connection().cursor()
        query = "SELECT * FROM Contravention WHERE id_poursuite=?"
        cursor.execute(query, (id_poursuite,))
        info_poursuite = cursor.fetchone()
        if len(info_poursuite) == 0:
            return None
        return _build_contravention_dict(info_poursuite)

    def get_info_contrevenant(self, id_business):
        """
        Récupère les informations sur un contrevenant donné à partir
        de son identifiant d'entreprise.
        """
        self.validates_business_exists(id_business)
        connection = self.get_contravention_connection()
        cursor = connection.cursor()
        query = "SELECT * FROM Contravention WHERE id_business = ?"
        cursor.execute(query, (id_business,))
        info_etablissement = cursor.fetchall()
        return [_build_contravention_dict(item) for item in info_etablissement]

    def validates_poursuite_exists(self, id_poursuite):
        """
        Valide l'existence d'une poursuite dans la base de données.
        """
        cursor = self.get_contravention_connection().cursor()
        query = ("SELECT COUNT(*)  FROM Contravention WHERE id_poursuite=? "
                 "AND deleted=0")
        cursor.execute(query, (id_poursuite,))
        count = cursor.fetchone()

        if count[0] == 0:
            raise IDResourceNotFoundError(
                "Le id_poursuite `" + str(id_poursuite) +
                "` ne correspond à aucune ressource dans la base de données.")

    def validates_business_exists(self, id_business):
        """
        Valide l'existence d'une entreprise dans la base de données.
        """
        cursor = self.get_contravention_connection().cursor()
        query = ("SELECT COUNT(*)  FROM Contravention WHERE id_business=? "
                 "AND deleted=0")
        cursor.execute(query, (id_business,))
        count = cursor.fetchone()

        if count[0] == 0:
            raise IDResourceNotFoundError(
                "Le id_business `" + id_business +
                "` ne correspond à aucune ressource dans la base de données.")

    def update_date(self, id_poursuite, contrevenant):
        """
        Met à jour la date d'une poursuite dans la base de données.
        """
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
        """
        Met à jour la description d'une poursuite dans la base de données.
        """
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
        """
        Met à jour l'adresse d'une entreprise dans la base de données.
        """
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
        """
        Met à jour la date de jugement d'une poursuite dans la base de données.
        """
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
        """
        Met à jour le nom de l'établissement d'une entreprise dans la
        base de données.
        """
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
        """
        Met à jour le montant d'une contravention dans la base de données.
        """
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
        """
        Met à jour le propriétaire d'une contravention dans la base de données.
        """
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
        """
        Met à jour la ville associée à une contravention dans la base
        de données.
        """
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
        """
         Met à jour le statut d'une contravention dans la base de données.
         """
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
        """
        Met à jour la date de statut d'une contravention dans la base
        de données.

        """
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
        """
        Met à jour la catégorie d'une contravention dans la base de données.
        """
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
        """
        Met à jour les informations d'un contrevenant dans la base de données.
        """
        contrevenant = _build_contravention(modif_request)
        self.update_adresse(id_business, contrevenant)
        self.update_nom_etablissement(id_business, contrevenant)
        self.update_proprietaire(id_business, contrevenant)
        self.update_statut(id_business, contrevenant)
        self.update_date_statut(id_business, contrevenant)

    def update_contravention(self, id_poursuite,
                             modif_request):
        """
        Met à jour les informations d'une contravention dans la
        base de données.
        """
        contravention = _build_contravention(modif_request)
        self.update_date(id_poursuite, contravention)
        self.update_description(id_poursuite, contravention)
        self.update_date_jugement(id_poursuite, contravention)
        self.update_montant(id_poursuite, contravention)
        self.update_categorie(id_poursuite, contravention)

    def delete_contrevenant(self, id_business):
        """
        Supprime un contrevenant de la base de données.
        """
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

    # USER
    def get_user_connection(self):
        """
        Obtient la connexion à la base de données des utilisateurs.
        """
        if self.user_connection is None:
            self.user_connection = sqlite3.connect('db/user.db')
        return self.user_connection

    def create_user(self, user):
        """
        Crée un nouvel utilisateur dans la base de données.
        """
        connection = self.get_user_connection()
        cursor = connection.cursor()
        try:
            choix_etablissements_json = json.dumps(user.choix_etablissements)
            cursor.execute(
                "INSERT INTO User (nom_complet, courriel, "
                "choix_etablissements, mdp_hash, mdp_salt)"
                "VALUES (?, ?, ?, ?, ?)",
                (user.nom_complet, user.courriel, choix_etablissements_json,
                 user.mdp_hash, user.mdp_salt)
            )
            connection.commit()
        except Exception as e:
            print(f"Failed to create user {user.courriel}: {e}")
            connection.rollback()
        finally:
            cursor.close()
            connection.close()

    def get_user_login_infos(self, courriel):
        """
        Récupère les informations de connexion de l'utilisateur à partir
        de son adresse e-mail.
        """
        cursor = self.get_user_connection().cursor()
        cursor.execute((
            "SELECT * FROM user "
            "WHERE courriel=?"),
            (courriel,))
        return cursor.fetchone()

    def get_user_by_email(self, email):
        """
        Récupère les informations de l'utilisateur à partir de
        son adresse e-mail.
        """
        cursor = self.get_user_connection().cursor()
        cursor.execute(
            "SELECT * FROM User WHERE courriel = ?",
            (email,)
        )
        return cursor.fetchone()

    def get_user_by_id(self, id_user):
        """
        Récupère les informations de l'utilisateur à partir de son identifiant.
        """
        connection = self.get_user_connection()
        cursor = connection.cursor()
        cursor.execute(
            "SELECT * FROM User WHERE id_user = ?",
            (id_user,)
        )
        return cursor.fetchone()

    def get_all_users(self):
        """
        Récupère toutes les informations sur les utilisateurs enregistrés
        dans la base de données.
        """
        connection = self.get_user_connection()
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM User")
        return cursor.fetchall()

    def update_user_etablissements(self, id_user, new_etablissements):
        """
        Met à jour la liste des établissements choisis par un utilisateur.
        """
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
                "Liste des établissements mise à jour avec succès pour "
                "l'utilisateur",
                id_user)
        except Exception as e:
            print(
                "Erreur lors de la mise à jour des établissements pour "
                "l'utilisateur",
                id_user)
            print("Erreur détaillée:", e)

    def delete_user_choix_etablissements(self, email, id_business):
        """
        Supprime un établissement de la liste des choix d'établissements
        d'un utilisateur.
        """
        id_business = int(
            id_business)
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

                # Vérifier si l'établissement est dans la liste de
                # l'utilisateur et le supprimer
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
                f"Erreur lors de la suppression de l'établissement "
                f"{id_business} pour l'utilisateur {email}: {e}")
            return False
        finally:
            cursor.close()
            connection.close()

    def get_demandes_inspection_connection(self):
        """
        Récupère la connexion à la base de données des demandes d'inspection.
        """
        if self.demande_inspection_connection is None:
            self.demande_inspection_connection = sqlite3.connect(
                'db/demande_inspection.db')
        return self.demande_inspection_connection

    def disconnect_demandes_inspection(self):
        """
        Déconnecte de la base de données des demandes d'inspection.
        """
        if self.demande_inspection_connection is not None:
            self.demande_inspection_connection.close()

    def insert_demande_inspection(self, demande_inspection):
        """
        Insère une demande d'inspection dans la base de données.
        """
        cursor = self.get_demandes_inspection_connection().cursor()
        query = (
            "INSERT INTO DemandesInspection (etablissement, adresse, ville, "
            "date_visite, nom_complet_client, description ) "
            "VALUES (?,?,?,?,?,?)")
        params = (
            demande_inspection.etablissement, demande_inspection.adresse,
            demande_inspection.ville,
            demande_inspection.date_visite,
            demande_inspection.nom_complet_client,
            demande_inspection.description)
        cursor.execute(query, params)
        self.demande_inspection_connection.commit()
        return cursor.lastrowid

    def get_demande_inspection(self, id_demande):
        """
        Récupère une demande d'inspection à partir de son identifiant.
        """
        cursor = self.get_demandes_inspection_connection().cursor()
        query = "SELECT * FROM DemandesInspection WHERE id = ?"
        cursor.execute(query, (id_demande,))
        demande = cursor.fetchone()

        if demande is None:
            return None
        else:
            return DemandeInspection(demande[0], demande[1], demande[2],
                                     demande[3], demande[4], demande[5],
                                     demande[6])

    def delete_demande_inspection(self, id_demande):
        """
        Supprime une demande d'inspection de la base de données.
        """
        connection = self.get_demandes_inspection_connection()
        query = "DELETE FROM DemandesInspection WHERE id = ?"
        connection.execute(query, (id_demande,))
        connection.commit()

    # PHOTO
    def get_photo_connection(self):
        """
        Récupère ou établit une connexion à la base de données des photos.
        """
        if self.photo_connection is None:
            self.photo_connection = sqlite3.connect('db/photo.db')
        return self.photo_connection

    def get_photo(self, id_photo):
        """
        Récupère les données d'une photo à partir de son identifiant.
        """
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
        """
        Ajoute une nouvelle photo à la base de données.
        """
        id_photo = str(uuid.uuid4())
        connection = self.get_photo_connection()
        connection.execute("insert into Photo(id_photo, data) values(?, ?)",
                           [id_photo, sqlite3.Binary(photo_data)])
        connection.commit()
        return id_photo

    def update_user_photo(self, id_user, nouveau_id_photo):
        """
        Met à jour l'identifiant de la photo associée à un utilisateur
        dans la base de données.
        """
        connection = self.get_user_connection()
        connection.execute(
            "UPDATE User SET id_photo=? WHERE id_user=?",
            (nouveau_id_photo, id_user)
        )
        connection.commit()

    def delete_photo(self, id_photo):
        """
        Supprime une photo de la base de données en fonction de
        son identifiant.
        """
        connection = self.get_photo_connection()
        connection.execute("DELETE FROM Photo WHERE id_photo = ?",
                           (id_photo,))
        connection.commit()
