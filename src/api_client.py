import requests
import pandas as pd
import time

class GeocodeurLibrairies:
    def __init__(self):
        self.url_api = "https://api-adresse.data.gouv.fr/search/"

    def geocoder_adresse(self, adresse, code_postal):
        query = f"{adresse} {code_postal}"
        try:
            response = requests.get(self.url_api, params={'q': query, 'limit': 1}, timeout=5)
            if response.status_code == 200:
                data = response.json()
                if data['features']:
                    feature = data['features'][0]
                    return {
                        'lon': feature['geometry']['coordinates'][0],
                        'lat': feature['geometry']['coordinates'][1],
                        'score': feature['properties']['score']
                    }
            return {'lon': 0, 'lat': 0, 'score': 0}
        except Exception as e:
            return {'lon': 0, 'lat': 0, 'score': 0}

    def enrichir_dataframe(self, df):
        print("Enrichissement des données via API Adresse...")
        longitudes, latitudes, scores = [], [], []
        for _, row in df.iterrows():
            time.sleep(0.1) 
            res = self.geocoder_adresse(row.get('adresse', ''), row.get('code_postal', ''))
            longitudes.append(res['lon'])
            latitudes.append(res['lat'])
            scores.append(res['score'])
        df['longitude'] = longitudes
        df['latitude'] = latitudes
        df['geocodage_score'] = scores
        return df