import pandas as pd
import os

def charger_excel(chemin_fichier):
    """
    Charge le fichier Excel des partenaires et vérifie s'il existe.
    """
    if not os.path.exists(chemin_fichier):
        # Pour le test, on crée un DataFrame vide si le fichier est absent
        print(f"Erreur : Le fichier {chemin_fichier} est introuvable.")
        return pd.DataFrame()
    
    print(f"Chargement du fichier : {chemin_fichier}")
    # On lit le Excel
    df = pd.read_excel(chemin_fichier)
    
    # Nettoyage rapide des colonnes (enlever les espaces)
    df.columns = [c.strip().lower().replace(' ', '_') for c in df.columns]
    
    return df

if __name__ == "__main__":
    # Test local
    df = charger_excel('data/partenaire_librairies.xlsx')
    print(df.head())