import datetime
import sqlite3
import csv
from flask import g
from datetime import datetime

import contravention
from contravention import Contravention


class Database:
    def __init__(self):
        self.connection = None

    def get_connection(self):
        if self.connection is None:
            self.connection = sqlite3.connect('db/contravention.db')
        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.close()

    @staticmethod
    def get_db():
        if not hasattr(g, '_database'):
            g._database = Database()
        return g._database

    def insert_contraventions_from_csv(self, csv_file):
        with open(csv_file, 'r', encoding='utf-8') as file:
            contenu = csv.reader(file)
            cursor = self.get_connection().cursor()
            insertion = (
                "INSERT INTO Contravention(id_poursuite, id_business, date, "
                "description, adresse, date_jugement, etablissement, montant, "
                "proprietaire, ville, statut, date_statut, categorie) "
                "VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)")

            # Ignorer la première ligne (en-tête)
            next(contenu)

            for row in contenu:
                try:
                    # Convertir la date du format YYYYMMDD en un objet datetime
                    date = datetime.strptime(row[2], '%Y%m%d').date()
                except ValueError:
                    # Gérer les erreurs de format de date
                    print(f"Erreur de format de date pour la ligne: {row}")
                    continue

                try:
                    # Insérer les données dans la base de données
                    cursor.execute(insertion, (
                        row[0], row[1], date, row[3], row[4], row[5], row[6],
                        row[7],
                        row[8], row[9], row[10], row[11], row[12]))
                except sqlite3.IntegrityError:
                    # Gérer les erreurs d'unicité en les ignorant
                    print(
                        f"Ignorer l'insertion pour id_poursuite existant: {row[0]}")
                    continue
                except Exception as e:
                    # Gérer les autres erreurs
                    print(f"Erreur lors de l'insertion pour la ligne: {row}")
                    print(f"Erreur détaillée: {e}")
                    continue
                else:
                    print(f"Données insérées avec succès pour la ligne: {row}")

            self.connection.commit()
