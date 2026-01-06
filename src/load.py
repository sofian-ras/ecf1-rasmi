import psycopg2
from sqlalchemy import create_engine

def charger_dans_postgres(df, nom_table):
    """
    Charge un DataFrame Pandas dans une table PostgreSQL.
    """
    try:
        # Configuration de la connexion (on utilise les mêmes paramètres que ton docker)
        conn_string = "postgresql://admin_rasmi:password123@localhost:5433/ecf_db"
        engine = create_engine(conn_string)
        
        print(f"Chargement de {len(df)} lignes dans la table '{nom_table}'...")
        
        # On utilise to_sql de Pandas pour une insertion rapide
        # if_exists='append' permet de rajouter les données sans supprimer la table
        df.to_sql(nom_table, engine, if_exists='append', index=False)
        
        print(f"Succès : Données chargées dans {nom_table}")
        
    except Exception as e:
        print(f"Erreur lors du chargement dans Postgres : {e}")

if __name__ == "__main__":
    print("Module Load prêt.")