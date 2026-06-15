from django.apps import AppConfig

import nltk

class App1Config(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "app1"

    # def ready(self):
    #     """应用启动时确保nltk资源已下载"""
    #     try:
    #         nltk.data.find('tokenizers/punkt')
    #         nltk.data.find('corpora/stopwords')
    #         nltk.data.find('corpora/wordnet')
    #         nltk.data.find('corpora/omw-1.4')
    #     except LookupError:
    #         nltk.download('punkt')
    #         nltk.download('stopwords')
    #         nltk.download('wordnet')
    #         nltk.download('omw-1.4')