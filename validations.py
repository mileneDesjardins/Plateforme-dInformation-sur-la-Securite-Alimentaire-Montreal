"""
Module servant à la validation de données
"""

import re
from datetime import datetime

from flask import render_template


def validates_format_iso(date):
    """
    Valide le format de date ISO 8601 (AAAA-MM-JJ).
    """
    iso8601_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if not re.match(iso8601_pattern, date):
        raise ValueError("Mauvais format de date. "
                         "Vérifier que la date respecte le format "
                         "ISO 8601 (AAAA-MM-JJ)")


def validates_dates_order(start_date, end_date):
    """
    Valide l'ordre des dates.
    """
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()
    if start > end:
        raise ValueError("La date de fin est inférieure"
                         " à la date de début. ")


def validates_dates(start_date, end_date):
    """
    Valide les dates en vérifiant le format et l'ordre.
    """
    validates_format_iso(start_date)
    validates_format_iso(end_date)
    validates_dates_order(start_date, end_date)


def is_empty(array):
    """
    Vérifie si un tableau est vide.
    """
    return len(array) == 0


def doesnt_exist():
    """
    Renvoie un message d'erreur si l'utilisateur n'existe pas.
    """
    return render_template('connection.html',
                           erreur="Utilisateur inexistant, veuillez "
                                  "vérifier vos informations")


def is_incomplete():
    """
    Renvoie un message d'erreur si des champs sont manquants.
    """
    return render_template('connection.html',
                           erreur="Veuillez remplir tous les champs")


def validates_is_integer(value, name_value):
    """
    Valide si une valeur est un entier positif.
    """
    try:
        int_value = int(value)
    except ValueError:
        raise ValueError(
            name_value + " doit être un nombre entier valide.")

    if int_value <= 0:
        raise ValueError(
            name_value + " doit être un nombre entier positif.")
