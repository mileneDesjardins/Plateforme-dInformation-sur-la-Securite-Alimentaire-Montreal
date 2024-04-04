import sqlite3
import uuid
from datetime import datetime, timedelta

class TokenManager:
    def __init__(self):
        self.token_connection = None

    def get_token_connection(self):
        if self.token_connection is None:
            self.token_connection = sqlite3.connect('db/token.db')
        return self.token_connection

    def generate_token(self, id_business, courriel):
        # Générer un token unique
        token_value = str(uuid.uuid4())

        # Insérer le token dans la base de données avec une expiration initialisée à NULL
        try:
            connection = self.get_token_connection().cursor()

            # Insérer le token dans la table Token
            connection.execute(
                "INSERT INTO Token (token_value, courriel, id_business, expiration_timestamp) VALUES (?, ?, ?, NULL)",
                (token_value, courriel, id_business))

            connection.connection.commit()
            connection.close()

            return token_value
        except sqlite3.Error as e:
            print("Erreur lors de l'insertion du token :", e)
            return None

    def update_token_expiration(self, token):
        # Mettre à jour le timestamp d'expiration du token pour démarrer le décompte
        try:
            connection = self.get_token_connection().cursor()

            # Mettre à jour l'expiration_timestamp avec le timestamp actuel
            connection.execute(
                "UPDATE Token SET expiration_timestamp = ? WHERE token_value = ?",
                (datetime.now() + timedelta(minutes=30), token))

            connection.connection.commit()
            connection.close()

            return True
        except sqlite3.Error as e:
            print("Erreur lors de la mise à jour du token :", e)
            return False

    def verify_token(self, token):
        try:
            connection = self.get_token_connection().cursor()

            connection.execute(
                "SELECT expiration_timestamp FROM Token WHERE token_value = ?",
                (token,))
            result = connection.fetchone()
            if result:
                expiration_timestamp = result[0]
                if expiration_timestamp > datetime.now():
                    return True
            return False
        except sqlite3.Error as e:
            print("Erreur lors de la vérification du token :", e)
            return False

    def get_token_data(self, token):
        try:
            conn = self.get_token_connection().cursor()

            # Récupérer les informations associées au token
            conn.execute(
                "SELECT courriel, id_business FROM Token WHERE token_value = ?",
                (token,))
            result = conn.fetchone()
            if result:
                return result
            return None
        except sqlite3.Error as e:
            print("Erreur lors de la récupération des données du token :", e)
            return None

    def delete_token(self, token):
        try:
            connection = self.get_token_connection().cursor()

            # Supprimer le token de la base de données
            connection.execute(
                "DELETE FROM Token WHERE token_value = ?",
                (token,)
            )

            connection.connection.commit()
            connection.close()

            return True
        except sqlite3.Error as e:
            print("Erreur lors de la suppression du token :", e)
            return False