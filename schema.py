inspection_insert_schema = {
    'type': 'object',
    'required': ['etablissement', 'adresse', 'ville', 'date_visite',
                 'nom_complet_client', 'description'],
    'properties': {
        'etablissement': {
            'type': 'string'
        },
        'adresse': {
            'type': 'string'
        },
        'ville': {
            'type': 'string'
        },
        'date_visite': {
            'type': 'string',
            'format': 'date-time'
        },
        'nom_complet_client': {
            'type': 'string'
        },
        'description': {
            'type': 'string'
        },
    },
    'additionalProperties': False
}

valider_new_user_schema = {
    "type": "object",
    "properties": {
        "nom_complet": {"type": "string"},
        "courriel": {"type": "string"},
        "choix_etablissements": {
            "type": "array",
            "items": {"type": "integer"}
        },
        "mdp": {"type": "string"},
    },
    "required": ["nom_complet", "courriel", "choix_etablissements", "mdp"],
    "additionalProperties": False
}

