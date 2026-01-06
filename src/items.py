import scrapy

class BookItem(scrapy.Item):
    titre = scrapy.Field()
    prix = scrapy.Field()
    note = scrapy.Field()
    disponibilite = scrapy.Field()
    categorie = scrapy.Field()
    date_collecte = scrapy.Field()
    image_urls = scrapy.Field()
    images = scrapy.Field()

class QuoteItem(scrapy.Item):
    texte = scrapy.Field()
    auteur = scrapy.Field()
    tags = scrapy.Field()
    date_collecte = scrapy.Field()