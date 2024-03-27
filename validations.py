import re
from datetime import datetime

from flask import render_template


def validates_format_iso(date):
    iso8601_pattern = r'^\d{4}-\d{2}-\d{2}$'
    if re.match(iso8601_pattern, date):
        return True
    else:
        return False


def validates_dates_order(start_date, end_date):
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end = datetime.strptime(end_date, '%Y-%m-%d').date()
    print(start <= end)
    return start <= end


def validates_dates(start_date, end_date):
    if (not validates_format_iso(start_date) or
            not validates_format_iso(end_date)):
        raise ValueError("Mauvais format de date. "
                         "Vérifier que date1 et date2 respectent le "
                         "format ISO 8601 (AAAA-MM-JJ)")
    elif not validates_dates_order(start_date, end_date):
        raise ValueError("La date de fin est inférieure"
                         " à la date de début. ")


def is_empty(array):
    return len(array) == 0


def doesnt_exist():
    return render_template('connection.html',
                           erreur="Utilisateur inexistant, veuillez "
                                  "vérifier vos informations")


def is_incomplete():
    return render_template('connection.html',
                           erreur="Veuillez remplir tous les champs")


def validates_is_integer(value, name_value):
    try:
        int_value = int(value)
    except ValueError:
        raise ValueError(
            name_value + " doit être un nombre entier valide.")

    if int_value <= 0:
        raise ValueError(
            name_value + " doit être un nombre entier positif.")
