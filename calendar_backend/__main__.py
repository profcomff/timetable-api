import logging.config

import uvicorn


from calendar_backend.routes import app

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(user)s %(message)s',
            'defaults': {'user': ''},
            "datefmt":"%d-%m-%Y %I:%M:%S"
        }
    },
    'handlers': {
        'defaultout': {
            'level': 'DEBUG',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'defaulterr': {
            'level': 'ERROR',
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stderr',
        }
    },
    'loggers': {
        '': {  # root logger
            'handlers': ['defaultout', "defaulterr"],
            'propagate': False
        },
        'fastapi': {
            'handlers': ['defaultout', "defaulterr"],
            'propagate': False
        },
        'uvicorn': {  # if __name__ == '__main__'
            'handlers': ['defaultout', "defaulterr"],
            'propagate': False
        },
    }
}

logging.config.dictConfig(LOGGING_CONFIG)

if __name__ == "__main__":
    log = logging.getLogger(__name__)
    log.debug("hello")
    uvicorn.run(app)
