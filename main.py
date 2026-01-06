"""
RÔLE : Point d'entrée unique du pipeline ETL.
C'est le bouton "Démarrer". Il lance tout le travail dans le bon ordre : d'abord la récolte, puis le nettoyage, et enfin le rangement sur Internet.
"""

from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from src.minio_client import MinioUploader
from src.import_excel import charger_excel
from src.api_client import GeocodeurLibrairies
from src.transform import TransformationDonnees
from src.load import charger_dans_postgres

def run_pipeline():
    print("--- debut du pipeline ecf ---")

    # 1. scraping (extraction web)
    print("etape 1 : scraping books et quotes...")
    process = CrawlerProcess(get_project_settings())
    process.crawl('books')
    process.crawl('quotes')
    process.start() # le script attend la fin du scraping

# 2. EXCEL & API (Enrichissement)
    print("\n>>> ETAPE 2 : IMPORT EXCEL & API ADRESSE...")
    df_brut = charger_excel('data/partenaire_librairies.xlsx')
    
    if df_brut.empty:
        print("Erreur : Le DataFrame Excel est vide ou introuvable.")
        return

    # On initialise la classe et on appelle la méthode
    geo = GeocodeurLibrairies()
    df_enrichi = geo.enrichir_dataframe(df_brut)
    
# 3. TRANSFORMATION (Nettoyage & RGPD)
    print("\n>>> ETAPE 3 : TRANSFORMATION & RGPD...")
    
    # On crée l'objet (l'instance de la classe)
    transformer = TransformationDonnees()
    
    # On appelle la méthode de la classe sur notre DataFrame
    df_final = transformer.transformer_librairies_df(df_enrichi)

    # 4. chargement final
    print("etape 4 : chargement dans postgres...")
    charger_dans_postgres(df_final, "librairies")

    print("--- pipeline termine avec succes ! ---")

    # 5. upload vers MinIO
    print("\n>>> ETAPE 5 : UPLOAD VERS MINIO...")
    try:
        uploader = MinioUploader()
        uploader.uploader_dossier('data')
        print("Upload vers MinIO termine avec succes !")
    except Exception as e:
        print(f"Erreur lors de l'upload vers MinIO : {e}")
    
    print("--- fin du pipeline ecf ---")

if __name__ == "__main__":
    run_pipeline()