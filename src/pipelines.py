"""
Dès que les robots trouvent une info, ces fichiers décident où la ranger
"""
import json
import os
import requests
from io import BytesIO
import boto3
import psycopg2
from datetime import datetime
from itemadapter import ItemAdapter

class JsonPipeline:
    def open_spider(self, spider):
        os.makedirs('data/raw', exist_ok=True)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'data/raw/{spider.name}_{timestamp}.json'
        self.file = open(filename, 'w', encoding='utf-8')
        self.file.write('[\n')
        self.first_item = True

    def close_spider(self, spider):
        self.file.write('\n]')
        self.file.close()

    def process_item(self, item, spider):
        # On ne met QUE l'écriture fichier ici ! Pas de SQL.
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + "\n"
        self.file.write(line)
        return item

class PostgresPipeline:
    """Envoie les données vers PostgreSQL"""
    def __init__(self):
        # Paramètres de connexion
        self.conn = psycopg2.connect(
            host="localhost",
            port="5433",
            database="ecf_db",
            user="admin_rasmi",
            password="password123"
        )
        self.cur = self.conn.cursor()

    def open_spider(self, spider):
        """
        Cette fonction s'exécute AVANT que le robot ne commence à scraper.
        Elle crée la table si elle n'existe pas.
        """
        if spider.name == 'books':
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY,
                    titre TEXT,
                    prix TEXT,
                    note TEXT,
                    disponibilite TEXT,
                    categorie TEXT
                );
            """)
        elif spider.name == 'quotes':
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id SERIAL PRIMARY KEY,
                    texte TEXT,
                    auteur TEXT,
                    tags TEXT
                );
            """)
        self.conn.commit()
        print(f"✅ Table pour le spider '{spider.name}' vérifiée/créée.")

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        try:
            if spider.name == 'books':
                self.cur.execute("""
                    INSERT INTO books (titre, prix, note, disponibilite, categorie)
                    VALUES (%s, %s, %s, %s, %s)
                """, (
                    adapter.get('titre'), adapter.get('prix'), adapter.get('note'),
                    adapter.get('disponibilite'), adapter.get('categorie')
                ))
            elif spider.name == 'quotes':
                tags = ", ".join(adapter.get('tags', []))
                self.cur.execute("""
                    INSERT INTO quotes (texte, auteur, tags)
                    VALUES (%s, %s, %s)
                """, (
                    adapter.get('texte'), adapter.get('auteur'), tags
                ))
            
            self.conn.commit()
        except Exception as e:
            print(f" Erreur SQL dans {spider.name} : {e}")
            self.conn.rollback()
            
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()