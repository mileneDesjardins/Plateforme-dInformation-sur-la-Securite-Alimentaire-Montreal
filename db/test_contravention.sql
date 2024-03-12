CREATE TABLE Contravention
(
    id_poursuite  INTEGER NOT NULL PRIMARY KEY,
    id_business   INTEGER NOT NULL,
    date          DATE    NOT NULL,
    description   TEXT    NOT NULL,
    adresse       TEXT    NOT NULL,
    date_jugement DATE    NOT NULL,
    etablissement TEXT    NOT NULL,
    montant       INTEGER NOT NULL,
    proprietaire  TEXT    NOT NULL,
    ville         TEXT    NOT NULL,
    statut        TEXT    NOT NULL CHECK (statut IN
                                          ('Fermé changement d''exploitant',
                                           'Ouvert', 'Fermé')),
    date_statut   DATE    NOT NULL,
    categorie     TEXT    NOT NULL
);
