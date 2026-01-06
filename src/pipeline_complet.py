import subprocess
import os
import glob
from import_excel import ImportLibrairies
from api_client import ApiAdresseClient
from transform import TransformationDonnees
from load import ChargementBase

def etape_1_scraping():
    """lance les scrapers"""
    print("=" * 50)
    print("etape 1: scraping des sites web")
    print("=" * 50)
    
    os.chdir('scraping')
    
    print("\nlancement du scraper books...")
    subprocess.run(['scrapy', 'crawl', 'books'])
    
    print("\nlancement du scraper quotes...")
    subprocess.run(['scrapy', 'crawl', 'quotes'])
    
    os.chdir('..')
    print("\nscraping termine!")

def etape_2_import_excel():
    """importe et anonymise le fichier excel"""
    print("\n" + "=" * 50)
    print("etape 2: import du fichier excel")
    print("=" * 50)
    
    importer = ImportLibrairies('data/partenaire_librairies.xlsx')
    df = importer.importer_et_anonymiser()
    data = importer.sauvegarder_json(df, 'data/raw/librairies_anonymisees.json')
    
    print("\nimport termine!")
    return data

def etape_3_geocodage(librairies_data):
    """geocode les adresses des librairies"""
    print("\n" + "=" * 50)
    print("etape 3: geocodage des adresses")
    print("=" * 50)
    
    client = ApiAdresseClient()
    librairies_geocodees = client.geocoder_librairies(librairies_data)
    
    import json
    with open('data/raw/librairies_geocodees.json', 'w', encoding='utf-8') as f:
        json.dump(librairies_geocodees, f, ensure_ascii=False, indent=2, default=str)
    
    print("\ngeocodage termine!")
    return librairies_geocodees

def etape_4_transformation():
    """transforme toutes les donnees"""
    print("\n" + "=" * 50)
    print("etape 4: transformation des donnees")
    print("=" * 50)
    
    transform = TransformationDonnees()
    
    # transformer les livres
    fichiers_livres = glob.glob('data/raw/books_*.json')
    df_livres = transform.transformer_livres(fichiers_livres)
    
    # transformer les citations
    fichiers_citations = glob.glob('data/raw/quotes_*.json')
    df_citations = transform.transformer_citations(fichiers_citations)
    
    # transformer les librairies
    df_librairies = transform.transformer_librairies('data/raw/librairies_geocodees.json')
    
    print("\ntransformation terminee!")
    return df_livres, df_citations, df_librairies

def etape_5_chargement(df_livres, df_citations, df_librairies):
    """charge les donnees dans la base"""
    print("\n" + "=" * 50)
    print("etape 5: chargement dans la base de donnees")
    print("=" * 50)
    
    chargement = ChargementBase()
    
    # creer le schema
    chargement.creer_schema()
    
    # charger les donnees
    chargement.charger_livres(df_livres)
    chargement.charger_citations(df_citations)
    chargement.charger_librairies(df_librairies)
    
    # verifier
    chargement.verifier_chargement()
    
    print("\nchargement termine!")

def pipeline_complet():
    """execute tout le pipeline"""
    print("debut du pipeline complet")
    print("=" * 50)
    
    # etape 1: scraping
    etape_1_scraping()
    
    # etape 2: import excel
    librairies_data = etape_2_import_excel()
    
    # etape 3: geocodage
    librairies_geocodees = etape_3_geocodage(librairies_data)
    
    # etape 4: transformation
    df_livres, df_citations, df_librairies = etape_4_transformation()
    
    # etape 5: chargement
    etape_5_chargement(df_livres, df_citations, df_librairies)
    
    print("\n" + "=" * 50)
    print("pipeline termine avec succes!")
    print("=" * 50)

if __name__ == "__main__":
    # on peut lancer tout ou juste une etape
    import sys
    
    if len(sys.argv) > 1:
        etape = sys.argv[1]
        if etape == "scraping":
            etape_1_scraping()
        elif etape == "import":
            etape_2_import_excel()
        elif etape == "transform":
            etape_4_transformation()
        elif etape == "load":
            df_livres, df_citations, df_librairies = etape_4_transformation()
            etape_5_chargement(df_livres, df_citations, df_librairies)
    else:
        pipeline_complet()