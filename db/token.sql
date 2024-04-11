CREATE TABLE Token
(
    id_token             INTEGER PRIMARY KEY,
    token_value          VARCHAR(255) NOT NULL,
    expiration_timestamp TIMESTAMP,
    courriel             VARCHAR(100) NOT NULL,
    id_business          INTEGER      NOT NULL,
    etablissement        TEXT         NOT NULL,
    FOREIGN KEY (courriel) REFERENCES User (courriel)
);

