import logging.config

import uvicorn

from calendar_backend.routes import app

LOGGING_CONFIG = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(user)s %(message)s',
            'default': {'user': ''}
        }
    },
    'handlers': {
        'defaultout': {
            'formatter': 'standard',
            'class': 'logging.StreamHandler',
            'stream': 'ext://sys.stdout',
        },
        'defaulterr': {
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

# logging.basicConfig(
#     filename=f'logger_{__name__}.log',
#     level=logging.DEBUG,
#     format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(user)s %(message)s',
#     datefmt='%Y-%m-%d %H:%M:%S',
# )
logging.config.dictConfig(LOGGING_CONFIG)

if __name__ == "__main__":
    uvicorn.run(app)
