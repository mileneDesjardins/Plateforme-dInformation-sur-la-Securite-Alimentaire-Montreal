class IDRessourceNonTrouve(Exception):
    def __init__(self,
                 message="Le ou les ID ne correspondent à aucune ressource "
                         "dans la base de données."):
        self.message = message
        super().__init__(self.message)
