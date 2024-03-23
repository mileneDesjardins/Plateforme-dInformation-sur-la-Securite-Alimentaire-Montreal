
CREATE TABLE User(
    id_user INTEGER NOT NULL PRIMARY KEY,
    nom_complet varchar(50) NOT NULL,
    courriel varchar(100) NOT NULL,
    choix_etablissements INTEGER[] NOT NULL,
    mdp_hash varchar(128) NOT NULL,
    mdp_salt varchar(32) NOT NULL,
    id_photo VARCHAR(255),
    CONSTRAINT fk_photo
        FOREIGN KEY (id_photo)
        REFERENCES photo(id_photo)
)