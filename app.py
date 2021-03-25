from flask import Flask
import controllers.views
import controllers.api
import settings
import lookup


flask_app = Flask(__name__)
flask_app.register_blueprint(controllers.api.api_routes)
flask_app.register_blueprint(controllers.views.view_routes)

lookup.cache.init_app(flask_app)

settings.load_settings("settings.json")

if __name__ == '__main__':
    flask_app.run(use_debugger=True)
