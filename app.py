from flask import Flask
from api import router

def create_app():
    api = Flask(__name__)
    api.register_blueprint(router)
    return api


if __name__ == "__main__":
    app = create_app()
    app.run()