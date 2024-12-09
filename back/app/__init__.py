"""Modulo Principal do Projeto."""
import logging
import os
from logging.config import dictConfig

from decouple import config
from flask import Flask
from flask_cors import CORS


def start_app() -> Flask:
    """Inicia o App."""
    app = Flask(__name__)
    CORS(app)

    # Log config
    if os.name != 'nt':
        dictConfig({
            'version': 1,
            'formatters': {'default': {
                'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
            }},
            'handlers': {
                'wsgi': {
                    'level': 'INFO',
                    'class': 'logging.StreamHandler',
                    'stream': 'ext://flask.logging.wsgi_errors_stream',
                    'formatter': 'default'
                },
                'file': {
                    'level': 'INFO',
                    'class': 'logging.FileHandler',
                    'formatter': 'default',
                    'filename': '/tmp/gunicorn.error.log'
                }
            },
            'loggers': {
                'file': {
                    'level': 'INFO',
                    'handlers': ['file'],
                    'propagate': 'no'
                }
            },
            'root': {
                'level': 'INFO',
                'handlers': ['wsgi', 'file']
            }
        })
    app.logger.setLevel(logging.INFO)

    app.config.from_object(
        "app.config." + config('FLASK_ENV').capitalize()
    )

    CORS(
        app,
        supports_credentials=True
    )

    @app.errorhandler(404)
    def page_not_found(_):  # pylint: disable=unused-variable
        """Error Page Not Found."""
        return {"status": "rota não encontrada!"}, 404

    @app.errorhandler(500)
    def server_error(_):  # pylint: disable=unused-variable
        """Error Internal Server Error."""
        return {"status": "erro no servidor!"}, 500

    @app.errorhandler(401)
    def unauthorized(_):  # pylint: disable=unused-variable
        """Error unauthorized."""
        return {"status": "erro não autorizado!"}, 401

    @app.errorhandler(403)
    def forbidden(_):  # pylint: disable=unused-variable
        """Error unauthorized."""
        return {"status": "Você não possui permissão para acessar!"}, 403

    from .controllers.bbint import bbint
    app.register_blueprint(bbint)

    from .controllers.bbtsp import bbtsp
    app.register_blueprint(bbtsp)

    from .controllers.bbint_interactive import bbint_interactive
    app.register_blueprint(bbint_interactive)

    return app
