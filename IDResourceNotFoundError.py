class IDResourceNotFoundError(Exception):
    def __init__(self,
                 message="Le ID ne correspond à aucune ressource "
                         "dans la base de données."):
        self.message = message
        super().__init__(self.message)
