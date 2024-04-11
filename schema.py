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

contrevenant_update_schema = {
    'type': 'object',
    'properties': {
        'adresse': {
            'type': 'string'
        },
        'etablissement': {
            'type': 'string'
        },
        'proprietaire': {
            'type': 'string'
        },
        'ville': {
            'type': 'string'
        },
        'statut': {
            'type': 'string'
        },
        'date_statut': {
            'type': 'string',
            'format': 'date-time'
        }
    },
    'additionalProperties': False
}

contravention_update_schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "id_poursuite": {
                "type": "number",
            },
            "date": {
                "type": "string",
                "format": "date-time"
            },
            "date_jugement": {
                "type": "string",
                "format": "date-time"
            },
            "montant": {
                "type": "number"
            },
            "categorie": {
                "type": "string"
            }
        },
        "required": ["id_poursuite"],
        'additionalProperties': False
    }
}

valider_new_user_schema = {
    "type": "object",
    "properties": {
        "nom_complet": {"type": "string"},
        "courriel": {
            "type": "string",
            "format": "email"
        },
        "choix_etablissements": {
            "type": "array",
            "items": {"type": "integer"}
        },
        "mdp": {"type": "string"}
    },
    "required": ["nom_complet", "courriel", "choix_etablissements",
                 "mdp"],
    "additionalProperties": False
}
