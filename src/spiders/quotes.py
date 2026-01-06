"""
Ce sont (books.py et quotes.py) des petits robots qui vont sur les sites web. Ils lisent les pages comme un humain, notent les titres, les prix et les auteurs, puis tournent les pages automatiquement jusqu'à la fin.
"""

import scrapy
from datetime import datetime
from src.items import QuoteItem

class QuotesSpider(scrapy.Spider):
    name = 'quotes'
    allowed_domains = ['quotes.toscrape.com']
    start_urls = ['https://quotes.toscrape.com/']

    def parse(self, response):
        # recuperer toutes les citations
        for quote in response.css('div.quote'):
            item = QuoteItem()
            
            # texte de la citation
            item['texte'] = quote.css('span.text::text').get()
            
            # auteur
            item['auteur'] = quote.css('small.author::text').get()
            
            # tags (liste)
            item['tags'] = quote.css('a.tag::text').getall()
            
            # date de collecte
            item['date_collecte'] = datetime.now().isoformat()
            
            yield item
        
        # pagination
        next_page = response.css('li.next a::attr(href)').get()
        if next_page:
            yield response.follow(next_page, self.parse)