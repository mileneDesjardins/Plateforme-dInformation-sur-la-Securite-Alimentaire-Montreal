CREATE TABLE Demandes_Inspection
(
    id            INTEGER NOT NULL PRIMARY KEY,
    etablissement TEXT    NOT NULL,
    adresse       TEXT    NOT NULL,
    ville         TEXT    NOT NULL,
    date_visite   TEXT    NOT NULL,
    nom_client    TEXT    NOT NULL,
    prenom_client TEXT    NOT NULL,
    description   TEXT    NOT NULL
)