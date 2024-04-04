CREATE TABLE Token (
    id_token INTEGER PRIMARY KEY,
    token_value VARCHAR(255) NOT NULL,
    expiration_date TIMESTAMP NOT NULL,
    courriel VARCHAR(100) NOT NULL,
    FOREIGN KEY (courriel) REFERENCES User(courriel)
);

-- Créez un trigger pour supprimer automatiquement les tokens expirés après 30 minutes
CREATE TRIGGER DeleteExpiredTokens AFTER INSERT ON Token
BEGIN
    DELETE FROM Token WHERE expiration_date <= strftime('%s', 'now', '-30 minutes');
END;
