# INF5190-Projet

## Auteures

ABEA05619105 - Anne-Sophie Abel-Levesque

DESM31559704 - Milene Desjardins

Le projet consiste à récupérer un ensemble de données provenant de la ville de Montréal et d'offrir des 
services à partir de ces données. Il s'agit de données ouvertes à propos d'établissements ayant reçu des 
constats d'infraction lors d'inspections alimentaires.


## EXÉCUTIONS DU PROGRAMME

Si vous n'êtes pas sur un environnement UNIX ou si vous n'avez pas Make d'installé, utilisez l'une des deux commandes
suivantes :

Option 1 :

```sh
flask run --app=index:run
```

Option 2 :

``` sh
export FLASK_APP=index.py
flask run
```

Si vous avez Make, vous pouvez exécuter le programme avec la commande :

``` sh
make
```


## PRÉREQUIS

1. Assurez-vous d'avoir installer Python sur votre système: https://www.python.org/downloads/

2. Installer Flask et pycodestyle à l'aide de pip, le gestionnaire de paquets de Python:

```bash

pip install Flask pycodestyle

```

- Python 3.12
- Flask 2
- SQLite3
- Make (optionnel)

## DÉPENDANCES

Installer toutes les librairies incluses dans le fichier requirements.txt:
   
```bash

pip install -r requirements.txt

```

## TECHNOLOGIES UTILISÉES

### Front-end

  - HTML 5
  - CSS 3
  - JavaScript
  - Bootstrap

### Back-end

  - Python
  - Flask
  - Jinja
  - SQLite3

## COMPATIBILITÉ DES FURETEURS

- Chrome
- Firefox
- Opera
- Edge
