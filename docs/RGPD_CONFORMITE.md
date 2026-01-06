# document de conformite rgpd

## 1. inventaire des donnees personnelles

### donnees personnelles collectees

| donnee | source | type | caractere sensible |
|--------|--------|------|-------------------|
| contact_nom | fichier excel | identite | oui - donnee personnelle |
| contact_email | fichier excel | coordonnees | oui - donnee personnelle |
| contact_telephone | fichier excel | coordonnees | oui - donnee personnelle |
| ca_annuel | fichier excel | financier | oui - donnee confidentielle |

### donnees non personnelles

| donnee | source | justification |
|--------|--------|---------------|
| titres de livres | books.toscrape.com | donnees publiques fictives |
| citations | quotes.toscrape.com | donnees publiques |
| adresses de librairies | fichier excel | donnees professionnelles publiques |
| coordonnees gps | api adresse | donnees publiques |

## 2. base legale du traitement

### pour les donnees personnelles du fichier excel

**base legale: interet legitime**
- finalite: gestion des partenariats commerciaux
- necessite: identifier les contacts des librairies partenaires
- proportionnalite: seules les donnees necessaires sont collectees

**mesures de protection:**
- anonymisation immediate par hachage
- suppression des donnees en clair
- acces restreint aux donnees brutes

### pour les donnees publiques

**base legale: interet legitime**
- finalite: analyse de marche et recherche
- les donnees sont deja publiques
- utilisation conforme aux cgu des sites

## 3. traitement des donnees personnelles

### methode d'anonymisation

**hachage sha256:**
```python
import hashlib

def anonymiser(valeur):
    hash_object = hashlib.sha256(str(valeur).encode())
    return hash_object.hexdigest()[:16]
```

**caracteristiques:**
- irreversible: impossible de retrouver la donnee originale
- deterministe: meme valeur donne meme hash
- unique: chaque valeur a un hash different

**exemple:**
- donnee originale: "marie.dubois@librairie.fr"
- apres anonymisation: "a3f5e8d9c2b1f4e7"

### cycle de vie des donnees

**collecte:**
1. reception du fichier excel
2. lecture en memoire
3. jamais stocke en clair

**traitement:**
1. anonymisation immediate
2. suppression des colonnes sensibles
3. sauvegarde uniquement des donnees anonymisees

**stockage:**
1. fichiers json avec donnees anonymisees
2. base postgres avec donnees anonymisees
3. aucune donnee en clair persistante

**suppression:**
1. sur demande via script
2. purge automatique possible (a implementer)

## 4. droits des personnes concernees

### droit d'acces

les personnes peuvent demander quelles donnees nous avons sur elles.

**procedure:**
1. la personne contacte l'entreprise
2. identification avec nom de librairie
3. verification de l'identite
4. communication des donnees anonymisees

### droit de rectification

les personnes peuvent demander a corriger leurs donnees.

**procedure:**
1. reception de la demande
2. mise a jour du fichier source
3. re-execution du pipeline avec nouvelles donnees

### droit a l'effacement

les personnes peuvent demander la suppression de leurs donnees.

**procedure:**
1. reception de la demande
2. execution du script de suppression
3. confirmation a la personne

**script de suppression:**
```python
from sqlalchemy import create_engine, text

def supprimer_donnees_librairie(nom_librairie):
    engine = create_engine('postgresql://dataengineer:password123@localhost:5433/datapulse')
    
    with engine.connect() as conn:
        # supprimer de la base
        conn.execute(
            text("delete from librairies where nom_librairie = :nom"),
            {'nom': nom_librairie}
        )
        conn.commit()
    
    print(f"donnees supprimees pour: {nom_librairie}")

# utilisation
supprimer_donnees_librairie("Librairie du Marais")
```

### droit a la portabilite

les personnes peuvent demander leurs donnees dans un format lisible.

**procedure:**
1. extraction des donnees de la base
2. export en csv ou json
3. envoi securise a la personne

## 5. mesures de securite

### protection des donnees

**anonymisation:**
- toutes les donnees personnelles sont hashees
- pas de stockage en clair

**isolation:**
- fichier excel original jamais commit dans git
- .gitignore configure pour exclure les donnees sensibles

**acces restreint:**
- base de donnees protegee par mot de passe
- acces uniquement en local

### fichier .gitignore
```
# donnees sensibles
data/*.xlsx
data/raw/*.json
data/analyses/*.csv

# environnement
venv/
__pycache__/
*.pyc

# secrets
.env
config.ini
```

### bonnes pratiques

**developpement:**
- jamais de donnees reelles en clair dans le code
- utilisation de variables d'environnement pour les secrets
- tests avec des donnees fictives

**production:**
- chiffrement des connexions (ssl)
- sauvegardes regulieres chiffrees
- logs anonymises

## 6. duree de conservation

### donnees de production

**donnees anonymisees:**
- conservation: 2 ans
- justification: analyses historiques

**donnees brutes:**
- conservation: 30 jours
- justification: debuggage et verifications

### procedure de purge
```python
from datetime import datetime, timedelta

def purger_anciennes_donnees():
    limite = datetime.now() - timedelta(days=730)  # 2 ans
    
    query = """
    delete from librairies 
    where date_import < :limite
    """
    
    conn.execute(text(query), {'limite': limite})
```

## 7. transfert de donnees

### pas de transfert hors ue

- toutes les donnees restent en local
- base de donnees sur serveur local
- pas d'api externe pour les donnees personnelles

### api utilisees

**api adresse (data.gouv.fr):**
- api publique francaise
- aucune donnee personnelle envoyee
- uniquement des adresses professionnelles publiques

## 8. responsabilites

### responsable du traitement

datapulse analytics
- decide des finalites et moyens du traitement
- responsable de la conformite rgpd

### sous-traitants

aucun sous-traitant pour le moment

### data protection officer (dpo)

a nommer si necessaire selon la taille de l'entreprise

## 9. registre des traitements

### traitement: gestion des librairies partenaires

- finalite: gestion commerciale
- categorie de donnees: identite, coordonnees
- categorie de personnes: contacts professionnels
- destinataires: equipe commerciale uniquement
- transferts: aucun
- duree de conservation: 2 ans
- mesures de securite: anonymisation, acces restreint

## 10. incidents et violations

### procedure en cas de violation

1. detection de l'incident
2. evaluation de la gravite
3. notification a la cnil sous 72h si necessaire
4. information des personnes concernees si risque eleve
5. documentation de l'incident

### registre des incidents

a maintenir dans un document separe avec:
- date de l'incident
- nature de l'incident
- donnees concernees
- mesures prises
- notifications effectuees