### 1ere methode: scraping simple avec requests et BeautifulSoup.

## QUESTION 1. choix d'architecture globale

### architecture choisie: scrapy

- Stockage Relationnel (PostgreSQL) : Pour les données structurées (prix, titres, adresses) afin de permettre des analyses SQL rapides.
- Stockage Objet (MinIO) : Pour l'archivage des fichiers JSON bruts et la centralisation des images récupérées sur le web.

### pourquoi ce choix?

pour un projet de cette taille avec 3 sources de donnees, une architecture lakehouse simplifiee est la plus adaptee parce que:
- on peut garder les donnees brutes en json (flexibilite)
- on peut faire du sql sur les donnees transformees (performance)
- c'est simple a mettre en place avec docker
- ca coute pas cher en infrastructure

### alternative consideree

**base nosql (mongodb)**
- avantages: flexible pour le schema
- inconvenients: pas de sql natif, moins bon pour les jointures
- pourquoi pas choisi: le besoin demande du sql

## QUESTION 2. choix des technologies

### stockage des donnees brutes: fichiers json

**justification:**
- format lisible par un humain
- facile a debugger
- compatible avec tous les langages
- pas besoin d'infrastructure complexe

### stockage des donnees transformees: postgresql

**justification:**
- base relationnelle solide et gratuite
- excellent support du sql avec window functions
- types de donnees riches (array, json, etc)
- facile a dockeriser
- bonne documentation

### interrogation sql: postgresql direct

**justification:**
- meme base que le stockage donc pas de duplication
- performances suffisantes pour ce volume
- pas besoin d'outil supplementaire

## 3. organisation des donnees

### structure des dossiers
```
data/
├── raw/                    # donnees brutes non transformees
│   ├── books_*.json
│   ├── quotes_*.json
│   ├── librairies_anonymisees.json
│   └── librairies_geocodees.json
└── analyses/              # resultats des requetes sql
    ├── requete_1.csv
    └── ...
```

### couches de transformation

**couche 1: raw (donnees brutes)**
- donnees telles que collectees
- aucune transformation
- format json avec timestamp

**couche 2: cleaned (donnees nettoyees)**
- conversion des devises (gbp vers eur)
- normalisation des dates
- suppression des doublons
- anonymisation rgpd
- geocodage des adresses

**couche 3: analytics (base postgres)**
- donnees chargees en tables relationnelles
- index pour les performances
- prete pour les requetes sql

### convention de nommage

**fichiers json:**
- format: `{source}_{timestamp}.json`
- exemple: `books_20260106_101530.json`

**tables postgres:**
- noms en minuscules pluriel
- exemple: `livres`, `citations`, `librairies`

**colonnes:**
- snake_case en francais
- exemple: `prix_eur`, `date_collecte`, `nom_librairie`

## 4. modelisation des donnees

### modele de donnees

on utilise un modele en etoile simplifie:
```
livres (table de faits)
├── id (pk)
├── titre
├── prix_gbp
├── prix_eur
├── note
├── disponibilite
├── categorie
└── date_collecte

citations (table de faits)
├── id (pk)
├── texte
├── auteur
├── tags (array)
└── date_collecte

librairies (table de dimension)
├── id (pk)
├── nom_librairie
├── adresse
├── code_postal
├── ville
├── specialite
├── date_partenariat
├── longitude
├── latitude
└── geocodage_score
```

### justification du modele

**pourquoi pas de tables de dimension separees?**
- le volume de donnees est faible (moins de 10000 lignes)
- pas de dimension partagee entre les sources
- la denormalisation simplifie les requetes

**pourquoi des tables separees par source?**
- chaque source a un schema different
- facilite la maintenance
- permet d'ajouter facilement de nouvelles sources

**utilisation de array pour les tags**
- evite une table de liaison
- simplifie les requetes
- postgres supporte bien ce type

## 5. conformite rgpd

### donnees personnelles identifiees

**dans le fichier partenaire_librairies.xlsx:**
- contact_nom: nom de la personne (donnee personnelle)
- contact_email: email (donnee personnelle)
- contact_telephone: telephone (donnee personnelle)
- ca_annuel: chiffre d'affaires (donnee confidentielle)

**dans les autres sources:**
- aucune donnee personnelle (sites publics, api publique)

### mesures de protection

**anonymisation par hachage sha256:**
- les donnees personnelles sont hashees avant stockage
- impossible de retrouver la donnee originale
- on garde un identifiant unique pour les analyses

**suppression des donnees sensibles:**
- le ca_annuel est supprime car confidentiel
- les donnees originales ne sont jamais stockees en clair

**isolation des donnees brutes:**
- le fichier excel original reste en local
- jamais commit dans git
- .gitignore configure

### gestion du droit a l'effacement

pour supprimer les donnees d'une librairie:
```sql
-- supprimer par hash si on l'a
delete from librairies where contact_nom_hash = 'xxxx';

-- ou supprimer par nom de librairie
delete from librairies where nom_librairie = 'nom de la librairie';
```

un script python peut etre cree pour automatiser ca:
```python
def supprimer_librairie(nom):
    query = "delete from librairies where nom_librairie = :nom"
    conn.execute(text(query), {'nom': nom})
```

### base legale du traitement

- interet legitime: analyse de marche et partenariats commerciaux
- les donnees sont anonymisees donc le risque est minimal
- conservation limitee dans le temps (possibilite de purge)

## 6. infrastructure docker

### services deploys

**postgres 15:**
- base de donnees principale
- port 5433 (pour eviter conflit)
- volume persistant pour les donnees
- initialisation automatique du schema

### avantages de docker

- reproductibilite: meme environnement partout
- isolation: pas de conflit avec d'autres projets
- simplicite: un seul fichier de config
- portabilite: fonctionne sur windows, mac, linux

### commandes utiles
```bash
# lancer l'infrastructure
docker-compose up -d

# voir les logs
docker-compose logs -f

# arreter
docker-compose down

# tout supprimer (attention aux donnees)
docker-compose down -v
```