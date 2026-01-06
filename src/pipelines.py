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

    def upload_image_direct(self, item):
        if item.get('image_urls'):
            url = item['image_urls'][0]
            reponse = requests.get(url)
            image_en_memoire = BytesIO(reponse.content)
            
            # 2. On l'envoie direct sur MinIO
            nom_fichier = url.split('/')[-1]
            self.s3_client.upload_fileobj(
                image_en_memoire, 
                "mon-bucket", 
                f"images/{nom_fichier}"
            )

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
            print(f"Erreur SQL : {e}")
            self.conn.rollback() # ICI on peut faire un rollback car self.conn existe
            
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()