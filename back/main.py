"""Executar Servidor Flask."""
import os
from decouple import config
from app import start_app

if __name__ == "__main__":
    os.environ["FLASK_APP"] = "app:start_app"
    os.environ["FLASK_SKIP_DOTENV"] = "1"
    os.environ["FLASK_ENV"] = config(
        'FLASK_ENV',
        default='development',
        cast=str
    )
    os.environ["FLASK_DEBUG"] = config(
        'FLASK_DEBUG',
        default='True',
        cast=str
    )
    start_app().run(host="0.0.0.0")
