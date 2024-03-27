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

contrevenants_update_schema = {
    'type': 'object',
    'required': ['id_business'],
    'properties': {
        'id_poursuite': {
            'type': 'number'
        },
        'id_business': {
            'type': 'number'
        },
        'date': {
            'type': 'string',
            'format': 'date-time'
        },
        'adresse': {
            'type': 'string'
        },
        'date_jugement': {
            'type': 'string',
            'format': 'date-time'
        },
        'etablissement': {
            'type': 'string'
        },
        'montant': {
            'type': 'number'
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
        },
        'categorie': {
            'type': 'string'
        }
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
    'type': 'array',
    'required': ['id_poursuite'],
    'properties': {
        'id_poursuite': {
            'type': 'number'
        },
        'date': {
            'type': 'string',
            'format': 'date-time'
        },
        'date_jugement': {
            'type': 'string',
            'format': 'date-time'
        },
        'montant': {
            'type': 'number'
        },
        'categorie': {
            'type': 'string'
        }
    },
    'additionalProperties': False
}
