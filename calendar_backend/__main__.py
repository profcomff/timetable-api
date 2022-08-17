import logging
import uvicorn

from calendar_backend.routes import app

logging.basicConfig(
    filename=f'logger_{__name__}.log',
    level=logging.DEBUG,
    format='%(asctime)s.%(msecs)03d %(levelname)s %(module)s - %(funcName)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

if __name__ == "__main__":
    uvicorn.run(app)
