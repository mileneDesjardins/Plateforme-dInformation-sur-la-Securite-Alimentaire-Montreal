class Contravention:
    """
    Représente une contravention.
    """

    def __init__(self, id_poursuite, id_business, date, description,
                 adresse, date_jugement, etablissement, montant,
                 proprietaire, ville, statut, date_statut, categorie,
                 date_importation):
        self.id_poursuite = id_poursuite
        self.id_business = id_business
        self.date = date
        self.description = description
        self.adresse = adresse
        self.date_jugement = date_jugement
        self.etablissement = etablissement
        self.montant = montant
        self.proprietaire = proprietaire
        self.ville = ville
        self.statut = statut
        self.date_statut = date_statut
        self.categorie = categorie
        self.date_importation = date_importation

    def set_id(self, id):
        self.id = id

    def etablissement(self):
        return {
            'etablissement': self.etablissement,
        }
