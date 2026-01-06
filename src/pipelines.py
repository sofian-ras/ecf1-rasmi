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

    def close_spider(self, spider):
        self.file.write('\n]')
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict(), ensure_ascii=False) + ",\n"
        self.file.write(line)
        return item

class PostgresPipeline:
    def __init__(self):
        # Configuration Postgres
        self.conn = psycopg2.connect(
            host="localhost", port="5433", database="ecf_db",
            user="admin_rasmi", password="password123"
        )
        self.cur = self.conn.cursor()

        # Configuration MinIO
        self.bucket_name = "ecf-data" # <--- Change ici si tu veux un autre nom
        self.s3_client = boto3.client(
            's3', endpoint_url='http://localhost:9000',
            aws_access_key_id='minioadmin', aws_secret_access_key='minioadmin',
            region_name='us-east-1'
        )
        
        # Auto-création du Bucket
        try:
            self.s3_client.head_bucket(Bucket=self.bucket_name)
        except:
            self.s3_client.create_bucket(Bucket=self.bucket_name)

    def open_spider(self, spider):
        if spider.name == 'books':
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS books (
                    id SERIAL PRIMARY KEY, titre TEXT, prix TEXT, 
                    note TEXT, disponibilite TEXT, categorie TEXT
                );
            """)
        elif spider.name == 'quotes':
            self.cur.execute("""
                CREATE TABLE IF NOT EXISTS quotes (
                    id SERIAL PRIMARY KEY, texte TEXT, auteur TEXT, tags TEXT
                );
            """)
        self.conn.commit()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        
        # UPLOAD DIRECT IMAGE VERS MINIO
        if adapter.get('image_urls'):
            try:
                url = adapter.get('image_urls')[0]
                nom_fichier = url.split('/')[-1]
                reponse = requests.get(url, timeout=10)
                if reponse.status_code == 200:
                    self.s3_client.upload_fileobj(
                        BytesIO(reponse.content), 
                        self.bucket_name, 
                        f"images/{nom_fichier}"
                    )
            except Exception as e:
                print(f" Erreur MinIO direct : {e}")

        # INSERTION SQL
        try:
            if spider.name == 'books':
                self.cur.execute("""
                    INSERT INTO books (titre, prix, note, disponibilite, categorie)
                    VALUES (%s, %s, %s, %s, %s)
                """, (adapter.get('titre'), adapter.get('prix'), adapter.get('note'),
                      adapter.get('disponibilite'), adapter.get('categorie')))
            elif spider.name == 'quotes':
                tags = ", ".join(adapter.get('tags', []))
                self.cur.execute("""
                    INSERT INTO quotes (texte, auteur, tags)
                    VALUES (%s, %s, %s)
                """, (adapter.get('texte'), adapter.get('auteur'), tags))
            self.conn.commit()
        except Exception as e:
            self.conn.rollback()
        return item

    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()