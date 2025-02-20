import os

from flask import Flask
from flask_cors import CORS
from api import router

permitted_origins = os.getenv("PERMITTED_ORIGIN")

def create_app():
    api = Flask(__name__)
    api.register_blueprint(router)

    CORS(api, origins=permitted_origins,
         methods=['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT'],
         # headers=None,
         supports_credentials=False,
         max_age=None,
         send_wildcard=True,
         always_send=True,
         automatic_options=False
         )

    return api


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0")