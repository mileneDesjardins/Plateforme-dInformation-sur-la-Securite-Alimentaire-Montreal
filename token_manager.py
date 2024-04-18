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

    def generate_token(self, id_business, courriel, etablissement, adresse):
        # Générer un token unique
        token_value = str(uuid.uuid4())

        # Insérer le token dans la base de données avec une expiration
        # initialisée à NULL
        try:
            connection = self.get_token_connection().cursor()

            # Insérer le token dans la table Token
            connection.execute(
                "INSERT INTO Token (token_value, courriel, id_business, "
                "etablissement, adresse, expiration_timestamp) VALUES "
                "(?, ?, ?, ?, ?, NULL)",
                (token_value, courriel, id_business, etablissement,
                 adresse))

            connection.connection.commit()
            connection.close()

            return token_value
        except sqlite3.Error as e:
            print("Erreur lors de l'insertion du token :", e)
            return None

    def get_token_data(self, token):
        try:
            conn = self.get_token_connection().cursor()

            conn.execute(
                "SELECT courriel, id_business, etablissement, adresse FROM "
                "Token WHERE "
                "token_value = ?",
                (token,))
            result = conn.fetchone()
            if result:
                return result
            return None
        except sqlite3.Error as e:
            print("Erreur lors de la récupération des données du token :", e)
            return None

    def update_token_expiration(self, token):
        try:
            connection = self.get_token_connection().cursor()

            # Vérifier d'abord si l'expiration_timestamp est déjà défini
            connection.execute(
                "SELECT expiration_timestamp FROM Token WHERE token_value = ?",
                (token,)
            )
            result = connection.fetchone()

            # Si expiration_timestamp est None, mettre à jour le timestamp
            if result and result[0] is None:
                connection.execute(
                    "UPDATE Token SET expiration_timestamp = ? WHERE "
                    "token_value = ?",
                    (datetime.now() + timedelta(minutes=30), token)
                )

                connection.connection.commit()
                print("Expiration du token mise à jour avec succès.")
            else:
                print(
                    "Le token a déjà un timestamp d'expiration, mise à jour "
                    "non nécessaire.")

            connection.close()
            return True
        except sqlite3.Error as e:
            print("Erreur lors de la mise à jour de l'expiration du token :",
                  e)
            return False

    def is_token_expired(self, token):
        try:
            connection = self.get_token_connection().cursor()

            # Récupérer le expiration_timestamp du token
            connection.execute(
                "SELECT expiration_timestamp FROM Token WHERE token_value = ?",
                (token,)
            )
            result = connection.fetchone()
            connection.close()

            if result:
                expiration_timestamp = result[0]
                if expiration_timestamp:
                    # Convertir le expiration_timestamp en objet datetime
                    expiration_datetime = datetime.strptime(
                        expiration_timestamp, "%Y-%m-%d %H:%M:%S.%f")
                    if datetime.now() > expiration_datetime:
                        # Le token est expiré
                        print("Token expiré.")
                        return True
                    else:
                        # Le token n'est pas expiré
                        print("Le token n'est pas encore expiré.")
                        return False
                else:
                    # expiration_timestamp est None, le token n'est pas
                    # considéré comme expiré
                    print(
                        "Le timestamp d'expiration n'est pas défini, le token "
                        "n'est pas considéré comme expiré.")
                    return False
            else:
                # Aucun token correspondant trouvé dans la base de données.
                print(
                    "Aucun token correspondant trouvé dans la base de "
                    "données.")
                return False
        except sqlite3.Error as e:
            print(
                "Erreur lors de la tentative de vérification de l'expiration "
                "du token :",
                e)
            return False

    def delete_token(self, token):
        try:
            connection = self.get_token_connection().cursor()

            # Exécuter la requête de suppression
            connection.execute(
                "DELETE FROM Token WHERE token_value = ?",
                (token,)
            )

            # Valider les changements dans la base de données
            connection.connection.commit()
            print("Token supprimé avec succès.")

            connection.close()
            return True
        except sqlite3.Error as e:
            print("Erreur lors de la suppression du token :", e)
            return False
