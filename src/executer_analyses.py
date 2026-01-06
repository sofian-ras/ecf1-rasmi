from sqlalchemy import create_engine, text
import pandas as pd

class ExecuteurAnalyses:
    
    def __init__(self):
        self.engine = create_engine('postgresql://dataengineer:password123@localhost:5433/datapulse')
    
    def executer_fichier_sql(self, fichier_sql):
        """execute toutes les requetes d'un fichier sql"""
        print(f"execution des requetes du fichier: {fichier_sql}")
        print("=" * 80)
        
        with open(fichier_sql, 'r', encoding='utf-8') as f:
            contenu = f.read()
        
        # separer les requetes (on prend celles qui finissent par ;)
        requetes = [q.strip() for q in contenu.split(';') if q.strip() and not q.strip().startswith('--')]
        
        resultats = []
        
        for i, requete in enumerate(requetes, 1):
            # ignorer les commentaires purs
            if requete.startswith('--') or not requete:
                continue
            
            print(f"\nrequete {i}:")
            print("-" * 80)
            
            # extraire le premier commentaire comme titre
            lignes = requete.split('\n')
            titre = None
            for ligne in lignes:
                if ligne.strip().startswith('--'):
                    titre = ligne.strip('- \n')
                    break
            
            if titre:
                print(f"titre: {titre}")
            
            try:
                with self.engine.connect() as conn:
                    result = conn.execute(text(requete))
                    
                    # si c'est une requete select, afficher les resultats
                    if result.returns_rows:
                        df = pd.DataFrame(result.fetchall(), columns=result.keys())
                        print(f"\nnombre de lignes: {len(df)}")
                        print("\nresultat:")
                        print(df.to_string())
                        resultats.append({
                            'numero': i,
                            'titre': titre,
                            'dataframe': df
                        })
                    else:
                        print("requete executee avec succes (pas de resultat)")
                
            except Exception as e:
                print(f"erreur lors de l'execution: {e}")
        
        print("\n" + "=" * 80)
        print(f"execution terminee: {len(resultats)} requetes executees")
        
        return resultats
    
    def sauvegarder_resultats_csv(self, resultats, dossier='../data/analyses'):
        """sauvegarde les resultats en csv"""
        import os
        os.makedirs(dossier, exist_ok=True)
        
        for resultat in resultats:
            nom_fichier = f"requete_{resultat['numero']}.csv"
            chemin = os.path.join(dossier, nom_fichier)
            resultat['dataframe'].to_csv(chemin, index=False, encoding='utf-8')
            print(f"resultat sauvegarde: {chemin}")

# execution
if __name__ == "__main__":
    executeur = ExecuteurAnalyses()
    
    # executer toutes les analyses
    resultats = executeur.executer_fichier_sql('../sql/analyses.sql')
    
    # sauvegarder les resultats
    executeur.sauvegarder_resultats_csv(resultats)