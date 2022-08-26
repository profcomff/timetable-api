import logging

import uvicorn

from calendar_backend.routes import app

if __name__ == "__main__":
    logger = logging.getLogger(__name__)
    logger.info("hi")
    uvicorn.run(app)
