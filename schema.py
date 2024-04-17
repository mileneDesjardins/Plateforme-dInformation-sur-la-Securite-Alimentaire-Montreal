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
            'format': 'date-time',
            "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
        }
    },
    'additionalProperties': False
}

valider_new_user_schema = {
    "type": "object",
    "properties": {
        "nom_complet": {
            "type": "string",
            "minLength": 3,
            "maxLength": 50},
        "courriel": {
            "type": "string",
            "pattern": "^[\\w\\.+-]+@([\\w-]+\\.)+[\\w-]{2,4}$"
        },
        "choix_etablissements": {
            "type": "array",
            "minItems": 1,
            "items": {"type": "integer"}
        },
        "mdp": {
            "type": "string",
            "minLength": 5,
            "maxLength": 20}
    },
    "required": ["nom_complet", "courriel", "choix_etablissements",
                 "mdp"],
    "additionalProperties": False
}

valider_unsubscribe_user_schema = {
    "type": "object",
    "properties": {
        "token": {
            "type": "string",
            "minLength": 1
        },
        "id_business": {
            "type": "integer"
        },
        "email": {
            "type": "string",
            "format": "email"
        }
    },
    "required": ["token", "id_business", "email"],
    "additionalProperties": False
}
