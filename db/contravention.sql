CREATE TABLE Contravention
(
    id_poursuite    INTEGER  NOT NULL PRIMARY KEY,
    id_business     INTEGER  NOT NULL,
    date            DATE,
    description     TEXT,
    adresse         TEXT,
    date_jugement   DATE,
    etablissement   TEXT,
    montant         INTEGER,
    proprietaire    TEXT,
    ville           TEXT,
    statut          TEXT,
    date_statut     DATE,
    categorie       TEXT,
    timestamp_csv   DATETIME NOT NULL,
    timestamp_modif DATETIME,
    deleted         INTEGER  NOT NULL
);
