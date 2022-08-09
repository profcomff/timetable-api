import uvicorn

from calendar_backend.routes import app


if __name__ == "__main__":
    uvicorn.run(app)
