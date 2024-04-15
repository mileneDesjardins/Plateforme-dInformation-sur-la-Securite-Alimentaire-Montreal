CREATE TABLE DemandesInspection
(
    id                 INTEGER NOT NULL PRIMARY KEY,
    etablissement      TEXT    NOT NULL,
    adresse            TEXT    NOT NULL,
    ville              TEXT    NOT NULL,
    date_visite        TEXT    NOT NULL,
    nom_complet_client TEXT    NOT NULL,
    description        TEXT    NOT NULL
)