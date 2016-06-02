import os
basedir = os.path.abspath(os.path.dirname(__file__))

DEBUG = False
LOG_DEBUG = True

SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(basedir, 'app.db')
SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'db_repository')
SQLALCHEMY_TRACK_MODIFICATIONS = False


LOG_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "level": "DEBUG",
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "default",
            "filename": os.path.join(os.path.dirname(__name__), "debug.log"),
            "maxBytes": 1024 * 1024 * 10,
            "backupCount": 1,
        }
    },
    "formatters": {
        "default": {
            "format": "[%(asctime)s] %(levelname)s %(name)s.%(funcName)s:%(lineno)d %(message)s"
        },
    },
    "loggers": {
        "": {
            "handlers": ["file", "console"],
            "level": "DEBUG",
            "propagate": True,
        }
    }
}
