class User:
    def __init__(self, id_user, prenom, nom, courriel, choix_etablissements,
                 mdp_hash, mdp_salt, id_photo=None):
        self.id_user = id_user
        self.prenom = prenom
        self.nom = nom
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
            'prenom': self.prenom,
            'nom': self.nom,
            'courriel': self.courriel,
            'choix_etablissements': self.choix_etablissements,
            'mdp_hash': self.mdp_hash,
            'mdp_salt': self.mdp_salt,
            'id_photo': self.id_photo
        }


insert_schema = {
    'type': 'object',
    'required': ['prenom', 'nom', 'courriel', 'choix_etablissements',
                 'mdp_hash', 'mdp_salt'],
    'properties': {
        'prenom': {'type': 'string'},
        'nom': {'type': 'string'},
        'courriel': {'type': 'string'},
        'choix_etablissements': {
            'type': 'array',
            'items': {'type': 'string'}
        },
        'mdp_hash': {'type': 'string'},
        'mdp_salt': {'type': 'string'},
        'id_photo': {'type': ['string', 'null']}
        # Permet une chaîne ou une valeur null
    },
    'additionalProperties': False
}
