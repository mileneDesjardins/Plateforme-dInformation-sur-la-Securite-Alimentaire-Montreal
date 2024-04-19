class DemandeInspection:
    """
    Représente une Demande d'inspection.
    """
    def __init__(self, id, etablissement, adresse, ville, date_visite,
                 nom_complet_client, description):
        self.id = id
        self.etablissement = etablissement
        self.adresse = adresse
        self.ville = ville
        self.date_visite = date_visite
        self.nom_complet_client = nom_complet_client
        self.description = description

    def get_demande_info(self):
        return {
            'id': self.id,
            'etablissement': self.etablissement,
            'adresse': self.adresse,
            'ville': self.ville,
            'date_visite': self.date_visite,
            'nom_complet_client': self.nom_complet_client,
            'description': self.description
        }

    def set_id(self, id):
        self.id = id

    def dictionnaire(self):
        return {
            'id': self.id,
            'etablissement': self.etablissement,
            'adresse': self.adresse,
            'ville': self.ville,
            'date_visite': self.date_visite,
            'nom_complet_client': self.nom_complet_client,
            'description': self.description
        }
