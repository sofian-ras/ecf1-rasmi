DROP TABLE IF EXISTS books CASCADE;
DROP TABLE IF EXISTS quotes CASCADE;
DROP TABLE IF EXISTS librairies CASCADE;

-- table pour les livres scrapes
CREATE TABLE books (
    id SERIAL PRIMARY KEY,
    titre VARCHAR(500),
    prix VARCHAR(50),     
    note VARCHAR(50),
    disponibilite VARCHAR(100),
    categorie VARCHAR(100),
    date_collecte TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- table pour les citations
CREATE TABLE quotes (
    id SERIAL PRIMARY KEY,
    texte TEXT,
    auteur VARCHAR(200),
    tags TEXT,
    date_collecte TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE librairies (
    id SERIAL PRIMARY KEY,
    nom_librairie VARCHAR(200),
    adresse VARCHAR(300),
    code_postal VARCHAR(10),
    ville VARCHAR(100),
    specialite VARCHAR(100),
    date_partenariat DATE,
    longitude DECIMAL(10,6),
    latitude DECIMAL(10,6),
    geocodage_score DECIMAL(5,2),
    date_import TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_books_categorie ON books(categorie);
CREATE INDEX idx_quotes_auteur ON quotes(auteur);
CREATE INDEX idx_librairies_ville ON librairies(ville);