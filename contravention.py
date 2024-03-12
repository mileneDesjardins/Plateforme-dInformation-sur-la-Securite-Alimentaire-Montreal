class Contravention:
    def __init__(self, id_poursuite, id_business, date, description,
                 adresse, date_jugement, etablissement, montant,
                 proprietaire, ville, statut, date_statut, categorie):
        self.id_poursuite = id_poursuite
        self.id_business = id_business #ANNE-SO pas le meme nom que dans CSV
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
