from fastapi import FastAPI
from app.api import routes
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)


app.include_router(routes.router)
