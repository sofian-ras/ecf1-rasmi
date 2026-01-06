"""
Nettoyage : On enlève les symboles inutiles (comme le "£") pour transformer les prix en vrais chiffres.

L'expert API : Pour les librairies, on n'a que l'adresse. Ce fichier demande à un service du gouvernement : "Dis-moi où se trouve exactement cette adresse sur une carte". Le service nous répond avec les points GPS.
"""

import json
import pandas as pd
from datetime import datetime

class TransformationDonnees:
    
    def __init__(self):
        # taux de conversion gbp vers eur (approximatif)
        self.taux_gbp_eur = 1.17
    
    def charger_json(self, fichier):
        """charge un fichier json"""
        with open(fichier, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def transformer_livres(self, fichiers_livres):
        """transforme les donnees des livres"""
        print("transformation des livres...")
        
        tous_les_livres = []
        
        # charger tous les fichiers de livres
        for fichier in fichiers_livres:
            data = self.charger_json(fichier)
            tous_les_livres.extend(data)
        
        df = pd.DataFrame(tous_les_livres)
        
        # nettoyer et transformer
        # convertir le prix en float
        df['prix_gbp'] = df['prix'].astype(float)
        
        # convertir en euros
        df['prix_eur'] = df['prix_gbp'] * self.taux_gbp_eur
        df['prix_eur'] = df['prix_eur'].round(2)
        
        # nettoyer la disponibilite
        df['disponibilite'] = df['disponibilite'].str.strip()
        
        # convertir la date de collecte
        df['date_collecte'] = pd.to_datetime(df['date_collecte'])
        
        # supprimer les doublons sur le titre
        df = df.drop_duplicates(subset=['titre'], keep='first')
        
        # selectionner les colonnes finales
        df_final = df[['titre', 'prix_gbp', 'prix_eur', 'note', 'disponibilite', 'categorie', 'date_collecte']]
        
        print(f"nombre de livres apres transformation: {len(df_final)}")
        
        return df_final
    
    def transformer_citations(self, fichiers_citations):
        """transforme les donnees des citations"""
        print("transformation des citations...")
        
        toutes_les_citations = []
        
        # charger tous les fichiers de citations
        for fichier in fichiers_citations:
            data = self.charger_json(fichier)
            toutes_les_citations.extend(data)
        
        df = pd.DataFrame(toutes_les_citations)
        
        # nettoyer le texte
        df['texte'] = df['texte'].str.strip()
        df['auteur'] = df['auteur'].str.strip()
        
        # convertir la date
        df['date_collecte'] = pd.to_datetime(df['date_collecte'])
        
        # supprimer les doublons sur le texte
        df = df.drop_duplicates(subset=['texte'], keep='first')
        
        print(f"nombre de citations apres transformation: {len(df)}")
        
        return df
    
import pandas as pd

class TransformationDonnees:
    def __init__(self):
        self.taux_gbp_eur = 1.17

    def transformer_librairies_df(self, df):
        """Nettoie le DataFrame des librairies (version appelée par le main)"""
        print("Nettoyage des données librairies...")
        
        # Nettoyage basique
        if 'nom_librairie' in df.columns:
            df['nom_librairie'] = df['nom_librairie'].str.strip()
        
        # RGPD : Suppression des données sensibles
        colonnes_a_supprimer = ['nom_responsable', 'email', 'telephone']
        for col in colonnes_a_supprimer:
            if col in df.columns:
                df = df.drop(columns=[col])
                
        return df

# test
if __name__ == "__main__":
    transform = TransformationDonnees()
    
    # tester avec un fichier
    import glob
    fichiers_livres = glob.glob('../data/raw/books_*.json')
    if fichiers_livres:
        df_livres = transform.transformer_livres(fichiers_livres)
        print(df_livres.head())