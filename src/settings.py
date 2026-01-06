# settings.py
BOT_NAME = 'scraping'

SPIDER_MODULES = ['src.spiders']
NEWSPIDER_MODULE = 'src.spiders'

# respect des sites
ROBOTSTXT_OBEY = True
DOWNLOAD_DELAY = 1  # 1 seconde entre chaque requete
CONCURRENT_REQUESTS = 1

# user agent identifiable
USER_AGENT = 'datapulse-student-bot (educational-project)'

# cookies et redirections
COOKIES_ENABLED = False

# pipelines pour sauvegarder les donnees
ITEM_PIPELINES = {
   'src.pipelines.JsonPipeline': 300,
   'src.pipelines.PostgresPipeline': 400,
}