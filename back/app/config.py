"""Arquivo de Configurações."""
import os
from decouple import config


class Config:
    """Classe Base das Configurações."""

    PROJECT_ROOT = os.path.dirname(__file__)
    SECRET_KEY = config("SECRET_KEY")
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024


class Development(Config):
    """Configurações de Desenvolvimento."""

    DEBUG = True


class Production(Config):
    """Configurações de Produção."""

    DEBUG = False
