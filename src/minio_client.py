"""
le coffre-fort à distance,
Une fois que tout est fini, ce fichier prend tous nos dossiers  et les envoie dans MinIO. C'est ce qu'on appelle le "Cloud". Comme ça, même si notre ordinateur casse, les données sont en sécurité
"""
import os
import boto3
from botocore.client import Config

class MinioUploader:
    def __init__(self):
        # Configuration MinIO (identifiants par défaut de l'image Docker)
        self.s3 = boto3.resource('s3',
            endpoint_url='http://localhost:9000',
            aws_access_key_id='minioadmin',
            aws_secret_access_key='minioadmin',
            config=Config(signature_version='s3v4'),
            region_name='us-east-1')
        
        self.bucket_name = 'ecf-storage'
        self.creer_bucket_si_besoin()

    def creer_bucket_si_besoin(self):
        bucket = self.s3.Bucket(self.bucket_name)
        if not bucket.creation_date:
            bucket.create()
            print(f"Bucket '{self.bucket_name}' créé avec succès.")

    def uploader_dossier(self, dossier_local):
        print(f"Synchronisation de {dossier_local} vers MinIO...")
        for root, dirs, files in os.walk(dossier_local):
            for file in files:
                chemin_local = os.path.join(root, file)
                # On crée un chemin relatif pour MinIO
                chemin_minio = os.path.relpath(chemin_local, dossier_local)
                
                self.s3.Bucket(self.bucket_name).upload_file(chemin_local, chemin_minio)
                print(f"  -> Uploadé : {chemin_minio}")

if __name__ == "__main__":
    uploader = MinioUploader()
    uploader.uploader_dossier('data')