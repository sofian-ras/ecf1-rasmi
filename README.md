#  Pipeline ETL : Scraping, Enrichissement et Stockage Cloud

##  Présentation du Projet
Ce projet est un pipeline de données complet (ETL) réalisé dans le cadre de l'examen ECF. Il automatise la collecte de données web, leur nettoyage, leur enrichissement via API, et leur stockage dans une architecture hybride (SQL et Stockage Objet).

## Architecture Technique
Le projet repose sur une infrastructure conteneurisée via **Docker** :
- **PostgreSQL** : Stockage des données structurées (Livres, Citations, Librairies).
- **MinIO** : Stockage objet (S3) pour les fichiers JSON bruts et les images.
- **pgAdmin** : Interface d'administration pour la base de données.

## Flux de données (Data Pipeline)
1. **Extraction (Scrapy)** : 
   - Scraping de `books.toscrape.com` (images incluses).
   - Scraping de `quotes.toscrape.com`.
   - Pipeline de sauvegarde immédiate en JSON (format brut).
2. **Transformation & Enrichissement (Pandas & API)** :
   - Nettoyage des prix et des types de données.
   - Appel à l'**API Adresse (Gouv.fr)** pour géolocaliser les librairies partenaires (ajout de Latitude/Longitude).
3. **Chargement (PostgreSQL & Boto3)** :
   - Insertion sécurisée dans Postgres (gestion des transactions et rollbacks).
   - Synchronisation finale de tout le répertoire `data/` vers le bucket MinIO.


### Comment lancer le projet ?
1. **Lancer les services** (Base de données et Cloud) :
   `docker-compose up -d`
2. **Installer les outils** :
   `pip install -r requirements.txt`
3. **Démarrer le pipeline** :
   `python main.py`

### 🛠️ Ce que fait le projet :
1. **Récolte** : Des robots (Scrapy) vont chercher des livres et des citations sur le web.
2. **Enrichit** : On ajoute les coordonnées GPS des librairies via une API météo/adresse.
3. **Nettoie** : On transforme les prix et les notes en vrais chiffres avec Pandas.
4. **Stocke** : Tout est rangé dans une base SQL (Postgres) et les images vont dans le Cloud (MinIO).