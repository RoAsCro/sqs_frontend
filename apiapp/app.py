import os

from flask import Flask
from flask_cors import CORS
from api import router
import api

permitted_origins = os.getenv("PERMITTED_ORIGIN") or []

def create_app(mode="error"):
    api.set_logger(mode)
    api_app = Flask(__name__)
    api_app.register_blueprint(router)
    CORS(api_app, origins=permitted_origins,
         methods=['GET', 'HEAD', 'POST', 'OPTIONS', 'PUT'],
         supports_credentials=False,
         max_age=None,
         send_wildcard=True,
         always_send=True,
         automatic_options=False
         )

    return api_app


if __name__ == "__main__":
    app = create_app("debug")
    app.run(host="0.0.0.0")