class User:
    """
    Représente un user.
    """
    def __init__(self, nom_complet, courriel, choix_etablissements,
                 mdp_hash, mdp_salt, id_photo=None):
        self.nom_complet = nom_complet
        self.courriel = courriel
        self.choix_etablissements = choix_etablissements
        self.mdp_hash = mdp_hash
        self.mdp_salt = mdp_salt
        self.id_photo = id_photo

    def set_id(self, id_user):
        self.id_user = id_user

    def all_infos(self):
        return {
            'id_user': self.id_user,
            'nom_complet': self.nom_complet,
            'courriel': self.courriel,
            'choix_etablissements': self.choix_etablissements,
            'mdp_hash': self.mdp_hash,
            'mdp_salt': self.mdp_salt,
            'id_photo': self.id_photo
        }
