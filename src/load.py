import psycopg2
from sqlalchemy import create_engine

def charger_dans_postgres(df, nom_table):
    """
    Charge un DataFrame Pandas dans une table PostgreSQL.
    """
    try:
        # Configuration de la connexion
        conn_string = "postgresql://admin_rasmi:password123@localhost:5433/ecf_db"
        engine = create_engine(conn_string)
        
        print(f"Chargement de {len(df)} lignes dans la table '{nom_table}'...")
        df.to_sql(nom_table, engine, if_exists='replace', index=False)
        print(f"Succès : La table '{nom_table}' a été créée et chargée.")
    except Exception as e:
        print(f"Erreur lors du chargement dans Postgres : {e}")

if __name__ == "__main__":
    print("Module Load prêt.")