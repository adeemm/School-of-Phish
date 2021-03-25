from flask import Flask
from flask_caching import Cache
import settings


flask_app = Flask(__name__)

cache = Cache(config={'CACHE_TYPE': 'simple', 'CACHE_DEFAULT_TIMEOUT': 86400})
cache.init_app(flask_app)

settings.load_settings("settings.json")

if __name__ == '__main__':
    flask_app.run(use_debugger=True)


import controllers.views
import controllers.api
