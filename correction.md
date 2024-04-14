# Correction projet INF5190-H24

## Milene Desjarins - DESM31559704

### A1 10xp

#### Comment tester :
Importation des données avec la base de données "Contravention" déjà 
configurée.
1. Ouvrez le terminal dans le répertoire du projet.
2. Exécutez la commande suivante : `$ python3 download.py`

Création de la base de données "Contravention"
1. Lancez la création de la table en exécutant : `$ python3 
   create_table_contravention.py`

### A2 5xp

#### Comment tester reblabla

### C1 10xp

#### Comment tester reblabla

### C2 5xp

#### Comment tester reblabla

### C3 5xp

#### Comment tester reblabla

### E1 15xp

#### Comment tester reblabla

### E2 15xp

#### Comment tester reblabla

### E3 5xp

#### Comment tester reblabla

### E4 10xp

#### Comment tester reblabla

UPDATE Contravention SET date_importation = '2024-04-01 12:08:00:000' WHERE
id_poursuite = 10002;

UPDATE Contravention SET date_importation = '2024-04-01 12:08:00:000' WHERE
id_poursuite = 4455;

### E4 10xp

#### Comment tester reblabla

### F1 15xp

#### Comment tester reblabla

## Anne-Sophie Abel-Levesque ABEA05619105

### A2 10xp

#### Étapes pour tester
- Aller sur la page d'accueil (la barre de recherche est également accessible partout sur le site) 
- Cliquer sur la barre de recherche en haut à droite de la page
- Effectuer une recherche
    - Par nom et/ou établissement et/ou rue
    - vide (envoyer une requête vide)

### A4 10xp

#### Étapes pour tester
Effectuez une requête `GET` à la route `api/contrevenants?start-date<date1>&end-date=<date2>` via l'extension YARC (ou tout autre REST client), en remplaçant `date1` et `date2` par les dates que vous souhaitez testés.  

Un exemple de requête valide : 

```text
api/contrevenants?start-date=2022-12-12&end-date=2024-12-12
```


### A5 10xp

#### Comment tester reblabla

### A6 10xp

#### Comment tester reblabla

### D1 15xp

#### Comment tester reblabla

### D2 5xp

#### Comment tester reblabla

### D3 15xp

#### Comment tester reblabla

### D4 15xp

#### Comment tester reblabla

Mettre user et mdp dans fichier .quelquechose 

