"""
Ce sont (books.py et quotes.py) des petits robots qui vont sur les sites web. Ils lisent les pages comme un humain, notent les titres, les prix et les auteurs, puis tournent les pages automatiquement jusqu'à la fin.
"""
import scrapy
from datetime import datetime
from src.items import BookItem

class BooksSpider(scrapy.Spider):
    name = 'books'
    allowed_domains = ['books.toscrape.com']
    start_urls = ['https://books.toscrape.com/']

    def parse(self, response):
        for book in response.css('article.product_pod'):
            item = BookItem()
            
            # Titre
            item['titre'] = book.css('h3 a::attr(title)').get()
            
            # Prix
            prix_text = book.css('p.price_color::text').get()
            item['prix'] = prix_text.replace('£', '').strip()
            
            # Note
            note_class = book.css('p.star-rating::attr(class)').get()
            notes_map = {'One': 1, 'Two': 2, 'Three': 3, 'Four': 4, 'Five': 5}
            note_word = note_class.replace('star-rating ', '')
            item['note'] = notes_map.get(note_word, 0)
            
            # Disponibilité
            item['disponibilite'] = book.css('p.instock.availability::text').getall()[-1].strip()
            
            # Catégorie
            item['categorie'] = response.css('ul.breadcrumb li:nth-child(3) a::text').get()
            
            # --- AJOUT POUR LES IMAGES ---
            # 1. Récupérer l'URL relative de l'image
            relative_url = book.css('div.image_container img::attr(src)').get()
            # 2. Convertir en URL absolue et mettre dans une LISTE (important)
            item['image_urls'] = [response.urljoin(relative_url)]
            # ------------------------------

            item['date_collecte'] = datetime.now().isoformat()
            
            yield item
        
        # Pagination
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)